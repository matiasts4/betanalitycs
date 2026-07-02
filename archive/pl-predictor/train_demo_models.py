"""
train_demo_models.py
====================
Entrena modelos de demostración usando únicamente temporadas 1718-2425
como entrenamiento, dejando la temporada 2526 como test set puro.

Estos modelos se usan en la landing page para mostrar predicciones sobre
partidos de test sin incurrir en data leakage.
"""
import os
import json
import sys
import warnings
import pandas as pd
import numpy as np
import joblib

warnings.filterwarnings("ignore")

sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from src.config import FEATURES_PATH, TARGETS, FEATURES, MODELS_DIR
from src.models_neural import PyTorchMLPClassifier

from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, PowerTransformer
from sklearn.impute import KNNImputer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
import xgboost as xgb

DEMO_MODELS_DIR = os.path.join(os.path.dirname(FEATURES_PATH), "..", "..", "models_demo")

SKEWED_FEATURES = ['away_xg', 'referee_avg_cards_history', 'B365H', 'B365D', 'B365A',
                   'h_l5_fls', 'a_l5_fls', 'h_l5_xg', 'a_l5_xg', 'h_l5_xga', 'a_l5_xga']

BEST_MODELS = {
    "1X2 (Match Winner)": "Logistic Regression (Elastic Net)",
    "Double Chance 1X (Home or Draw)": "Logistic Regression (Elastic Net)",
    "Double Chance X2 (Away or Draw)": "Logistic Regression (Elastic Net)",
    "Over 2.5 Goals": "XGBoost (L1/L2 Regularized)",
    "Under 2.5 Goals": "XGBoost (L1/L2 Regularized)",
    "BTTS (Both Teams To Score)": "Logistic Regression (Elastic Net)",
    "BTTS - No": "Neural Network (Dropout)",
    "Home Clean Sheet": "Neural Network (Dropout)",
}

USE_TOMEK = {"1X2 (Match Winner)", "Home Clean Sheet"}


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
    skewed_in = [f for f in SKEWED_FEATURES if f in FEATURES]
    standard_in = [f for f in FEATURES if f not in skewed_in]

    preprocessor = ColumnTransformer(
        transformers=[
            ('skewed', Pipeline([
                ('imputer', KNNImputer(n_neighbors=5, weights='distance')),
                ('yeo_johnson', PowerTransformer(method='yeo-johnson', standardize=True))
            ]), skewed_in),
            ('standard', Pipeline([
                ('imputer', KNNImputer(n_neighbors=5, weights='distance')),
                ('scaler', StandardScaler())
            ]), standard_in),
        ],
        remainder='passthrough'
    )

    if use_tomek:
        from imblearn.pipeline import Pipeline as ImbPipeline
        from imblearn.under_sampling import TomekLinks
        return ImbPipeline([
            ('preprocessor', preprocessor),
            ('sampler', TomekLinks()),
            ('classifier', classifier)
        ])

    return Pipeline([
        ('preprocessor', preprocessor),
        ('classifier', classifier)
    ])


def instantiate_classifier(model_name, params):
    clean_params = {}
    for k, v in params.items():
        if k in ['n_estimators', 'max_depth', 'min_samples_split', 'min_samples_leaf',
                 'max_iter', 'epochs', 'batch_size', 'hidden_dim']:
            clean_params[k] = int(v) if v is not None else None
        else:
            clean_params[k] = v

    if model_name == "Logistic Regression (Elastic Net)":
        return LogisticRegression(penalty='elasticnet', solver='saga', max_iter=5000,
                                  random_state=42, **clean_params)
    if model_name == "Random Forest":
        return RandomForestClassifier(random_state=42, n_jobs=-1, **clean_params)
    if model_name == "HistGradientBoosting (Early Stopping)":
        return HistGradientBoostingClassifier(early_stopping=True, validation_fraction=0.1,
                                              n_iter_no_change=10, random_state=42, **clean_params)
    if model_name == "XGBoost (L1/L2 Regularized)":
        return xgb.XGBClassifier(eval_metric='logloss', random_state=42, **clean_params)
    if model_name == "Neural Network (Dropout)":
        return PyTorchMLPClassifier(input_dim=len(FEATURES), random_state=42, **clean_params)
    raise ValueError(f"Modelo desconocido: {model_name}")


def main():
    json_path = os.path.join(MODELS_DIR, "optimized_hyperparams.json")
    if not os.path.exists(json_path):
        print(f"[Error] No se encontró {json_path}")
        return

    with open(json_path, 'r', encoding='utf-8') as f:
        optimized_data = json.load(f)

    df = pd.read_csv(FEATURES_PATH)
    df = df[df['game_id'].astype(str) != '0'].reset_index(drop=True)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date').reset_index(drop=True)
    df = prepare_targets(df)

    # Test set: temporada 2526 (última temporada completa del dataset)
    train_df = df[df['season'] != 2526].copy()
    test_df = df[df['season'] == 2526].copy()

    print(f"Partidos entrenamiento: {len(train_df)}")
    print(f"Partidos test (demo): {len(test_df)}")

    os.makedirs(DEMO_MODELS_DIR, exist_ok=True)

    X_train = train_df[FEATURES]

    for target_name, target_col in TARGETS.items():
        model_name = BEST_MODELS[target_name]
        use_tomek = target_name in USE_TOMEK

        params = optimized_data[target_name][model_name]["best_params"]
        clf = instantiate_classifier(model_name, params)
        pipe = create_pipeline(clf, use_tomek=use_tomek)

        y_train = train_df[target_col]
        pipe.fit(X_train, y_train)

        safe_name = target_name.replace(" ", "_").replace("(", "").replace(")", "").replace(".", "_")
        model_path = os.path.join(DEMO_MODELS_DIR, f"model_{safe_name}.pkl")
        joblib.dump(pipe, model_path)
        print(f"[OK] {target_name} -> {model_name} guardado en {model_path}")

    print(f"\nTodos los modelos demo guardados en: {DEMO_MODELS_DIR}")


if __name__ == "__main__":
    main()
