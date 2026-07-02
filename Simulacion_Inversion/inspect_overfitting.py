import pandas as pd
import numpy as np
import os
import sys
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import accuracy_score
import xgboost as xgb
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression

# Configurar rutas para importar desde archive/pl-predictor
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'archive', 'pl-predictor')))
from src.config import FEATURES, TARGETS
from evaluar_comparativa_completa import create_pipeline, prepare_targets

def inspect_fit_market(df, X, target_col, model_factory, model_name):
    y = df[target_col]
    tscv = TimeSeriesSplit(n_splits=5)
    
    train_accs = []
    test_accs = []
    
    for train_idx, test_idx in tscv.split(X):
        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
        
        # Crear pipeline y ajustar
        clf = model_factory()
        pipe = create_pipeline(clf, use_tomek=False)
        pipe.fit(X_train, y_train)
        
        # Predicciones
        train_preds = pipe.predict(X_train)
        test_preds = pipe.predict(X_test)
        
        train_accs.append(accuracy_score(y_train, train_preds))
        test_accs.append(accuracy_score(y_test, test_preds))
        
    return np.mean(train_accs), np.mean(test_accs)

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(current_dir, "historical_with_ou_odds.csv")
    df = pd.read_csv(csv_path)
    df = df[df['game_id'].astype(str) != '0'].reset_index(drop=True)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date').reset_index(drop=True)
    df = prepare_targets(df)
    
    X = df[FEATURES]
    
    # ─────────────────────────────────────────────────────────────────────────
    # 1. MERCADO 1X2 (Match Winner)
    # ─────────────────────────────────────────────────────────────────────────
    print("ANALIZANDO AJUSTE (FIT) EN MERCADO 1X2:")
    print("=======================================")
    
    configs_1x2 = [
        ("LogReg Optimizada (C=0.06)", lambda: LogisticRegression(penalty='elasticnet', solver='saga', l1_ratio=0.99, C=0.06, random_state=42, max_iter=2000)),
        ("LogReg Sin Regularizar (C=100)", lambda: LogisticRegression(penalty='elasticnet', solver='saga', l1_ratio=0.5, C=100.0, random_state=42, max_iter=2000)),
        ("HGB Complejo (Depth=10, LR=0.1)", lambda: HistGradientBoostingClassifier(learning_rate=0.1, max_depth=10, max_iter=200, random_state=42)),
        ("HGB Optimo (Depth=3, LR=0.018)", lambda: HistGradientBoostingClassifier(learning_rate=0.0187, max_depth=3, l2_regularization=7.36, max_iter=150, random_state=42))
    ]
    
    for label, factory in configs_1x2:
        train_acc, test_acc = inspect_fit_market(df, X, 'target_1x2', factory, label)
        gap = train_acc - test_acc
        print(f"{label:<35} | Train Acc={train_acc:.2%} | Test Acc={test_acc:.2%} | Brecha (Gap)={gap:.2%}")
        
    # ─────────────────────────────────────────────────────────────────────────
    # 2. MERCADO OVER 2.5 GOALS
    # ─────────────────────────────────────────────────────────────────────────
    print("\nANALIZANDO AJUSTE (FIT) EN MERCADO OVER 2.5 GOALS:")
    print("==================================================")
    
    configs_over = [
        ("XGBoost Optimo (Depth=2, Trees=136)", lambda: xgb.XGBClassifier(learning_rate=0.0043, n_estimators=136, max_depth=2, reg_lambda=0.0771, reg_alpha=0.0152, random_state=42, eval_metric='logloss')),
        ("XGBoost Complejo (Depth=6, Trees=500)", lambda: xgb.XGBClassifier(learning_rate=0.05, n_estimators=500, max_depth=6, random_state=42, eval_metric='logloss')),
        ("XGBoost Simple Stump (Depth=1, Trees=50)", lambda: xgb.XGBClassifier(learning_rate=0.01, n_estimators=50, max_depth=1, random_state=42, eval_metric='logloss'))
    ]
    
    for label, factory in configs_over:
        train_acc, test_acc = inspect_fit_market(df, X, 'target_over_2_5_goals', factory, label)
        gap = train_acc - test_acc
        print(f"{label:<35} | Train Acc={train_acc:.2%} | Test Acc={test_acc:.2%} | Brecha (Gap)={gap:.2%}")

if __name__ == "__main__":
    main()
