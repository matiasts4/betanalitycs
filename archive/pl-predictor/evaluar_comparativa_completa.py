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

def evaluate_pipeline(pipe, X, y, tscv, is_multiclass):
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
            accs.append(0.0)
            f1s.append(0.0)
            aucs.append(0.0)
            
    return np.mean(accs), np.mean(f1s), np.mean(aucs)

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
    
    records = []
    
    print("\n==================================================")
    print("CALCULANDO COMPARATIVA COMPLETA BASELINE VS OPTUNA")
    print("==================================================")
    
    for target_name, target_col in TARGETS.items():
        y = df[target_col]
        is_multiclass = len(np.unique(y)) > 2
        use_tomek = target_name in ["1X2 (Match Winner)", "Home Clean Sheet"]
        
        print(f"\nProcesando Mercado: {target_name}")
        if use_tomek:
            print("   -> Aplicando Tomek Links para los modelos optimizados...")
        
        for model_name in models_list:
            # 1. Evaluar Baseline
            print(f"  -> Evaluando Baseline de {model_name}...")
            base_clf = get_baseline_classifier(model_name, target_name)
            base_pipe = create_pipeline(base_clf, use_tomek=use_tomek) # Baseline usa Tomek en los 2 mercados para consistencia
            base_acc, base_f1, base_auc = evaluate_pipeline(base_pipe, X, y, tscv, is_multiclass)
            
            # 2. Evaluar Optimizado
            print(f"  -> Evaluando Optimizado de {model_name}...")
            opt_info = optimized_data[target_name][model_name]
            opt_params = opt_info["best_params"]
            opt_clf = instantiate_classifier(model_name, opt_params)
            opt_pipe = create_pipeline(opt_clf, use_tomek=use_tomek) # Optimizado usa Tomek en los 2 mercados
            opt_acc, opt_f1, opt_auc = evaluate_pipeline(opt_pipe, X, y, tscv, is_multiclass)
            
            records.append({
                "target_name": target_name,
                "model_name": model_name,
                "accuracy_baseline": base_acc,
                "accuracy_optuna": opt_acc,
                "f1_baseline": base_f1,
                "f1_optuna": opt_f1,
                "auc_baseline": base_auc,
                "auc_optuna": opt_auc
            })
            
    csv_path = os.path.join(MODELS_DIR, "baseline_vs_optimized_metrics.csv")
    pd.DataFrame(records).to_csv(csv_path, index=False)
    print(f"\n[OK] Métricas cruzadas guardadas en: {csv_path}")

if __name__ == "__main__":
    main()
