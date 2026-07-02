# Modelos Finales de Producción: Especificación y Métricas de Rendimiento

Este documento detalla la especificación técnica de los mejores modelos entrenados para cada mercado en **BetAnalytics**, incluyendo sus hiperparámetros óptimos sintonizados por **Optuna** (TPE Bayesiano) y sus métricas de validación cruzada temporal (`TimeSeriesSplit` de 5 splits).

---

## 📊 Tabla General de Modelos y Métricas

| Mercado | Modelo Ganador | Preprocesamiento / Resampling | Parámetros Óptimos (Optuna) | Accuracy (CV) | F1-Score (CV) | ROC-AUC (CV) |
| :--- | :--- | :---: | :--- | :---: | :---: | :---: |
| **1X2 (Match Winner)** | Logistic Regression (Elastic Net) | Tomek Links (RUS) | `C: 0.0602`, `l1_ratio: 0.9993` | 0.5284 | 0.4703 | N/A |
| **BTTS (Both Teams To Score)** | HistGradientBoosting (Early Stopping) | Sin remuestreo | `learning_rate: 0.0011`, `max_iter: 295`, `max_depth: 5`, `l2_regularization: 0.5581` | 0.5461 | 0.6365 | 0.5222 |
| **BTTS - No** | Neural Network (Dropout) | Sin remuestreo | `hidden_dim: 64`, `dropout_rate: 0.1735`, `lr: 0.0319`, `epochs: 100`, `batch_size: 128` | 0.5394 | 0.3612 | 0.5127 |
| **Double Chance 1X (Home or Draw)** | Logistic Regression (Elastic Net) | Sin remuestreo | `C: 0.0967`, `l1_ratio: 0.7308` | 0.7082 | 0.8063 | 0.7147 |
| **Double Chance X2 (Away or Draw)** | Logistic Regression (Elastic Net) | Sin remuestreo | `C: 0.0166`, `l1_ratio: 0.6036` | 0.6535 | 0.7062 | 0.7118 |
| **Home Clean Sheet** | Neural Network (Dropout) | Tomek Links (RUS) | `hidden_dim: 32`, `dropout_rate: 0.3010`, `lr: 0.0466`, `epochs: 50`, `batch_size: 32` | 0.7099 | 0.0635 | 0.5274 |
| **Over 2.5 Goals** | XGBoost (L1/L2 Regularized) | Sin remuestreo | `learning_rate: 0.0043`, `n_estimators: 136`, `max_depth: 2`, `reg_lambda: 0.0771`, `reg_alpha: 0.0152` | 0.5702 | 0.6810 | 0.5523 |
| **Under 2.5 Goals** | XGBoost (L1/L2 Regularized) | Sin remuestreo | `learning_rate: 0.0033`, `n_estimators: 194`, `max_depth: 2`, `reg_lambda: 0.0011`, `reg_alpha: 0.0313` | 0.5734 | 0.3192 | 0.5528 |

---

## 📝 Notas de Interpretación de las Métricas
1. **N/A en ROC-AUC (1X2):** El mercado 1X2 es un problema de clasificación multiclase (3 clases: Local, Empate, Visitante). La métrica ROC-AUC estándar de scikit-learn se calcula para clasificaciones binarias, por lo que para el 1X2 no se reporta en esta tabla.
2. **F1-Score en Home Clean Sheet:** El F1-score bajo ($0.0635$) en la valla invicta local se debe al fuerte desbalanceo de la clase (la valla invicta ocurre en un porcentaje muy menor de partidos). Sin embargo, el modelo prioriza maximizar la exactitud global ($70.99\%$) reduciendo el ruido de la clase minoritaria mediante Tomek Links.
3. **Resampling Híbrido:** Aplicamos submuestreo por **Tomek Links** únicamente en los mercados de alta incertidumbre o ruido de frontera: **1X2** y **Home Clean Sheet**. El resto de los mercados se benefician de entrenar directamente sobre el desequilibrio natural de la Premier League sin remuestreo.
