import pandas as pd
import numpy as np
import os
import sys
import json
import warnings
from sklearn.model_selection import TimeSeriesSplit, RandomizedSearchCV
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

def create_pipeline(classifier):
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
    
    return Pipeline([
        ('preprocessor', preprocessor),
        ('classifier', classifier)
    ])

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
    pipe = create_pipeline(clf)
    scores = []
    for train_idx, test_idx in tscv.split(X):
        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
        
        try:
            pipe.fit(X_train, y_train)
            preds = pipe.predict(X_test)
            scores.append(accuracy_score(y_test, preds))
        except Exception as e:
            scores.append(0.0)
    return np.mean(scores)

def main():
    print("Iniciando búsqueda de hiperparámetros optimizados para todos los modelos y mercados...")
    
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
    
    # Definir los espacios de búsqueda
    param_grids = {
        "Logistic Regression (Elastic Net)": {
            'classifier__C': [0.01, 0.05, 0.1, 0.5, 1.0, 5.0],
            'classifier__l1_ratio': [0.1, 0.3, 0.5, 0.7, 0.9],
        },
        "Random Forest": {
            'classifier__n_estimators': [100, 200, 300, 500],
            'classifier__max_depth': [5, 8, 12, 16, 20, None],
            'classifier__min_samples_split': [2, 5, 10, 15],
            'classifier__min_samples_leaf': [2, 4, 8, 12],
        },
        "HistGradientBoosting (Early Stopping)": {
            'classifier__learning_rate': [0.005, 0.01, 0.03, 0.05, 0.1],
            'classifier__max_iter': [50, 100, 150, 200, 300],
            'classifier__max_depth': [3, 5, 8, 10],
            'classifier__l2_regularization': [0.0, 0.1, 1.0, 5.0, 10.0],
        },
        "XGBoost (L1/L2 Regularized)": {
            'classifier__learning_rate': [0.01, 0.03, 0.05, 0.1],
            'classifier__n_estimators': [100, 150, 200, 300],
            'classifier__max_depth': [3, 4, 5, 6, 8],
            'classifier__reg_lambda': [0.1, 1.0, 3.0, 5.0, 10.0],
            'classifier__reg_alpha': [0.0, 0.1, 0.5, 1.0],
        },
        "Neural Network (Dropout)": {
            'classifier__hidden_dim': [32, 64, 128],
            'classifier__dropout_rate': [0.1, 0.2, 0.3, 0.4],
            'classifier__lr': [0.001, 0.005, 0.01, 0.02],
            'classifier__epochs': [50, 80, 100],
            'classifier__batch_size': [32, 64, 128],
        }
    }
    
    optimized_params = {}
    tuning_reports = []
    
    for target_name, target_col in TARGETS.items():
        print(f"\n==================================================")
        print(f"SINTONIZANDO TARGET: {target_name.upper()}")
        print(f"==================================================")
        
        y = df[target_col]
        optimized_params[target_name] = {}
        
        for model_name, grid in param_grids.items():
            print(f"  > Optimizando {model_name}...")
            
            # 1. Obtener score de la línea base
            baseline_score = evaluate_baseline_score(X, y, tscv, model_name, target_name)
            print(f"    Línea Base CV Accuracy: {baseline_score:.4f}")
            
            # 2. Inicializar clasificador y pipeline para la búsqueda
            if model_name == "Logistic Regression (Elastic Net)":
                clf = LogisticRegression(penalty='elasticnet', solver='saga', max_iter=5000, random_state=42)
                n_jobs = -1
                n_iter = 10
            elif model_name == "Random Forest":
                clf = RandomForestClassifier(random_state=42, n_jobs=-1)
                n_jobs = -1
                n_iter = 10
            elif model_name == "HistGradientBoosting (Early Stopping)":
                clf = HistGradientBoostingClassifier(early_stopping=True, validation_fraction=0.1, n_iter_no_change=10, random_state=42)
                n_jobs = -1
                n_iter = 10
            elif model_name == "XGBoost (L1/L2 Regularized)":
                clf = xgb.XGBClassifier(eval_metric='logloss', random_state=42)
                n_jobs = -1
                n_iter = 10
            elif model_name == "Neural Network (Dropout)":
                clf = PyTorchMLPClassifier(input_dim=len(FEATURES), random_state=42)
                # Ejecutar secuencialmente para evitar fallos de multiprocesamiento en PyTorch
                n_jobs = 1
                # Menos iteraciones para redes neuronales por velocidad
                n_iter = 5
                
            pipe = create_pipeline(clf)
            
            # 3. Ejecutar búsqueda aleatoria
            search = RandomizedSearchCV(
                estimator=pipe,
                param_distributions=grid,
                n_iter=n_iter,
                scoring='accuracy',
                cv=tscv,
                n_jobs=n_jobs,
                random_state=42,
                error_score=0.0
            )
            
            try:
                search.fit(X, y)
                best_score = search.best_score_
                # Extraer parámetros limpios sin el prefijo "classifier__"
                best_params = {k.replace('classifier__', ''): v for k, v in search.best_params_.items()}
                
                print(f"    Mejor CV Accuracy: {best_score:.4f}")
                print(f"    Parámetros óptimos: {best_params}")
                
                # Determinar si mejoró
                improved = best_score > baseline_score
                improvement_diff = best_score - baseline_score
                
                optimized_params[target_name][model_name] = {
                    "best_params": best_params,
                    "baseline_score": baseline_score,
                    "best_score": best_score,
                    "improved": improved
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
                
            except Exception as e:
                print(f"    ⚠️ Error durante la optimización de {model_name}: {e}")
                optimized_params[target_name][model_name] = {
                    "best_params": {},
                    "baseline_score": baseline_score,
                    "best_score": baseline_score,
                    "improved": False
                }
    
    # Guardar parámetros optimizados a JSON
    os.makedirs(os.path.join(MODELS_DIR), exist_ok=True)
    json_path = os.path.join(MODELS_DIR, "optimized_hyperparams.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(optimized_params, f, indent=4, ensure_ascii=False)
        
    print(f"\n==================================================")
    print(f"RESULTADOS CONSOLIDADOS DE LA OPTIMIZACIÓN")
    print(f"==================================================")
    report_df = pd.DataFrame(tuning_reports)
    print(report_df.to_string(index=False))
    
    csv_path = os.path.join(MODELS_DIR, "tuning_comparison_results.csv")
    report_df.to_csv(csv_path, index=False)
    print(f"\n✅ Resultados guardados en JSON: {json_path}")
    print(f"✅ Resultados guardados en CSV: {csv_path}")

if __name__ == "__main__":
    main()
