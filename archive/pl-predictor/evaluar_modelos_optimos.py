import pandas as pd
import numpy as np
import os
import sys
import json
import warnings
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score
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
    tscv = TimeSeriesSplit(n_splits=5)
    
    models_list = [
        "Logistic Regression (Elastic Net)",
        "Random Forest",
        "HistGradientBoosting (Early Stopping)",
        "XGBoost (L1/L2 Regularized)",
        "Neural Network (Dropout)"
    ]
    
    optimized_metrics = []
    
    print("\n==================================================")
    print("EVALUANDO MODELOS CON PARÁMETROS OPTUNA (5-SPLITS)")
    print("==================================================")
    
    for target_name, target_col in TARGETS.items():
        y = df[target_col]
        is_multiclass = len(np.unique(y)) > 2
        use_tomek = target_name in ["1X2 (Match Winner)", "Home Clean Sheet"]
        
        print(f"\nTarget: {target_name}")
        if use_tomek:
            print("   -> Aplicando Tomek Links en CV...")
        
        for model_name in models_list:
            info = optimized_data[target_name][model_name]
            params = info["best_params"]
            
            clf = instantiate_classifier(model_name, params)
            pipe = create_pipeline(clf, use_tomek=use_tomek)
            
            accs = []
            f1s = []
            aucs = []
            
            for train_idx, test_idx in tscv.split(X):
                X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
                y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
                
                try:
                    pipe.fit(X_train, y_train)
                    preds = pipe.predict(X_test)
                    
                    accs.append(accuracy_score(y_test, preds))
                    
                    if not is_multiclass:
                        f1s.append(f1_score(y_test, preds, zero_division=0))
                        try:
                            probs = pipe.predict_proba(X_test)[:, 1]
                            aucs.append(roc_auc_score(y_test, probs))
                        except Exception:
                            aucs.append(0.0)
                    else:
                        f1s.append(f1_score(y_test, preds, average='weighted', zero_division=0))
                        aucs.append(0.0)
                except Exception as e:
                    print(f"    ⚠️ Error evaluando {model_name} en split: {e}")
                    accs.append(0.0)
                    f1s.append(0.0)
                    aucs.append(0.0)
                    
            avg_acc = np.mean(accs)
            avg_f1 = np.mean(f1s)
            avg_auc = np.mean(aucs)
            
            print(f"   -> {model_name:<38} | Acc: {avg_acc:.4f} | F1: {avg_f1:.4f} | AUC: {avg_auc:.4f}")
            
            optimized_metrics.append({
                "target_name": target_name,
                "model_name": model_name,
                "accuracy": avg_acc,
                "f1_score": avg_f1,
                "roc_auc": avg_auc
            })
            
    csv_path = os.path.join(MODELS_DIR, "optimized_models_comparison_results.csv")
    pd.DataFrame(optimized_metrics).to_csv(csv_path, index=False)
    print(f"\n[OK] Evaluación completada. Resultados guardados en: {csv_path}")

if __name__ == "__main__":
    main()
