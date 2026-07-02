import pandas as pd
import numpy as np
import os
import sys
import warnings
import joblib
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import accuracy_score, roc_auc_score, f1_score
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
import xgboost as xgb

# Import pipeline elements from imblearn
from imblearn.pipeline import Pipeline as ImbPipeline
from imblearn.over_sampling import RandomOverSampler, SMOTE
from imblearn.under_sampling import RandomUnderSampler, TomekLinks, ClusterCentroids, NearMiss

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, PowerTransformer
from sklearn.impute import KNNImputer

# Asegurar que el directorio base esté en el path para importar src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.config import FEATURES_PATH, TARGETS, FEATURES, MODELS_DIR
from src.models_neural import PyTorchMLPClassifier

warnings.filterwarnings("ignore")

def prepare_targets(df):
    """Calcula los targets a partir de las columnas base para que los modelos sean ciegos al resultado original."""
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

def create_pipeline(classifier, sampler=None):
    skewed_features = ['away_xg', 'referee_avg_cards_history', 'B365H', 'B365D', 'B365A', 'h_l5_fls', 'a_l5_fls', 'h_l5_xg', 'a_l5_xg', 'h_l5_xga', 'a_l5_xga']
    skewed_in_features = [f for f in skewed_features if f in FEATURES]
    standard_in_features = [f for f in FEATURES if f not in skewed_in_features]
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('skewed', ImbPipeline([
                ('imputer', KNNImputer(n_neighbors=5, weights='distance')),
                ('yeo_johnson', PowerTransformer(method='yeo-johnson', standardize=True))
            ]), skewed_in_features),
            ('standard', ImbPipeline([
                ('imputer', KNNImputer(n_neighbors=5, weights='distance')),
                ('scaler', StandardScaler())
            ]), standard_in_features)
        ],
        remainder='passthrough'
    )
    
    steps = [('preprocessor', preprocessor)]
    if sampler is not None:
        steps.append(('sampler', sampler))
    steps.append(('classifier', classifier))
    
    return ImbPipeline(steps)

def get_base_classifiers(target_name):
    # Definir clasificadores exactamente igual que en train_models.py
    if '1X2' in target_name:
        rf = RandomForestClassifier(n_estimators=500, max_depth=9, min_samples_split=10, random_state=42, n_jobs=-1)
        hgb = HistGradientBoostingClassifier(learning_rate=0.0187, max_depth=3, l2_regularization=7.36, max_iter=150, random_state=42)
    elif target_name == 'Double Chance 1X (Home or Draw)':
        rf = RandomForestClassifier(n_estimators=200, max_depth=20, min_samples_split=8, random_state=42, n_jobs=-1)
        hgb = HistGradientBoostingClassifier(learning_rate=0.03, max_iter=200, max_depth=5, random_state=42)
    elif target_name == 'Double Chance X2 (Away or Draw)':
        rf = RandomForestClassifier(n_estimators=200, max_depth=16, min_samples_split=10, random_state=42, n_jobs=-1)
        hgb = HistGradientBoostingClassifier(learning_rate=0.041, max_depth=10, l2_regularization=4.82, max_iter=100, random_state=42)
    elif 'Over' in target_name:
        rf = RandomForestClassifier(n_estimators=100, max_depth=5, min_samples_split=3, random_state=42, n_jobs=-1)
        hgb = HistGradientBoostingClassifier(learning_rate=0.0102, max_depth=3, l2_regularization=0.05, max_iter=50, random_state=42)
    elif 'Under' in target_name:
        rf = RandomForestClassifier(n_estimators=500, max_depth=8, min_samples_split=2, random_state=42, n_jobs=-1)
        hgb = HistGradientBoostingClassifier(learning_rate=0.01, max_depth=3, max_iter=50, random_state=42)
    elif target_name == 'BTTS (Both Teams To Score)':
        rf = RandomForestClassifier(n_estimators=200, max_depth=7, min_samples_split=7, random_state=42, n_jobs=-1)
        hgb = HistGradientBoostingClassifier(learning_rate=0.0106, max_depth=4, l2_regularization=9.98, max_iter=50, random_state=42)
    elif target_name == 'BTTS - No':
        rf = RandomForestClassifier(n_estimators=100, max_depth=5, min_samples_split=6, random_state=42, n_jobs=-1)
        hgb = HistGradientBoostingClassifier(learning_rate=0.01, max_depth=3, max_iter=50, random_state=42)
    elif target_name == 'Home Clean Sheet':
        rf = RandomForestClassifier(n_estimators=300, max_depth=16, min_samples_split=5, random_state=42, n_jobs=-1)
        hgb = HistGradientBoostingClassifier(learning_rate=0.014, max_depth=4, l2_regularization=2.27, max_iter=100, random_state=42)
    else:
        rf = RandomForestClassifier(n_estimators=150, max_depth=6, min_samples_split=10, random_state=42, n_jobs=-1)
        hgb = HistGradientBoostingClassifier(learning_rate=0.03, max_iter=200, max_depth=5, l2_regularization=5.0, random_state=42)
        
    hgb.set_params(early_stopping=True, validation_fraction=0.1, n_iter_no_change=10)
    rf.set_params(min_samples_leaf=4)
    
    return {
        "Logistic Regression (Elastic Net)": LogisticRegression(penalty='elasticnet', solver='saga', l1_ratio=0.5, C=0.1, max_iter=5000, random_state=42),
        "Random Forest": rf,
        "HistGradientBoosting (Early Stopping)": hgb,
        "XGBoost (L1/L2 Regularized)": xgb.XGBClassifier(eval_metric='logloss', random_state=42, max_depth=4, learning_rate=0.05, n_estimators=150, reg_lambda=3.0, reg_alpha=0.5),
        "Neural Network (Dropout)": PyTorchMLPClassifier(input_dim=len(FEATURES), hidden_dim=64, dropout_rate=0.3, lr=0.01, epochs=80, batch_size=64, random_state=42)
    }

def main():
    print("Iniciando entrenamiento espejo de modelos con técnicas de balanceo...")
    if not os.path.exists(FEATURES_PATH):
        print(f"❌ Error: No se encontró el dataset {FEATURES_PATH}")
        return
        
    df = pd.read_csv(FEATURES_PATH)
    df = df[df['game_id'].astype(str) != '0'].reset_index(drop=True)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date').reset_index(drop=True)
    df = prepare_targets(df)
    
    X = df[FEATURES]
    
    # Definir los remuestreadores (Samplers)
    samplers = {
        "main": None,
        "oversampling_random": RandomOverSampler(random_state=42),
        "oversampling_smote": SMOTE(random_state=42),
        "undersampling_random": RandomUnderSampler(random_state=42),
        "undersampling_tomek": TomekLinks(),
        "undersampling_centroids": ClusterCentroids(random_state=42),
        "undersampling_nearmiss": NearMiss()
    }
    
    # Dataframe para almacenar las métricas comparativas
    all_metrics = []
    
    tscv = TimeSeriesSplit(n_splits=5)
    
    for config_name, sampler in samplers.items():
        print(f"\n==================================================")
        print(f"PROCESANDO CONFIGURACIÓN ESPEJO: {config_name.upper()}")
        print(f"==================================================")
        
        # Crear subdirectorio para los modelos guardados de esta configuración espejo
        config_dir = os.path.join(MODELS_DIR, "mirrors", config_name)
        os.makedirs(config_dir, exist_ok=True)
        
        for target_name, target_col in TARGETS.items():
            if target_col not in df.columns:
                print(f"  ❌ Error: Target {target_col} no encontrado en datos. Saltando...")
                continue
                
            y = df[target_col]
            is_multiclass = len(np.unique(y)) > 2
            
            # Obtener clasificadores base limpios
            base_classifiers = get_base_classifiers(target_name)
            
            # Construir pipelines con el sampler correspondiente
            models = {}
            for name, clf in base_classifiers.items():
                models[name] = create_pipeline(clf, sampler)
                
            print(f"  Evaluando target: {target_name}...")
            
            results = {name: {'acc': [], 'auc': [], 'f1': []} for name in models.keys()}
            
            for name, model in models.items():
                for train_idx, test_idx in tscv.split(X):
                    X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
                    y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
                    
                    try:
                        model.fit(X_train, y_train)
                        preds = model.predict(X_test)
                        
                        acc = accuracy_score(y_test, preds)
                        results[name]['acc'].append(acc)
                        
                        if not is_multiclass:
                            results[name]['f1'].append(f1_score(y_test, preds, zero_division=0))
                            try:
                                probs = model.predict_proba(X_test)[:, 1]
                                results[name]['auc'].append(roc_auc_score(y_test, probs))
                            except:
                                results[name]['auc'].append(0)
                        else:
                            results[name]['f1'].append(f1_score(y_test, preds, average='weighted', zero_division=0))
                            results[name]['auc'].append(0)
                    except Exception as e:
                        print(f"    ⚠️ Error entrenando {name} en fold: {e}")
                        results[name]['acc'].append(0)
                        results[name]['f1'].append(0)
                        results[name]['auc'].append(0)
                        
            # Registrar métricas promedio y buscar el mejor modelo
            best_name = None
            best_acc = -1
            
            for name in models.keys():
                avg_acc = np.mean(results[name]['acc'])
                avg_auc = np.mean(results[name]['auc'])
                avg_f1 = np.mean(results[name]['f1'])
                
                all_metrics.append({
                    "mirror_config": config_name,
                    "target_name": target_name,
                    "model_name": name,
                    "accuracy": avg_acc,
                    "roc_auc": avg_auc,
                    "f1_score": avg_f1
                })
                
                if avg_acc > best_acc:
                    best_acc = avg_acc
                    best_name = name
                    
            print(f"    👉 Mejor Modelo: {best_name} (Acc: {best_acc:.4f})")
            
            # Entrenar el mejor modelo de este target/config con toda la data
            best_model = models[best_name]
            try:
                best_model.fit(X, y)
                safe_name = target_name.replace(" ", "_").replace("(", "").replace(")", "").replace(".", "_")
                model_path = os.path.join(config_dir, f"model_{safe_name}.pkl")
                joblib.dump(best_model, model_path)
            except Exception as e:
                print(f"    ❌ Error al guardar el modelo final: {e}")
                
    # Guardar métricas completas en un CSV comparativo
    results_path = os.path.join(MODELS_DIR, "mirrors", "mirror_comparison_results.csv")
    metrics_df = pd.DataFrame(all_metrics)
    metrics_df.to_csv(results_path, index=False)
    print(f"\n✅ Entrenamiento de espejos completado con éxito!")
    print(f"✅ Resultados consolidados guardados en: {results_path}")

if __name__ == "__main__":
    main()
