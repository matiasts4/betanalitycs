import pandas as pd
import numpy as np
import os
import sys
import json
import warnings
import optuna
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import accuracy_score
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
optuna.logging.set_verbosity(optuna.logging.WARNING)

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

def get_baseline_classifier(model_name, target_name):
    if model_name == "Logistic Regression (Elastic Net)":
        return LogisticRegression(penalty='elasticnet', solver='saga', l1_ratio=0.5, C=0.1, max_iter=5000, random_state=42)
    elif model_name == "Random Forest":
        if '1X2' in target_name:
            rf = RandomForestClassifier(n_estimators=500, max_depth=9, min_samples_split=10, random_state=42, n_jobs=-1)
        elif target_name == "Double Chance 1X (Home or Draw)":
            rf = RandomForestClassifier(n_estimators=200, max_depth=20, min_samples_split=8, random_state=42, n_jobs=-1)
        elif target_name == "Double Chance X2 (Away or Draw)":
            rf = RandomForestClassifier(n_estimators=200, max_depth=16, min_samples_split=10, random_state=42, n_jobs=-1)
        elif 'Over' in target_name:
            rf = RandomForestClassifier(n_estimators=100, max_depth=5, min_samples_split=3, random_state=42, n_jobs=-1)
        elif 'Under' in target_name:
            rf = RandomForestClassifier(n_estimators=500, max_depth=8, min_samples_split=2, random_state=42, n_jobs=-1)
        elif target_name == "BTTS (Both Teams To Score)":
            rf = RandomForestClassifier(n_estimators=200, max_depth=7, min_samples_split=7, random_state=42, n_jobs=-1)
        elif target_name == "BTTS - No":
            rf = RandomForestClassifier(n_estimators=100, max_depth=5, min_samples_split=6, random_state=42, n_jobs=-1)
        elif target_name == "Home Clean Sheet":
            rf = RandomForestClassifier(n_estimators=300, max_depth=16, min_samples_split=5, random_state=42, n_jobs=-1)
        else:
            rf = RandomForestClassifier(n_estimators=150, max_depth=6, min_samples_split=10, random_state=42, n_jobs=-1)
        rf.set_params(min_samples_leaf=4)
        return rf
    elif model_name == "HistGradientBoosting (Early Stopping)":
        if '1X2' in target_name:
            hgb = HistGradientBoostingClassifier(learning_rate=0.0187, max_depth=3, l2_regularization=7.36, max_iter=150, random_state=42)
        elif target_name == "Double Chance 1X (Home or Draw)":
            hgb = HistGradientBoostingClassifier(learning_rate=0.03, max_iter=200, max_depth=5, random_state=42)
        elif target_name == "Double Chance X2 (Away or Draw)":
            hgb = HistGradientBoostingClassifier(learning_rate=0.041, max_depth=10, l2_regularization=4.82, max_iter=100, random_state=42)
        elif 'Over' in target_name:
            hgb = HistGradientBoostingClassifier(learning_rate=0.0102, max_depth=3, l2_regularization=0.05, max_iter=50, random_state=42)
        elif 'Under' in target_name:
            hgb = HistGradientBoostingClassifier(learning_rate=0.01, max_depth=3, max_iter=50, random_state=42)
        elif target_name == "BTTS (Both Teams To Score)":
            hgb = HistGradientBoostingClassifier(learning_rate=0.0106, max_depth=4, l2_regularization=9.98, max_iter=50, random_state=42)
        elif target_name == "BTTS - No":
            hgb = HistGradientBoostingClassifier(learning_rate=0.01, max_depth=3, max_iter=50, random_state=42)
        elif target_name == "Home Clean Sheet":
            hgb = HistGradientBoostingClassifier(learning_rate=0.014, max_depth=4, l2_regularization=2.27, max_iter=100, random_state=42)
        else:
            hgb = HistGradientBoostingClassifier(learning_rate=0.03, max_iter=200, max_depth=5, l2_regularization=5.0, random_state=42)
        hgb.set_params(early_stopping=True, validation_fraction=0.1, n_iter_no_change=10)
        return hgb
    elif model_name == "XGBoost (L1/L2 Regularized)":
        return xgb.XGBClassifier(eval_metric='logloss', random_state=42, max_depth=4, learning_rate=0.05, n_estimators=150, reg_lambda=3.0, reg_alpha=0.5)
    elif model_name == "Neural Network (Dropout)":
        return PyTorchMLPClassifier(input_dim=len(FEATURES), hidden_dim=64, dropout_rate=0.3, lr=0.01, epochs=80, batch_size=64, random_state=42)

def evaluate_baseline_score(X, y, tscv, model_name, target_name):
    clf = get_baseline_classifier(model_name, target_name)
    use_tomek = target_name in ["1X2 (Match Winner)", "Home Clean Sheet"]
    pipe = create_pipeline(clf, use_tomek=use_tomek)
    scores = []
    for train_idx, test_idx in tscv.split(X):
        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
        try:
            pipe.fit(X_train, y_train)
            preds = pipe.predict(X_test)
            scores.append(accuracy_score(y_test, preds))
        except Exception:
            scores.append(0.0)
    return float(np.mean(scores))

def make_json_serializable(obj):
    if isinstance(obj, dict):
        return {k: make_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [make_json_serializable(v) for v in obj]
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, bool):
        return bool(obj)
    elif isinstance(obj, (int, float, str)):
        return obj
    else:
        return str(obj)

def main():
    print("Iniciando optimización avanzada de hiperparámetros con OPTUNA...")
    
    if not os.path.exists(FEATURES_PATH):
        print(f"❌ Error: No se encontró el dataset {FEATURES_PATH}")
        return
        
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
    
    json_path = os.path.join(MODELS_DIR, "optimized_hyperparams.json")
    if os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            optimized_params = json.load(f)
    else:
        optimized_params = {}
        
    tuning_reports = []
    
    target_keys = ["1X2 (Match Winner)", "Home Clean Sheet"]
    for target_name in target_keys:
        if target_name not in TARGETS:
            continue
        target_col = TARGETS[target_name]
        
        print(f"\n==================================================")
        print(f"SINTONIZANDO TARGET CON OPTUNA: {target_name.upper()}")
        print(f"==================================================")
        
        y = df[target_col]
        optimized_params[target_name] = {}
        
        use_tomek = target_name in ["1X2 (Match Winner)", "Home Clean Sheet"]
        for model_name in models_list:
            print(f"  > Optimizando {model_name}...")
            
            # 1. Evaluar línea base
            baseline_score = evaluate_baseline_score(X, y, tscv, model_name, target_name)
            print(f"    Línea Base CV Accuracy: {baseline_score:.4f}")
            
            # 2. Definir objetivo de Optuna
            def objective(trial):
                if model_name == "Logistic Regression (Elastic Net)":
                    C = trial.suggest_float('C', 0.001, 10.0, log=True)
                    l1_ratio = trial.suggest_float('l1_ratio', 0.0, 1.0)
                    clf = LogisticRegression(penalty='elasticnet', solver='saga', C=C, l1_ratio=l1_ratio, max_iter=5000, random_state=42)
                elif model_name == "Random Forest":
                    n_estimators = trial.suggest_int('n_estimators', 50, 500)
                    max_depth = trial.suggest_int('max_depth', 3, 20)
                    min_samples_split = trial.suggest_int('min_samples_split', 2, 20)
                    min_samples_leaf = trial.suggest_int('min_samples_leaf', 2, 20)
                    clf = RandomForestClassifier(n_estimators=n_estimators, max_depth=max_depth,
                                                 min_samples_split=min_samples_split, min_samples_leaf=min_samples_leaf,
                                                 random_state=42, n_jobs=-1)
                elif model_name == "HistGradientBoosting (Early Stopping)":
                    learning_rate = trial.suggest_float('learning_rate', 0.001, 0.2, log=True)
                    max_iter = trial.suggest_int('max_iter', 50, 300)
                    max_depth = trial.suggest_int('max_depth', 2, 10)
                    l2_regularization = trial.suggest_float('l2_regularization', 1e-5, 10.0, log=True)
                    clf = HistGradientBoostingClassifier(learning_rate=learning_rate, max_iter=max_iter, max_depth=max_depth,
                                                         l2_regularization=l2_regularization, early_stopping=True,
                                                         validation_fraction=0.1, n_iter_no_change=10, random_state=42)
                elif model_name == "XGBoost (L1/L2 Regularized)":
                    learning_rate = trial.suggest_float('learning_rate', 0.001, 0.2, log=True)
                    n_estimators = trial.suggest_int('n_estimators', 50, 300)
                    max_depth = trial.suggest_int('max_depth', 2, 8)
                    reg_lambda = trial.suggest_float('reg_lambda', 1e-3, 10.0, log=True)
                    reg_alpha = trial.suggest_float('reg_alpha', 1e-3, 10.0, log=True)
                    clf = xgb.XGBClassifier(learning_rate=learning_rate, n_estimators=n_estimators, max_depth=max_depth,
                                            reg_lambda=reg_lambda, reg_alpha=reg_alpha, eval_metric='logloss', random_state=42)
                elif model_name == "Neural Network (Dropout)":
                    hidden_dim = trial.suggest_categorical('hidden_dim', [32, 64, 128])
                    dropout_rate = trial.suggest_float('dropout_rate', 0.1, 0.5)
                    lr = trial.suggest_float('lr', 0.001, 0.05, log=True)
                    epochs = trial.suggest_categorical('epochs', [50, 80, 100])
                    batch_size = trial.suggest_categorical('batch_size', [32, 64, 128])
                    clf = PyTorchMLPClassifier(input_dim=len(FEATURES), hidden_dim=hidden_dim, dropout_rate=dropout_rate,
                                               lr=lr, epochs=epochs, batch_size=batch_size, random_state=42)
                
                pipe = create_pipeline(clf, use_tomek=use_tomek)
                scores = []
                for train_idx, test_idx in tscv.split(X):
                    X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
                    y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
                    try:
                        pipe.fit(X_train, y_train)
                        preds = pipe.predict(X_test)
                        scores.append(accuracy_score(y_test, preds))
                    except Exception:
                        scores.append(0.0)
                return np.mean(scores)
            
            # 3. Determinar número de ensayos
            n_trials = 8 if model_name == "Neural Network (Dropout)" else 15
            
            study = optuna.create_study(direction="maximize")
            study.optimize(objective, n_trials=n_trials)
            
            best_score = float(study.best_value)
            best_params = study.best_params
            
            print(f"    Mejor CV Accuracy (Optuna): {best_score:.4f}")
            print(f"    Parámetros óptimos: {best_params}")
            
            improved = best_score > baseline_score
            improvement_diff = best_score - baseline_score
            
            optimized_params[target_name][model_name] = {
                "best_params": best_params,
                "baseline_score": baseline_score,
                "best_score": best_score,
                "improved": bool(improved)
            }
            
            tuning_reports.append({
                "Mercado": target_name,
                "Modelo": model_name,
                "Línea Base": baseline_score,
                "Optimizado": best_score,
                "Mejora": improvement_diff,
                "¿Mejoró?": "SÍ" if improved else "NO",
                "Hiperparámetros": str(best_params)
            })
            
    # Guardar parámetros optimizados a JSON
    os.makedirs(os.path.join(MODELS_DIR), exist_ok=True)
    json_path = os.path.join(MODELS_DIR, "optimized_hyperparams.json")
    
    # Hacer serializable a JSON de forma segura
    clean_params = make_json_serializable(optimized_params)
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(clean_params, f, indent=4, ensure_ascii=False)
        
    print(f"\n==================================================")
    print(f"RESULTADOS CONSOLIDADOS DE LA OPTIMIZACIÓN (OPTUNA)")
    print(f"==================================================")
    report_df = pd.DataFrame(tuning_reports)
    print(report_df.to_string(index=False))
    
    csv_path = os.path.join(MODELS_DIR, "tuning_comparison_results.csv")
    report_df.to_csv(csv_path, index=False)
    print(f"\n[OK] Resultados guardados en JSON: {json_path}")
    print(f"[OK] Resultados guardados en CSV: {csv_path}")

if __name__ == "__main__":
    main()
