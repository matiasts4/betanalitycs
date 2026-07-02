import pandas as pd
import numpy as np
import os
import sys
import json
import warnings
import joblib
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
import xgboost as xgb

from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, PowerTransformer
from sklearn.impute import KNNImputer

# Asegurar que el directorio base esté en el path para importar src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.config import FEATURES_PATH, TARGETS, FEATURES, MODELS_DIR
from src.models_neural import PyTorchMLPClassifier

warnings.filterwarnings("ignore")

def prepare_targets(df):
    df_out = df.copy()
    df_out['target_1x2'] = df_out['result_1x2'].astype(int)
    df_out['target_dc_1X'] = (df_out['result_1x2'] >= 1).astype(int)
    df_out['target_dc_X2'] = (df_out['result_1x2'] <= 1).astype(int)
    df_out['target_over_2_5_goals'] = (df_out['total_goals'] > 2.5).astype(int)
    df_out['target_under_2_5_goals'] = (df_out['total_goals'] <= 2.5).astype(int)
    df_out['target_btts'] = df_out['btts'].astype(int)
    df_out['target_btts_no'] = (df_out['btts'] == 0).astype(int)
    df_out['target_home_clean_sheet'] = (df_out['away_goals'] == 0).astype(int)
    return df_out

def create_pipeline(classifier, use_tomek=False):
    skewed_features = ['away_xg', 'referee_avg_cards_history', 'B365H', 'B365D', 'B365A', 'h_l5_fls', 'a_l5_fls', 'h_l5_xg', 'a_l5_xg', 'h_l5_xga', 'a_l5_xga']
    skewed_in_features = [f for f in skewed_features if f in FEATURES]
    standard_in_features = [f for f in FEATURES if f not in skewed_in_features]
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('skewed', Pipeline([
                ('imputer', KNNImputer(n_neighbors=5, weights='distance')),
                ('yeo_johnson', PowerTransformer(method='yeo-johnson', standardize=True))
            ]), skewed_in_features),
            ('standard', Pipeline([
                ('imputer', KNNImputer(n_neighbors=5, weights='distance')),
                ('scaler', StandardScaler())
            ]), standard_in_features)
        ],
        remainder='passthrough'
    )
    
    from imblearn.pipeline import Pipeline as ImbPipeline
    from imblearn.under_sampling import TomekLinks
    
    steps = [('preprocessor', preprocessor)]
    if use_tomek:
        steps.append(('sampler', TomekLinks()))
    steps.append(('classifier', classifier))
    
    return ImbPipeline(steps)

def instantiate_classifier(model_name, params):
    # Asegurarnos de que los tipos de los hiperparámetros son correctos
    clean_params = {}
    for k, v in params.items():
        if k in ['n_estimators', 'max_depth', 'min_samples_split', 'min_samples_leaf', 'max_iter', 'epochs', 'batch_size', 'hidden_dim']:
            clean_params[k] = int(v) if v is not None else None
        else:
            clean_params[k] = v

    if model_name == "Logistic Regression (Elastic Net)":
        return LogisticRegression(penalty='elasticnet', solver='saga', max_iter=5000, random_state=42, **clean_params)
    elif model_name == "Random Forest":
        return RandomForestClassifier(random_state=42, n_jobs=-1, **clean_params)
    elif model_name == "HistGradientBoosting (Early Stopping)":
        return HistGradientBoostingClassifier(early_stopping=True, validation_fraction=0.1, n_iter_no_change=10, random_state=42, **clean_params)
    elif model_name == "XGBoost (L1/L2 Regularized)":
        return xgb.XGBClassifier(eval_metric='logloss', random_state=42, **clean_params)
    elif model_name == "Neural Network (Dropout)":
        return PyTorchMLPClassifier(input_dim=len(FEATURES), random_state=42, **clean_params)
    else:
        raise ValueError(f"Modelo desconocido: {model_name}")

def main():
    json_path = os.path.join(MODELS_DIR, "optimized_hyperparams.json")
    if not os.path.exists(json_path):
        print(f"[Error] No se encontró el archivo de hiperparámetros optimizados {json_path}")
        return
        
    if not os.path.exists(FEATURES_PATH):
        print(f"[Error] No se encontró el dataset {FEATURES_PATH}")
        return
        
    with open(json_path, 'r', encoding='utf-8') as f:
        optimized_data = json.load(f)
        
    df = pd.read_csv(FEATURES_PATH)
    df = df[df['game_id'].astype(str) != '0'].reset_index(drop=True)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date').reset_index(drop=True)
    df = prepare_targets(df)
    
    X = df[FEATURES]
    
    print("\n==================================================")
    print("ENTRENANDO MODELOS FINALES CON PARÁMETROS OPTUNA")
    print("==================================================")
    
    for target_name, target_col in TARGETS.items():
        if target_col not in df.columns:
            print(f"[Error] Target {target_col} no encontrado en datos. Saltando...")
            continue
            
        y = df[target_col]
        
        # Encontrar el mejor modelo según best_score
        target_models = optimized_data[target_name]
        best_model_name = None
        best_score = -1
        best_params = None
        
        for model_name, info in target_models.items():
            if info["best_score"] > best_score:
                best_score = info["best_score"]
                best_model_name = model_name
                best_params = info["best_params"]
                
        print(f"\nMercado: {target_name}")
        print(f"   -> Mejor Modelo: {best_model_name}")
        print(f"   -> Accuracy CV Optimizado: {best_score:.4f}")
        print(f"   -> Hiperparámetros: {best_params}")
        
        # Instanciar y construir el pipeline completo
        clf = instantiate_classifier(best_model_name, best_params)
        use_tomek = target_name in ["1X2 (Match Winner)", "Home Clean Sheet"]
        if use_tomek:
            print("   -> Aplicando submuestreo de Tomek Links para balanceo de fronteras...")
        pipe = create_pipeline(clf, use_tomek=use_tomek)
        
        # Entrenar con toda la data
        print("   -> Entrenando modelo final...")
        pipe.fit(X, y)
        
        # Guardar en pickle
        safe_name = target_name.replace(" ", "_").replace("(", "").replace(")", "").replace(".", "_")
        model_path = os.path.join(MODELS_DIR, f"model_{safe_name}.pkl")
        joblib.dump(pipe, model_path)
        print(f"   -> Guardado con éxito en: {model_path}")
        
    print("\n[OK] ¡Entrenamiento de todos los modelos de producción completado con éxito!")

if __name__ == "__main__":
    main()
