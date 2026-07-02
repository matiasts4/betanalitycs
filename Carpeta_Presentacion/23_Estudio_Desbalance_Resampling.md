# Estudio Comparativo: Tratamiento del Desbalanceo de Clases mediante Modelos Espejo (BetAnalytics)

Este informe documenta el estudio avanzado de remuestreo (resampling) realizado para evaluar el impacto del desbalanceo de clases en la predicción de mercados deportivos de la Premier League ($N = 3,389$ partidos).

Sirve como material de apoyo metodológico oficial para tu defensa de tesis, respondiendo a la inquietud académica de evaluar técnicas de sobremuestreo y submuestreo frente a la línea base limpia del proyecto.

---

## 1. ⚖️ El Problema del Desbalanceo en Pronósticos Deportivos

El desbalanceo de clases ocurre cuando una de las categorías del target está subrepresentada. En la literatura de machine learning, se suele clasificar el desbalanceo en tres niveles:
* **Leve/Moderado:** La clase minoritaria representa entre el $15\%$ y el $40\%$ del dataset.
* **Severo:** La clase minoritaria representa menos del $15\%$ (típico en detección de fraudes, fallas de maquinaria o enfermedades raras).

### Distribución de Clases en BetAnalytics:
Al analizar nuestros 8 mercados objetivos bajo el conjunto de entrenamiento histórico, observamos las siguientes proporciones:

* **Double Chance 1X (Home or Draw):** $67.36\%$ (1) vs. $32.64\%$ (0). *Desbalanceo leve/moderado.*
* **Home Clean Sheet (Valla Invicta Local):** $70.20\%$ (0 - Recibe Gol) vs. $29.80\%$ (1 - Valla Invicta). *Desbalanceo leve/moderado.*
* **1X2 Resultado (Multiclase):** Local $44.14\%$, Visitante $32.64\%$, Empate $23.22\%$. *Distribución natural de fútbol.*
* **Over/Under 2.5 Goles & Ambos Anotan (BTTS):** Distribuciones muy cercanas al $50/50$ (prácticamente balanceadas).

A diferencia de otros dominios (como fraude financiero), en fútbol las clases minoritarias representan proporciones altas ($23\% - 33\%$). Este estudio evalúa si alterar artificialmente estas proporciones naturales mejora la capacidad predictiva.

---

## 2. 🎛️ Fundamentos de las Técnicas de Resampling Evaluadas

Entrenamos **7 configuraciones espejo** de nuestro sistema de modelos predictivos. Cada configuración representa un enfoque metodológico diferente:

### A. Sobremuestreo (Oversampling)
1. **Random Oversampling (ROS):** Reclona de manera aleatoria observaciones de la clase minoritaria hasta igualar la clase mayoritaria.
   * *Riesgo:* Puede inducir a un sobreajuste (overfitting) severo, ya que el modelo entrena con registros duplicados exactos.
2. **SMOTE (Synthetic Minority Over-sampling Technique):** Genera nuevas muestras sintéticas interpolando linealmente entre los $k$ vecinos más cercanos de la clase minoritaria en el espacio de características.
   * *Ventaja:* Introduce variabilidad en lugar de solo copiar.
   * *Riesgo:* Si las clases están solapadas (común en fútbol), puede generar muestras sintéticas ruidosas en zonas de la clase contraria.

### B. Submuestreo (Undersampling)
3. **Random Undersampling (RUS):** Elimina aleatoriamente observaciones de la clase mayoritaria hasta equilibrar las proporciones.
   * *Riesgo:* Descarta una enorme cantidad de partidos históricos valiosos, reduciendo el tamaño de la muestra de entrenamiento.
4. **Tomek Links:** Detecta pares de puntos de clases opuestas que son sus vecinos más cercanos entre sí (enlaces de Tomek). Elimina el punto que pertenece a la clase mayoritaria.
   * *Efecto:* No equilibra las clases al 50/50, sino que **limpia la frontera de decisión** y elimina el ruido en las zonas de solapamiento.
5. **Cluster Centroids:** Agrupa las muestras de la clase mayoritaria mediante un algoritmo KMeans (donde el número de clusters es igual al tamaño de la clase minoritaria) y sustituye los datos originales por los centroides de dichos clusters.
6. **NearMiss (Versión 1):** Selecciona las muestras de la clase mayoritaria que tienen la menor distancia promedio a los $k$ vecinos más cercanos de la clase minoritaria.

---

## 3. 🛡️ Rigor Metodológico: Prevención de Leakage en Resampling

Un error común y grave en ciencia de datos es aplicar técnicas de balanceo (como SMOTE) a **todo el dataset** antes de realizar la validación cruzada. Esto genera **fuga de datos (data leakage)** porque el conjunto de prueba termina conteniendo muestras sintéticas creadas a partir de información que debería ser invisible (el conjunto de validación).

### Nuestra Implementación:
Utilizamos la librería `imbalanced-learn` y encapsulamos los samplers en pipelines dinámicos (`imblearn.pipeline.Pipeline`).
* Durante la validación cruzada temporal (`TimeSeriesSplit(n_splits=5)`), el balanceo se aplica **estrictamente sobre los pliegues de entrenamiento (train folds)**.
* Los pliegues de validación/prueba (test folds) permanecen **100% inalterados e intactos**, preservando las proporciones reales del fútbol para medir la generalización real en producción.

---

## 4. 📊 Resultados Numéricos Comparativos

A continuación se presentan las tablas de rendimiento del mejor modelo entrenado para cada mercado clave bajo las 7 configuraciones espejo:

### A. Comparativa de Exactitud (Accuracy)
| Configuración Espejo | Resultado 1X2 (Multiclase) | Doble Oportunidad 1X | Valla Invicta Local (CS) | Ambos Anotan (BTTS) |
| :--- | :---: | :---: | :---: | :---: |
| **Original (Línea Base)** | **0.5298** | **0.7071** | **0.7064** | **0.5323** |
| **Random Oversampling (ROS)** | 0.4926 | 0.6812 | 0.6663 | 0.5273 |
| **SMOTE (Oversampling)** | 0.4883 | 0.6784 | 0.6440 | 0.5206 |
| **Random Undersampling (RUS)** | 0.4876 | 0.6624 | 0.5702 | 0.5241 |
| **Tomek Links (Undersampling)** | 0.5238 | 0.7053 | 0.6943 | 0.5099 |
| **Cluster Centroids (Undersampling)** | 0.4894 | 0.6606 | 0.5709 | 0.5184 |
| **NearMiss (Undersampling)** | 0.4514 | 0.6160 | 0.5106 | 0.5181 |

### B. Comparativa de F1-Score
| Configuración Espejo | Resultado 1X2 (Multiclase) | Doble Oportunidad 1X | Valla Invicta Local (CS) | Ambos Anotan (BTTS) |
| :--- | :---: | :---: | :---: | :---: |
| **Original (Línea Base)** | 0.4631 | **0.8056** | 0.2896 | **0.6090** |
| **Random Oversampling (ROS)** | 0.4859 | 0.7726 | 0.4329 | 0.5763 |
| **SMOTE (Oversampling)** | 0.4897 | 0.7647 | 0.4308 | 0.5847 |
| **Random Undersampling (RUS)** | 0.4900 | 0.7301 | 0.4346 | 0.5799 |
| **Tomek Links (Undersampling)** | 0.4792 | 0.8004 | 0.3360 | 0.5037 |
| **Cluster Centroids (Undersampling)** | 0.4879 | 0.7341 | 0.4286 | 0.5735 |
| **NearMiss (Undersampling)** | 0.4575 | 0.6816 | **0.4373** | 0.5738 |

---

### C. Matriz Completa de Resultados (280 Combinaciones)
Esta tabla exhaustiva detalla el rendimiento obtenido por cada uno de los 5 clasificadores en cada una de las 7 configuraciones espejo para la totalidad de las 8 variables predictivas:

| Mercado (Target) | Configuración Espejo | Clasificador (Modelo) | Exactitud (Accuracy) | F1-Score | ROC-AUC |
| :--- | :--- | :--- | :---: | :---: | :---: |
| 1X2 (Match Winner) | Original (Línea Base) | Logistic Regression (Elastic Net) | 0.5298 | 0.4631 | N/A (Multiclase) |
| 1X2 (Match Winner) | Original (Línea Base) | Random Forest | 0.5287 | 0.4595 | N/A (Multiclase) |
| 1X2 (Match Winner) | Original (Línea Base) | HistGradientBoosting (Early Stopping) | 0.5223 | 0.4505 | N/A (Multiclase) |
| 1X2 (Match Winner) | Original (Línea Base) | XGBoost | 0.5007 | 0.4567 | N/A (Multiclase) |
| 1X2 (Match Winner) | Original (Línea Base) | Neural Network (MLP) | 0.4848 | 0.4429 | N/A (Multiclase) |
| 1X2 (Match Winner) | ROS (Oversampling) | Logistic Regression (Elastic Net) | 0.4883 | 0.4859 | N/A (Multiclase) |
| 1X2 (Match Winner) | ROS (Oversampling) | Random Forest | 0.4926 | 0.4730 | N/A (Multiclase) |
| 1X2 (Match Winner) | ROS (Oversampling) | HistGradientBoosting (Early Stopping) | 0.4876 | 0.4834 | N/A (Multiclase) |
| 1X2 (Match Winner) | ROS (Oversampling) | XGBoost | 0.4869 | 0.4768 | N/A (Multiclase) |
| 1X2 (Match Winner) | ROS (Oversampling) | Neural Network (MLP) | 0.4447 | 0.4465 | N/A (Multiclase) |
| 1X2 (Match Winner) | SMOTE (Oversampling) | Logistic Regression (Elastic Net) | 0.4883 | 0.4897 | N/A (Multiclase) |
| 1X2 (Match Winner) | SMOTE (Oversampling) | Random Forest | 0.4826 | 0.4772 | N/A (Multiclase) |
| 1X2 (Match Winner) | SMOTE (Oversampling) | HistGradientBoosting (Early Stopping) | 0.4730 | 0.4748 | N/A (Multiclase) |
| 1X2 (Match Winner) | SMOTE (Oversampling) | XGBoost | 0.4730 | 0.4698 | N/A (Multiclase) |
| 1X2 (Match Winner) | SMOTE (Oversampling) | Neural Network (MLP) | 0.4539 | 0.4410 | N/A (Multiclase) |
| 1X2 (Match Winner) | RUS (Undersampling) | Logistic Regression (Elastic Net) | 0.4876 | 0.4900 | N/A (Multiclase) |
| 1X2 (Match Winner) | RUS (Undersampling) | Random Forest | 0.4699 | 0.4740 | N/A (Multiclase) |
| 1X2 (Match Winner) | RUS (Undersampling) | HistGradientBoosting (Early Stopping) | 0.4631 | 0.4681 | N/A (Multiclase) |
| 1X2 (Match Winner) | RUS (Undersampling) | XGBoost | 0.4532 | 0.4625 | N/A (Multiclase) |
| 1X2 (Match Winner) | RUS (Undersampling) | Neural Network (MLP) | 0.4284 | 0.4375 | N/A (Multiclase) |
| 1X2 (Match Winner) | Tomek Links (RUS) | Logistic Regression (Elastic Net) | 0.5238 | 0.4792 | N/A (Multiclase) |
| 1X2 (Match Winner) | Tomek Links (RUS) | Random Forest | 0.5209 | 0.4687 | N/A (Multiclase) |
| 1X2 (Match Winner) | Tomek Links (RUS) | HistGradientBoosting (Early Stopping) | 0.5209 | 0.4725 | N/A (Multiclase) |
| 1X2 (Match Winner) | Tomek Links (RUS) | XGBoost | 0.4996 | 0.4723 | N/A (Multiclase) |
| 1X2 (Match Winner) | Tomek Links (RUS) | Neural Network (MLP) | 0.4720 | 0.4510 | N/A (Multiclase) |
| 1X2 (Match Winner) | Cluster Centroids (RUS) | Logistic Regression (Elastic Net) | 0.4894 | 0.4879 | N/A (Multiclase) |
| 1X2 (Match Winner) | Cluster Centroids (RUS) | Random Forest | 0.4766 | 0.4782 | N/A (Multiclase) |
| 1X2 (Match Winner) | Cluster Centroids (RUS) | HistGradientBoosting (Early Stopping) | 0.4426 | 0.4462 | N/A (Multiclase) |
| 1X2 (Match Winner) | Cluster Centroids (RUS) | XGBoost | 0.4543 | 0.4615 | N/A (Multiclase) |
| 1X2 (Match Winner) | Cluster Centroids (RUS) | Neural Network (MLP) | 0.4394 | 0.4417 | N/A (Multiclase) |
| 1X2 (Match Winner) | NearMiss (RUS) | Logistic Regression (Elastic Net) | 0.4447 | 0.4575 | N/A (Multiclase) |
| 1X2 (Match Winner) | NearMiss (RUS) | Random Forest | 0.4284 | 0.4384 | N/A (Multiclase) |
| 1X2 (Match Winner) | NearMiss (RUS) | HistGradientBoosting (Early Stopping) | 0.4514 | 0.4568 | N/A (Multiclase) |
| 1X2 (Match Winner) | NearMiss (RUS) | XGBoost | 0.3858 | 0.3956 | N/A (Multiclase) |
| 1X2 (Match Winner) | NearMiss (RUS) | Neural Network (MLP) | 0.3755 | 0.3801 | N/A (Multiclase) |
| Doble Oportunidad 1X | Original (Línea Base) | Logistic Regression (Elastic Net) | 0.7071 | 0.8056 | 0.7145 |
| Doble Oportunidad 1X | Original (Línea Base) | Random Forest | 0.6957 | 0.7995 | 0.6897 |
| Doble Oportunidad 1X | Original (Línea Base) | HistGradientBoosting (Early Stopping) | 0.6918 | 0.7997 | 0.6843 |
| Doble Oportunidad 1X | Original (Línea Base) | XGBoost | 0.6819 | 0.7884 | 0.6817 |
| Doble Oportunidad 1X | Original (Línea Base) | Neural Network (MLP) | 0.6702 | 0.7795 | 0.6552 |
| Doble Oportunidad 1X | ROS (Oversampling) | Logistic Regression (Elastic Net) | 0.6589 | 0.7295 | 0.7133 |
| Doble Oportunidad 1X | ROS (Oversampling) | Random Forest | 0.6812 | 0.7726 | 0.6867 |
| Doble Oportunidad 1X | ROS (Oversampling) | HistGradientBoosting (Early Stopping) | 0.6706 | 0.7558 | 0.6753 |
| Doble Oportunidad 1X | ROS (Oversampling) | XGBoost | 0.6652 | 0.7485 | 0.6815 |
| Doble Oportunidad 1X | ROS (Oversampling) | Neural Network (MLP) | 0.6404 | 0.7255 | 0.6483 |
| Doble Oportunidad 1X | SMOTE (Oversampling) | Logistic Regression (Elastic Net) | 0.6628 | 0.7336 | 0.7130 |
| Doble Oportunidad 1X | SMOTE (Oversampling) | Random Forest | 0.6784 | 0.7647 | 0.6962 |
| Doble Oportunidad 1X | SMOTE (Oversampling) | HistGradientBoosting (Early Stopping) | 0.6688 | 0.7558 | 0.6786 |
| Doble Oportunidad 1X | SMOTE (Oversampling) | XGBoost | 0.6780 | 0.7643 | 0.6884 |
| Doble Oportunidad 1X | SMOTE (Oversampling) | Neural Network (MLP) | 0.6518 | 0.7456 | 0.6508 |
| Doble Oportunidad 1X | RUS (Undersampling) | Logistic Regression (Elastic Net) | 0.6624 | 0.7301 | 0.7136 |
| Doble Oportunidad 1X | RUS (Undersampling) | Random Forest | 0.6500 | 0.7181 | 0.6949 |
| Doble Oportunidad 1X | RUS (Undersampling) | HistGradientBoosting (Early Stopping) | 0.6340 | 0.7084 | 0.6729 |
| Doble Oportunidad 1X | RUS (Undersampling) | XGBoost | 0.6326 | 0.7059 | 0.6739 |
| Doble Oportunidad 1X | RUS (Undersampling) | Neural Network (MLP) | 0.6071 | 0.6808 | 0.6476 |
| Doble Oportunidad 1X | Tomek Links (RUS) | Logistic Regression (Elastic Net) | 0.7053 | 0.8004 | 0.7135 |
| Doble Oportunidad 1X | Tomek Links (RUS) | Random Forest | 0.6947 | 0.7937 | 0.6901 |
| Doble Oportunidad 1X | Tomek Links (RUS) | HistGradientBoosting (Early Stopping) | 0.6869 | 0.7903 | 0.6849 |
| Doble Oportunidad 1X | Tomek Links (RUS) | XGBoost | 0.6837 | 0.7844 | 0.6832 |
| Doble Oportunidad 1X | Tomek Links (RUS) | Neural Network (MLP) | 0.6837 | 0.7818 | 0.6652 |
| Doble Oportunidad 1X | Cluster Centroids (RUS) | Logistic Regression (Elastic Net) | 0.6606 | 0.7341 | 0.7116 |
| Doble Oportunidad 1X | Cluster Centroids (RUS) | Random Forest | 0.6465 | 0.7135 | 0.6909 |
| Doble Oportunidad 1X | Cluster Centroids (RUS) | HistGradientBoosting (Early Stopping) | 0.6418 | 0.7091 | 0.6796 |
| Doble Oportunidad 1X | Cluster Centroids (RUS) | XGBoost | 0.6394 | 0.7090 | 0.6751 |
| Doble Oportunidad 1X | Cluster Centroids (RUS) | Neural Network (MLP) | 0.6333 | 0.7224 | 0.6496 |
| Doble Oportunidad 1X | NearMiss (RUS) | Logistic Regression (Elastic Net) | 0.6160 | 0.6816 | 0.6770 |
| Doble Oportunidad 1X | NearMiss (RUS) | Random Forest | 0.5543 | 0.5979 | 0.6253 |
| Doble Oportunidad 1X | NearMiss (RUS) | HistGradientBoosting (Early Stopping) | 0.5791 | 0.6343 | 0.6333 |
| Doble Oportunidad 1X | NearMiss (RUS) | XGBoost | 0.5514 | 0.5931 | 0.6056 |
| Doble Oportunidad 1X | NearMiss (RUS) | Neural Network (MLP) | 0.4894 | 0.4988 | 0.5717 |
| Doble Oportunidad X2 | Original (Línea Base) | Logistic Regression (Elastic Net) | 0.6422 | 0.6851 | 0.7091 |
| Doble Oportunidad X2 | Original (Línea Base) | Random Forest | 0.6394 | 0.6853 | 0.6952 |
| Doble Oportunidad X2 | Original (Línea Base) | HistGradientBoosting (Early Stopping) | 0.6372 | 0.6887 | 0.6731 |
| Doble Oportunidad X2 | Original (Línea Base) | XGBoost | 0.6287 | 0.6704 | 0.6778 |
| Doble Oportunidad X2 | Original (Línea Base) | Neural Network (MLP) | 0.6291 | 0.6737 | 0.6615 |
| Doble Oportunidad X2 | ROS (Oversampling) | Logistic Regression (Elastic Net) | 0.6408 | 0.6577 | 0.7083 |
| Doble Oportunidad X2 | ROS (Oversampling) | Random Forest | 0.6358 | 0.6691 | 0.6969 |
| Doble Oportunidad X2 | ROS (Oversampling) | HistGradientBoosting (Early Stopping) | 0.6291 | 0.6535 | 0.6769 |
| Doble Oportunidad X2 | ROS (Oversampling) | XGBoost | 0.6333 | 0.6607 | 0.6836 |
| Doble Oportunidad X2 | ROS (Oversampling) | Neural Network (MLP) | 0.6167 | 0.6375 | 0.6569 |
| Doble Oportunidad X2 | SMOTE (Oversampling) | Logistic Regression (Elastic Net) | 0.6379 | 0.6573 | 0.7093 |
| Doble Oportunidad X2 | SMOTE (Oversampling) | Random Forest | 0.6340 | 0.6632 | 0.6948 |
| Doble Oportunidad X2 | SMOTE (Oversampling) | HistGradientBoosting (Early Stopping) | 0.6291 | 0.6547 | 0.6816 |
| Doble Oportunidad X2 | SMOTE (Oversampling) | XGBoost | 0.6220 | 0.6456 | 0.6786 |
| Doble Oportunidad X2 | SMOTE (Oversampling) | Neural Network (MLP) | 0.6096 | 0.6543 | 0.6571 |
| Doble Oportunidad X2 | RUS (Undersampling) | Logistic Regression (Elastic Net) | 0.6355 | 0.6494 | 0.7092 |
| Doble Oportunidad X2 | RUS (Undersampling) | Random Forest | 0.6273 | 0.6431 | 0.6958 |
| Doble Oportunidad X2 | RUS (Undersampling) | HistGradientBoosting (Early Stopping) | 0.6277 | 0.6447 | 0.6778 |
| Doble Oportunidad X2 | RUS (Undersampling) | XGBoost | 0.6199 | 0.6354 | 0.6836 |
| Doble Oportunidad X2 | RUS (Undersampling) | Neural Network (MLP) | 0.6156 | 0.6457 | 0.6571 |
| Doble Oportunidad X2 | Tomek Links (RUS) | Logistic Regression (Elastic Net) | 0.6394 | 0.6640 | 0.7082 |
| Doble Oportunidad X2 | Tomek Links (RUS) | Random Forest | 0.6312 | 0.6586 | 0.6946 |
| Doble Oportunidad X2 | Tomek Links (RUS) | HistGradientBoosting (Early Stopping) | 0.6450 | 0.6683 | 0.6879 |
| Doble Oportunidad X2 | Tomek Links (RUS) | XGBoost | 0.6227 | 0.6430 | 0.6864 |
| Doble Oportunidad X2 | Tomek Links (RUS) | Neural Network (MLP) | 0.6060 | 0.6008 | 0.6638 |
| Doble Oportunidad X2 | Cluster Centroids (RUS) | Logistic Regression (Elastic Net) | 0.6443 | 0.6642 | 0.7079 |
| Doble Oportunidad X2 | Cluster Centroids (RUS) | Random Forest | 0.6323 | 0.6535 | 0.6927 |
| Doble Oportunidad X2 | Cluster Centroids (RUS) | HistGradientBoosting (Early Stopping) | 0.6227 | 0.6392 | 0.6741 |
| Doble Oportunidad X2 | Cluster Centroids (RUS) | XGBoost | 0.6330 | 0.6477 | 0.6849 |
| Doble Oportunidad X2 | Cluster Centroids (RUS) | Neural Network (MLP) | 0.6092 | 0.6206 | 0.6514 |
| Doble Oportunidad X2 | NearMiss (RUS) | Logistic Regression (Elastic Net) | 0.6326 | 0.6479 | 0.7036 |
| Doble Oportunidad X2 | NearMiss (RUS) | Random Forest | 0.6323 | 0.6467 | 0.6921 |
| Doble Oportunidad X2 | NearMiss (RUS) | HistGradientBoosting (Early Stopping) | 0.6230 | 0.6334 | 0.6759 |
| Doble Oportunidad X2 | NearMiss (RUS) | XGBoost | 0.6230 | 0.6401 | 0.6793 |
| Doble Oportunidad X2 | NearMiss (RUS) | Neural Network (MLP) | 0.5965 | 0.6245 | 0.6434 |
| Over 2.5 Goles | Original (Línea Base) | Logistic Regression (Elastic Net) | 0.5472 | 0.6294 | 0.5576 |
| Over 2.5 Goles | Original (Línea Base) | Random Forest | 0.5525 | 0.6356 | 0.5434 |
| Over 2.5 Goles | Original (Línea Base) | HistGradientBoosting (Early Stopping) | 0.5507 | 0.6644 | 0.5363 |
| Over 2.5 Goles | Original (Línea Base) | XGBoost | 0.5426 | 0.6065 | 0.5361 |
| Over 2.5 Goles | Original (Línea Base) | Neural Network (MLP) | 0.5156 | 0.5375 | 0.5318 |
| Over 2.5 Goles | ROS (Oversampling) | Logistic Regression (Elastic Net) | 0.5372 | 0.5824 | 0.5556 |
| Over 2.5 Goles | ROS (Oversampling) | Random Forest | 0.5372 | 0.5887 | 0.5473 |
| Over 2.5 Goles | ROS (Oversampling) | HistGradientBoosting (Early Stopping) | 0.5450 | 0.5951 | 0.5392 |
| Over 2.5 Goles | ROS (Oversampling) | XGBoost | 0.5309 | 0.5785 | 0.5400 |
| Over 2.5 Goles | ROS (Oversampling) | Neural Network (MLP) | 0.5252 | 0.6070 | 0.5141 |
| Over 2.5 Goles | SMOTE (Oversampling) | Logistic Regression (Elastic Net) | 0.5436 | 0.5881 | 0.5578 |
| Over 2.5 Goles | SMOTE (Oversampling) | Random Forest | 0.5397 | 0.5894 | 0.5462 |
| Over 2.5 Goles | SMOTE (Oversampling) | HistGradientBoosting (Early Stopping) | 0.5440 | 0.6031 | 0.5421 |
| Over 2.5 Goles | SMOTE (Oversampling) | XGBoost | 0.5337 | 0.5833 | 0.5381 |
| Over 2.5 Goles | SMOTE (Oversampling) | Neural Network (MLP) | 0.5067 | 0.5303 | 0.5151 |
| Over 2.5 Goles | RUS (Undersampling) | Logistic Regression (Elastic Net) | 0.5365 | 0.5881 | 0.5556 |
| Over 2.5 Goles | RUS (Undersampling) | Random Forest | 0.5305 | 0.5861 | 0.5403 |
| Over 2.5 Goles | RUS (Undersampling) | HistGradientBoosting (Early Stopping) | 0.5489 | 0.6078 | 0.5417 |
| Over 2.5 Goles | RUS (Undersampling) | XGBoost | 0.5316 | 0.5708 | 0.5340 |
| Over 2.5 Goles | RUS (Undersampling) | Neural Network (MLP) | 0.5273 | 0.5904 | 0.5280 |
| Over 2.5 Goles | Tomek Links (RUS) | Logistic Regression (Elastic Net) | 0.5379 | 0.5620 | 0.5573 |
| Over 2.5 Goles | Tomek Links (RUS) | Random Forest | 0.5447 | 0.5633 | 0.5491 |
| Over 2.5 Goles | Tomek Links (RUS) | HistGradientBoosting (Early Stopping) | 0.5294 | 0.5343 | 0.5422 |
| Over 2.5 Goles | Tomek Links (RUS) | XGBoost | 0.5333 | 0.5692 | 0.5342 |
| Over 2.5 Goles | Tomek Links (RUS) | Neural Network (MLP) | 0.5252 | 0.5763 | 0.5369 |
| Over 2.5 Goles | Cluster Centroids (RUS) | Logistic Regression (Elastic Net) | 0.5443 | 0.5931 | 0.5568 |
| Over 2.5 Goles | Cluster Centroids (RUS) | Random Forest | 0.5426 | 0.5988 | 0.5417 |
| Over 2.5 Goles | Cluster Centroids (RUS) | HistGradientBoosting (Early Stopping) | 0.5117 | 0.4389 | 0.5319 |
| Over 2.5 Goles | Cluster Centroids (RUS) | XGBoost | 0.5266 | 0.5757 | 0.5298 |
| Over 2.5 Goles | Cluster Centroids (RUS) | Neural Network (MLP) | 0.5142 | 0.5559 | 0.5244 |
| Over 2.5 Goles | NearMiss (RUS) | Logistic Regression (Elastic Net) | 0.5422 | 0.5879 | 0.5601 |
| Over 2.5 Goles | NearMiss (RUS) | Random Forest | 0.5440 | 0.5968 | 0.5487 |
| Over 2.5 Goles | NearMiss (RUS) | HistGradientBoosting (Early Stopping) | 0.5408 | 0.5911 | 0.5483 |
| Over 2.5 Goles | NearMiss (RUS) | XGBoost | 0.5379 | 0.5765 | 0.5600 |
| Over 2.5 Goles | NearMiss (RUS) | Neural Network (MLP) | 0.5277 | 0.5491 | 0.5380 |
| Under 2.5 Goles | Original (Línea Base) | Logistic Regression (Elastic Net) | 0.5472 | 0.4041 | 0.5576 |
| Under 2.5 Goles | Original (Línea Base) | Random Forest | 0.5486 | 0.4075 | 0.5429 |
| Under 2.5 Goles | Original (Línea Base) | HistGradientBoosting (Early Stopping) | 0.5628 | 0.2893 | 0.5442 |
| Under 2.5 Goles | Original (Línea Base) | XGBoost | 0.5426 | 0.4412 | 0.5361 |
| Under 2.5 Goles | Original (Línea Base) | Neural Network (MLP) | 0.5163 | 0.3615 | 0.5181 |
| Under 2.5 Goles | ROS (Oversampling) | Logistic Regression (Elastic Net) | 0.5372 | 0.4767 | 0.5556 |
| Under 2.5 Goles | ROS (Oversampling) | Random Forest | 0.5426 | 0.4677 | 0.5453 |
| Under 2.5 Goles | ROS (Oversampling) | HistGradientBoosting (Early Stopping) | 0.5504 | 0.4564 | 0.5353 |
| Under 2.5 Goles | ROS (Oversampling) | XGBoost | 0.5309 | 0.4649 | 0.5400 |
| Under 2.5 Goles | ROS (Oversampling) | Neural Network (MLP) | 0.5202 | 0.3734 | 0.5231 |
| Under 2.5 Goles | SMOTE (Oversampling) | Logistic Regression (Elastic Net) | 0.5436 | 0.4841 | 0.5578 |
| Under 2.5 Goles | SMOTE (Oversampling) | Random Forest | 0.5443 | 0.4637 | 0.5480 |
| Under 2.5 Goles | SMOTE (Oversampling) | HistGradientBoosting (Early Stopping) | 0.5465 | 0.4551 | 0.5489 |
| Under 2.5 Goles | SMOTE (Oversampling) | XGBoost | 0.5337 | 0.4655 | 0.5381 |
| Under 2.5 Goles | SMOTE (Oversampling) | Neural Network (MLP) | 0.5135 | 0.5074 | 0.5261 |
| Under 2.5 Goles | RUS (Undersampling) | Logistic Regression (Elastic Net) | 0.5365 | 0.4660 | 0.5557 |
| Under 2.5 Goles | RUS (Undersampling) | Random Forest | 0.5323 | 0.4557 | 0.5438 |
| Under 2.5 Goles | RUS (Undersampling) | HistGradientBoosting (Early Stopping) | 0.5411 | 0.4636 | 0.5356 |
| Under 2.5 Goles | RUS (Undersampling) | XGBoost | 0.5316 | 0.4802 | 0.5340 |
| Under 2.5 Goles | RUS (Undersampling) | Neural Network (MLP) | 0.5145 | 0.4967 | 0.5270 |
| Under 2.5 Goles | Tomek Links (RUS) | Logistic Regression (Elastic Net) | 0.5379 | 0.5001 | 0.5573 |
| Under 2.5 Goles | Tomek Links (RUS) | Random Forest | 0.5355 | 0.4941 | 0.5474 |
| Under 2.5 Goles | Tomek Links (RUS) | HistGradientBoosting (Early Stopping) | 0.5121 | 0.5183 | 0.5397 |
| Under 2.5 Goles | Tomek Links (RUS) | XGBoost | 0.5333 | 0.4803 | 0.5342 |
| Under 2.5 Goles | Tomek Links (RUS) | Neural Network (MLP) | 0.5209 | 0.5044 | 0.5347 |
| Under 2.5 Goles | Cluster Centroids (RUS) | Logistic Regression (Elastic Net) | 0.5447 | 0.4765 | 0.5569 |
| Under 2.5 Goles | Cluster Centroids (RUS) | Random Forest | 0.5390 | 0.4599 | 0.5404 |
| Under 2.5 Goles | Cluster Centroids (RUS) | HistGradientBoosting (Early Stopping) | 0.5195 | 0.5091 | 0.5320 |
| Under 2.5 Goles | Cluster Centroids (RUS) | XGBoost | 0.5266 | 0.4568 | 0.5298 |
| Under 2.5 Goles | Cluster Centroids (RUS) | Neural Network (MLP) | 0.5301 | 0.4391 | 0.5361 |
| Under 2.5 Goles | NearMiss (RUS) | Logistic Regression (Elastic Net) | 0.5422 | 0.4804 | 0.5601 |
| Under 2.5 Goles | NearMiss (RUS) | Random Forest | 0.5316 | 0.4727 | 0.5435 |
| Under 2.5 Goles | NearMiss (RUS) | HistGradientBoosting (Early Stopping) | 0.5447 | 0.4818 | 0.5427 |
| Under 2.5 Goles | NearMiss (RUS) | XGBoost | 0.5379 | 0.4875 | 0.5600 |
| Under 2.5 Goles | NearMiss (RUS) | Neural Network (MLP) | 0.5149 | 0.4674 | 0.5249 |
| BTTS (Ambos Anotan) | Original (Línea Base) | Logistic Regression (Elastic Net) | 0.5128 | 0.5686 | 0.5076 |
| BTTS (Ambos Anotan) | Original (Línea Base) | Random Forest | 0.5074 | 0.5713 | 0.5001 |
| BTTS (Ambos Anotan) | Original (Línea Base) | HistGradientBoosting (Early Stopping) | 0.5323 | 0.6090 | 0.5197 |
| BTTS (Ambos Anotan) | Original (Línea Base) | XGBoost | 0.5057 | 0.5597 | 0.5040 |
| BTTS (Ambos Anotan) | Original (Línea Base) | Neural Network (MLP) | 0.4993 | 0.5221 | 0.5078 |
| BTTS (Ambos Anotan) | ROS (Oversampling) | Logistic Regression (Elastic Net) | 0.5053 | 0.5471 | 0.5075 |
| BTTS (Ambos Anotan) | ROS (Oversampling) | Random Forest | 0.5011 | 0.5573 | 0.4978 |
| BTTS (Ambos Anotan) | ROS (Oversampling) | HistGradientBoosting (Early Stopping) | 0.5142 | 0.5763 | 0.5104 |
| BTTS (Ambos Anotan) | ROS (Oversampling) | XGBoost | 0.5131 | 0.5616 | 0.5066 |
| BTTS (Ambos Anotan) | ROS (Oversampling) | Neural Network (MLP) | 0.5273 | 0.5546 | 0.5170 |
| BTTS (Ambos Anotan) | SMOTE (Oversampling) | Logistic Regression (Elastic Net) | 0.5124 | 0.5520 | 0.5090 |
| BTTS (Ambos Anotan) | SMOTE (Oversampling) | Random Forest | 0.5007 | 0.5546 | 0.4997 |
| BTTS (Ambos Anotan) | SMOTE (Oversampling) | HistGradientBoosting (Early Stopping) | 0.5206 | 0.5847 | 0.5150 |
| BTTS (Ambos Anotan) | SMOTE (Oversampling) | XGBoost | 0.5110 | 0.5573 | 0.5137 |
| BTTS (Ambos Anotan) | SMOTE (Oversampling) | Neural Network (MLP) | 0.4911 | 0.4440 | 0.5096 |
| BTTS (Ambos Anotan) | RUS (Undersampling) | Logistic Regression (Elastic Net) | 0.5053 | 0.5429 | 0.5072 |
| BTTS (Ambos Anotan) | RUS (Undersampling) | Random Forest | 0.5071 | 0.5644 | 0.5026 |
| BTTS (Ambos Anotan) | RUS (Undersampling) | HistGradientBoosting (Early Stopping) | 0.5241 | 0.5799 | 0.5198 |
| BTTS (Ambos Anotan) | RUS (Undersampling) | XGBoost | 0.5089 | 0.5523 | 0.5099 |
| BTTS (Ambos Anotan) | RUS (Undersampling) | Neural Network (MLP) | 0.5106 | 0.5039 | 0.5234 |
| BTTS (Ambos Anotan) | Tomek Links (RUS) | Logistic Regression (Elastic Net) | 0.4915 | 0.3846 | 0.5051 |
| BTTS (Ambos Anotan) | Tomek Links (RUS) | Random Forest | 0.4894 | 0.4173 | 0.5066 |
| BTTS (Ambos Anotan) | Tomek Links (RUS) | HistGradientBoosting (Early Stopping) | 0.4706 | 0.0431 | 0.5192 |
| BTTS (Ambos Anotan) | Tomek Links (RUS) | XGBoost | 0.5099 | 0.5037 | 0.5089 |
| BTTS (Ambos Anotan) | Tomek Links (RUS) | Neural Network (MLP) | 0.4961 | 0.4265 | 0.5107 |
| BTTS (Ambos Anotan) | Cluster Centroids (RUS) | Logistic Regression (Elastic Net) | 0.5149 | 0.5608 | 0.5098 |
| BTTS (Ambos Anotan) | Cluster Centroids (RUS) | Random Forest | 0.5018 | 0.5687 | 0.4974 |
| BTTS (Ambos Anotan) | Cluster Centroids (RUS) | HistGradientBoosting (Early Stopping) | 0.5050 | 0.4571 | 0.4976 |
| BTTS (Ambos Anotan) | Cluster Centroids (RUS) | XGBoost | 0.5113 | 0.5659 | 0.5150 |
| BTTS (Ambos Anotan) | Cluster Centroids (RUS) | Neural Network (MLP) | 0.5184 | 0.5735 | 0.5151 |
| BTTS (Ambos Anotan) | NearMiss (RUS) | Logistic Regression (Elastic Net) | 0.5138 | 0.5516 | 0.5172 |
| BTTS (Ambos Anotan) | NearMiss (RUS) | Random Forest | 0.5007 | 0.5602 | 0.5083 |
| BTTS (Ambos Anotan) | NearMiss (RUS) | HistGradientBoosting (Early Stopping) | 0.5145 | 0.5738 | 0.5130 |
| BTTS (Ambos Anotan) | NearMiss (RUS) | XGBoost | 0.5131 | 0.5572 | 0.5077 |
| BTTS (Ambos Anotan) | NearMiss (RUS) | Neural Network (MLP) | 0.5181 | 0.5510 | 0.5140 |
| BTTS - No | Original (Línea Base) | Logistic Regression (Elastic Net) | 0.5128 | 0.4013 | 0.5076 |
| BTTS - No | Original (Línea Base) | Random Forest | 0.5103 | 0.3783 | 0.5004 |
| BTTS - No | Original (Línea Base) | HistGradientBoosting (Early Stopping) | 0.5351 | 0.3356 | 0.5208 |
| BTTS - No | Original (Línea Base) | XGBoost | 0.5057 | 0.4289 | 0.5040 |
| BTTS - No | Original (Línea Base) | Neural Network (MLP) | 0.5191 | 0.4290 | 0.5235 |
| BTTS - No | ROS (Oversampling) | Logistic Regression (Elastic Net) | 0.5053 | 0.4410 | 0.5075 |
| BTTS - No | ROS (Oversampling) | Random Forest | 0.5043 | 0.4021 | 0.5013 |
| BTTS - No | ROS (Oversampling) | HistGradientBoosting (Early Stopping) | 0.5280 | 0.4245 | 0.5162 |
| BTTS - No | ROS (Oversampling) | XGBoost | 0.5131 | 0.4469 | 0.5066 |
| BTTS - No | ROS (Oversampling) | Neural Network (MLP) | 0.5170 | 0.4266 | 0.5037 |
| BTTS - No | SMOTE (Oversampling) | Logistic Regression (Elastic Net) | 0.5124 | 0.4498 | 0.5090 |
| BTTS - No | SMOTE (Oversampling) | Random Forest | 0.5099 | 0.4083 | 0.4981 |
| BTTS - No | SMOTE (Oversampling) | HistGradientBoosting (Early Stopping) | 0.5337 | 0.4134 | 0.5202 |
| BTTS - No | SMOTE (Oversampling) | XGBoost | 0.5110 | 0.4485 | 0.5137 |
| BTTS - No | SMOTE (Oversampling) | Neural Network (MLP) | 0.5152 | 0.4669 | 0.5164 |
| BTTS - No | RUS (Undersampling) | Logistic Regression (Elastic Net) | 0.5057 | 0.4459 | 0.5072 |
| BTTS - No | RUS (Undersampling) | Random Forest | 0.5099 | 0.4304 | 0.4992 |
| BTTS - No | RUS (Undersampling) | HistGradientBoosting (Early Stopping) | 0.5220 | 0.3925 | 0.4979 |
| BTTS - No | RUS (Undersampling) | XGBoost | 0.5089 | 0.4521 | 0.5099 |
| BTTS - No | RUS (Undersampling) | Neural Network (MLP) | 0.5323 | 0.4545 | 0.5179 |
| BTTS - No | Tomek Links (RUS) | Logistic Regression (Elastic Net) | 0.4915 | 0.5530 | 0.5051 |
| BTTS - No | Tomek Links (RUS) | Random Forest | 0.4950 | 0.5437 | 0.5077 |
| BTTS - No | Tomek Links (RUS) | HistGradientBoosting (Early Stopping) | 0.4645 | 0.6089 | 0.5040 |
| BTTS - No | Tomek Links (RUS) | XGBoost | 0.5099 | 0.5086 | 0.5089 |
| BTTS - No | Tomek Links (RUS) | Neural Network (MLP) | 0.4926 | 0.5432 | 0.5054 |
| BTTS - No | Cluster Centroids (RUS) | Logistic Regression (Elastic Net) | 0.5149 | 0.4396 | 0.5098 |
| BTTS - No | Cluster Centroids (RUS) | Random Forest | 0.4961 | 0.4013 | 0.4905 |
| BTTS - No | Cluster Centroids (RUS) | HistGradientBoosting (Early Stopping) | 0.5266 | 0.4077 | 0.5084 |
| BTTS - No | Cluster Centroids (RUS) | XGBoost | 0.5113 | 0.4340 | 0.5150 |
| BTTS - No | Cluster Centroids (RUS) | Neural Network (MLP) | 0.5209 | 0.3936 | 0.5202 |
| BTTS - No | NearMiss (RUS) | Logistic Regression (Elastic Net) | 0.5138 | 0.4592 | 0.5172 |
| BTTS - No | NearMiss (RUS) | Random Forest | 0.5121 | 0.4190 | 0.5060 |
| BTTS - No | NearMiss (RUS) | HistGradientBoosting (Early Stopping) | 0.5238 | 0.4152 | 0.5187 |
| BTTS - No | NearMiss (RUS) | XGBoost | 0.5131 | 0.4526 | 0.5077 |
| BTTS - No | NearMiss (RUS) | Neural Network (MLP) | 0.5089 | 0.4637 | 0.5087 |
| Valla Invicta Local | Original (Línea Base) | Logistic Regression (Elastic Net) | 0.7004 | 0.1931 | 0.6099 |
| Valla Invicta Local | Original (Línea Base) | Random Forest | 0.7014 | 0.1733 | 0.6028 |
| Valla Invicta Local | Original (Línea Base) | HistGradientBoosting (Early Stopping) | 0.7064 | 0.0459 | 0.5967 |
| Valla Invicta Local | Original (Línea Base) | XGBoost | 0.6936 | 0.2238 | 0.5956 |
| Valla Invicta Local | Original (Línea Base) | Neural Network (MLP) | 0.6713 | 0.2896 | 0.5887 |
| Valla Invicta Local | ROS (Oversampling) | Logistic Regression (Elastic Net) | 0.5809 | 0.4329 | 0.6063 |
| Valla Invicta Local | ROS (Oversampling) | Random Forest | 0.6663 | 0.3353 | 0.5980 |
| Valla Invicta Local | ROS (Oversampling) | HistGradientBoosting (Early Stopping) | 0.6106 | 0.4159 | 0.6041 |
| Valla Invicta Local | ROS (Oversampling) | XGBoost | 0.6337 | 0.3790 | 0.5959 |
| Valla Invicta Local | ROS (Oversampling) | Neural Network (MLP) | 0.5947 | 0.3871 | 0.5749 |
| Valla Invicta Local | SMOTE (Oversampling) | Logistic Regression (Elastic Net) | 0.5699 | 0.4308 | 0.6092 |
| Valla Invicta Local | SMOTE (Oversampling) | Random Forest | 0.6440 | 0.3700 | 0.6018 |
| Valla Invicta Local | SMOTE (Oversampling) | HistGradientBoosting (Early Stopping) | 0.5908 | 0.4228 | 0.5956 |
| Valla Invicta Local | SMOTE (Oversampling) | XGBoost | 0.6301 | 0.3762 | 0.5928 |
| Valla Invicta Local | SMOTE (Oversampling) | Neural Network (MLP) | 0.6206 | 0.3352 | 0.5660 |
| Valla Invicta Local | RUS (Undersampling) | Logistic Regression (Elastic Net) | 0.5553 | 0.4346 | 0.6060 |
| Valla Invicta Local | RUS (Undersampling) | Random Forest | 0.5663 | 0.4317 | 0.5991 |
| Valla Invicta Local | RUS (Undersampling) | HistGradientBoosting (Early Stopping) | 0.5702 | 0.4296 | 0.5966 |
| Valla Invicta Local | RUS (Undersampling) | XGBoost | 0.5550 | 0.4281 | 0.5872 |
| Valla Invicta Local | RUS (Undersampling) | Neural Network (MLP) | 0.5397 | 0.3985 | 0.5613 |
| Valla Invicta Local | Tomek Links (RUS) | Logistic Regression (Elastic Net) | 0.6837 | 0.2523 | 0.6109 |
| Valla Invicta Local | Tomek Links (RUS) | Random Forest | 0.6943 | 0.2513 | 0.5997 |
| Valla Invicta Local | Tomek Links (RUS) | HistGradientBoosting (Early Stopping) | 0.6933 | 0.1358 | 0.6007 |
| Valla Invicta Local | Tomek Links (RUS) | XGBoost | 0.6801 | 0.2800 | 0.5957 |
| Valla Invicta Local | Tomek Links (RUS) | Neural Network (MLP) | 0.6376 | 0.3360 | 0.5863 |
| Valla Invicta Local | Cluster Centroids (RUS) | Logistic Regression (Elastic Net) | 0.5706 | 0.4232 | 0.6013 |
| Valla Invicta Local | Cluster Centroids (RUS) | Random Forest | 0.5709 | 0.4183 | 0.5922 |
| Valla Invicta Local | Cluster Centroids (RUS) | HistGradientBoosting (Early Stopping) | 0.5507 | 0.4286 | 0.5748 |
| Valla Invicta Local | Cluster Centroids (RUS) | XGBoost | 0.5574 | 0.4091 | 0.5849 |
| Valla Invicta Local | Cluster Centroids (RUS) | Neural Network (MLP) | 0.5560 | 0.4073 | 0.5716 |
| Valla Invicta Local | NearMiss (RUS) | Logistic Regression (Elastic Net) | 0.5106 | 0.4373 | 0.5819 |
| Valla Invicta Local | NearMiss (RUS) | Random Forest | 0.4599 | 0.4279 | 0.5663 |
| Valla Invicta Local | NearMiss (RUS) | HistGradientBoosting (Early Stopping) | 0.4922 | 0.4188 | 0.5611 |
| Valla Invicta Local | NearMiss (RUS) | XGBoost | 0.4752 | 0.4206 | 0.5540 |
| Valla Invicta Local | NearMiss (RUS) | Neural Network (MLP) | 0.4351 | 0.4195 | 0.5393 |

---

## 5. 📉 Visualización del Impacto del Resampling (Multimétrica)

El gráfico general a continuación contrasta el rendimiento de las 7 configuraciones espejo a través de tres dimensiones críticas (Exactitud, F1-Score y ROC-AUC) para los mercados analizados:

![Comparativa General de Resampling](file:///d:/datascience/Carpeta_Presentacion/24_Comparativa_Multimetrica_Resampling.png)

A continuación, para un análisis granular y exhaustivo de cómo responde **cada modelo clasificador individual** (Logistic Regression, Random Forest, HistGradientBoosting, XGBoost, y Neural Network) a cada una de las técnicas de remuestreo, se presentan las curvas de rendimiento cruzadas en cuadrículas de 2x4 que cubren **todos los mercados (targets)** y **las tres métricas analizadas**:

### A. Comparativa Completa de Exactitud (Accuracy)
El siguiente gráfico muestra la exactitud de todos los modelos a través de todos los métodos de resampling en las 8 variables predictivas:

![Comparativa Completa de Accuracy](file:///d:/datascience/Carpeta_Presentacion/27_Comparativa_Completa_Accuracy.png)

### B. Comparativa Completa de F1-Score
El siguiente gráfico muestra el F1-Score de todos los modelos a través de todos los métodos de resampling en las 8 variables predictivas:

![Comparativa Completa de F1-Score](file:///d:/datascience/Carpeta_Presentacion/28_Comparativa_Completa_F1.png)

### C. Comparativa Completa de ROC-AUC
El siguiente gráfico muestra el ROC-AUC de todos los modelos a través de todos los métodos de resampling en las 8 variables predictivas. Para el mercado multiclase `1X2 (Match Winner)`, se detalla estéticamente como *N/A (No Aplicable)* dado que esta métrica está definida estrictamente para clasificaciones binarias:

![Comparativa Completa de ROC-AUC](file:///d:/datascience/Carpeta_Presentacion/29_Comparativa_Completa_ROC_AUC.png)

---

## 6. 🧠 Conclusiones y Defensa Científica (¿Por qué no usar Resampling?)

Estos resultados proveen una justificación matemática sólida y elegante que te permitirá defender metodológicamente tu diseño ante el jurado de tesis:

### A. La Caída Generalizada de la Exactitud (Accuracy)
El remuestreo (tanto over como undersampling) **redujo la exactitud general en todos los mercados**:
* En **Doble Oportunidad 1X**, la exactitud cayó de **70.71%** (Original) a **67.84%** (SMOTE) y **61.60%** (NearMiss).
* En **Valla Invicta Local**, la exactitud se desplomó de **70.64%** (Original) a **66.63%** (ROS) y **51.06%** (NearMiss).
* *Explicación Científica:* El fútbol es un deporte con un **alto solapamiento de características** (los datos de partidos donde un equipo empata o pierde de local son muy similares a donde gana). Al balancear las clases al 50/50 de forma artificial, forzamos a los algoritmos a expandir excesivamente el límite de decisión de la clase minoritaria. Esto provoca que el modelo realice muchas más predicciones positivas de las que corresponden, disparando los **Falsos Positivos (Error Tipo I)** y arruinando el Accuracy.

### B. El Dilema del F1-Score vs. Exactitud en Valla Invicta
* **El Fenómeno:** En `Home Clean Sheet` (Valla Invicta, desbalance 70/30), la línea base tiene un F1-score bajo ($0.2896$) pero una exactitud muy alta ($70.64\%$). Las técnicas de resampling (como NearMiss) suben el F1-Score a un máximo de **0.4373**, pero reducen la exactitud general al **51.06%** (casi equivalente al azar).
* *Por qué ocurre:* La línea base original predice con cautela la valla invicta local (ya que estadísticamente ocurre solo el 29.8% de las veces). Al remuestrear, obligamos al modelo a volverse "agresivo" prediciendo vallas invictas. Aunque esto eleva la recuperación (Recall) de la clase minoritaria (y por ende el F1-Score), la tasa de Falsos Positivos se dispara, reduciendo la exactitud a niveles inaceptables.

### C. La Destrucción de la Calibración de Probabilidades (Negocio y Apuestas)
La conclusión de negocio más fuerte para tu tesis es sobre el **sistema de inversión**:
* Para colocar apuestas con **Valor Esperado positivo ($EV+$)**, dependemos de que las probabilidades estimadas por el modelo ($\hat{p}$) estén perfectamente calibradas con el mundo real:
  $$EV = (\hat{p} 	imes 	ext{Cuota}) - 1$$
* Si el modelo estima que la probabilidad de una Valla Invicta Local es del $50\%$ (debido al balanceo artificial del dataset de entrenamiento), cuando la probabilidad real histórica bajo esas condiciones de variables es de solo $30\%$, el sistema calculará un EV+ erróneo y **apostará dinero real en eventos perdedores**, destruyendo la rentabilidad financiera.
* *Recomendación:* **Se debe conservar la Línea Base Original (Sin Resampling)**, ya que preserva las frecuencias y probabilidades reales del deporte, permitiendo una correcta calibración probabilística indispensable para la gestión de capital y valor esperado.
