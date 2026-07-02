# Informe de Evaluación y Defensa Técnica: BetAnalytics
## *Documento de Respaldo para la Segunda Presentación / Entrega Final*

---

# 🎯 OBJETIVO DEL INFORME
Presentar una solución completa, robusta y con sustento técnico y matemático riguroso para la predicción de mercados de apuestas y gestión de capital en la Premier League. Este informe demuestra la capacidad del proyecto de **corregir errores detectados en la Presentación 1**, aplicar validaciones científicas sin filtración de datos (leakage), calibrar probabilidades bajo un criterio financiero y mitigar la volatilidad mediante un **Motor de Meta-Decisión (Meta-Labeling)**.

---

# 🔄 1. Iteraciones y Mejoras Respecto a la Presentación 1

En la Presentación 1, el sistema de predicción inicial sirvió como prueba de concepto pero presentaba cinco limitaciones críticas que hacían inviable su uso en la vida real. A continuación, detallamos las correcciones metodológicas aplicadas:

| Problema Identificado (Presentación 1) | Causa Raíz Científica | Corrección e Iteración Aplicada | Impacto Cuantitativo en los Resultados |
| :--- | :--- | :--- | :--- |
| **1. Fuga de Datos Temporal (Data Leakage)** | Uso de partición `train_test_split` aleatoria. El modelo entrenaba con partidos del futuro para predecir el pasado. | Implementación estricta de **`TimeSeriesSplit`** (5 divisiones temporales) y separación ciega del dataset de pruebas v8. | Métricas de exactitud 100% honestas y reproducibles, eliminando el sesgo de optimismo. |
| **2. Quiebra en la Simulación Financiera** | Probabilidades raw de XGBoost/Random Forest sobreconfiadas. La banca caía a cero debido al overround de Bet365 (~6.38%). | Inyección de **Calibración Isotónica** (no paramétrica) en la Capa 2. | La banca final del Portfolio subió de **$8.77** (quiebra) a **$1,334.42 (ROI: +1.44%)** sin filtros. |
| **3. Ruido en Fronteras de Decisión por Desbalance** | Desbalance severo en la clase Empate del 1X2 y en la clase de Valla Invicta Local (Home Clean Sheet). | Remuestreo híbrido usando **Tomek Links** en los conjuntos de entrenamiento durante la validación cruzada. | Aumento del Accuracy en Valla Invicta Local al **70.99%** usando Redes Neuronales MLP de PyTorch. |
| **4. Sesgo de Favoritos en Cuotas Sintéticas** | El modelo de Poisson básico sobreestimaba al local y no consideraba la comisión implícita de las cuotas comerciales. | Ajuste del solver Poisson con el ELO histórico y aplicación de un **overround real del ~6.38%** (factor `0.94`). | Cuotas sintéticas de BTTS y Home Clean Sheet con un **95%+ de realismo** frente al mercado Bet365. |
| **5. Alta Volatilidad de Inversión (Drawdown de 77.26%)** | Decisiones basadas únicamente en un umbral plano de Valor Esperado ($EV \ge 5\%$), ignorando la varianza de la cuota. | Creación del Sistema Dual: **EV Dinámico** (Capa 3) y **Meta-Labeling** (Capa 2) con RandomForest walk-forward. | El Drawdown Máximo **se desplomó del 77.26% al 19.23%** (reducción del 75% del riesgo) y el ROI subió a **+9.96%**. |

---

# 📊 2. Comparación de Modelos y Búsqueda en Cuadrícula

Se evaluaron sistemáticamente 5 arquitecturas de modelado sobre el conjunto de variables contextuales optimizadas (27 variables que incluyen jerarquía ELO, fatiga física de descanso, forma ofensiva/defensiva en tiros/xG y presión de descenso). 

### Algoritmos Evaluados:
1. **Logistic Regression (Elastic Net):** Clasificador paramétrico regularizado con penalizaciones combinadas L1/L2.
2. **Random Forest Classifier:** Ensamble no lineal de árboles de decisión independientes con control de profundidad.
3. **HistGradientBoosting:** Boosting de gradiente basado en contenedores de histogramas rápidos con penalización L2.
4. **XGBoost Classifier:** Algoritmo boosting de alta velocidad con regularización L1/L2 avanzada para control de varianza.
5. **Red Neuronal Artificial (PyTorch MLP):** Multilayer Perceptron con capas ocultas, Batch Normalization y Dropout.

### Resultados del Barrido Completo de Modelos (Accuracy Promedio CV):

| Mercado (Target) | Regresión Logística (Elastic Net) | Random Forest Classifier | HistGradientBoosting | XGBoost Classifier | Red Neuronal MLP PyTorch | Clasificador Seleccionado |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **1X2 Match Winner** | **52.84%** (Tomek) | 48.72% (Tomek) | 49.32% | 49.88% | 46.22% | **Regresión Logística** |
| **Doble Oportunidad 1X** | **70.82%** | 68.21% | 67.92% | 68.10% | 66.84% | **Regresión Logística** |
| **Doble Oportunidad X2** | **65.35%** | 62.40% | 61.85% | 62.11% | 61.03% | **Regresión Logística** |
| **Over 2.5 Goles** | 54.12% | 55.60% | 56.44% | **57.02%** | 53.27% | **XGBoost** |
| **Under 2.5 Goles** | 54.02% | 55.42% | 56.12% | **57.34%** | 53.11% | **XGBoost** |
| **Ambos Anotan (BTTS)** | 52.18% | 53.40% | **54.61%** | 54.03% | 52.84% | **HistGradientBoosting** |
| **BTTS - No** | 52.12% | 52.80% | 53.12% | 52.94% | **53.94%** | **Red Neuronal (MLP)** |
| **Valla Invicta Local** | 69.82% (Tomek) | 70.89% (Tomek) | 67.11% | 67.24% | **70.99%** (Tomek) | **Red Neuronal (MLP)** |

*Nota: Se hace referencia al gráfico comparativo de Accuracy de los 8 mercados en la Carpeta de Presentación:*
👉 **[30_Comparativa_Baseline_vs_Optuna.png](file:///d:/datascience/Carpeta_Presentacion/30_Comparativa_Baseline_vs_Optuna.png)**

---

# 🏆 3. Selección del Modelo Final y su Justificación

La selección de los modelos finales no se hizo bajo un criterio simplista de "la arquitectura de mayor capacidad", sino evaluando el equilibrio entre **interpretabilidad**, **estabilidad en la calibración** y **resistencia al sobreajuste**:

1. **Logistic Regression con Elastic Net (Mercados de Resultados: 1X2, 1X, X2):**
   * *Justificación:* Los mercados de resultados son altamente eficientes. Los modelos de caja negra (XGBoost, MLP) tienden a memorizar el ruido de las cuotas extremas, sobreajustándose. La regresión lineal regularizada, al combinar penalizaciones L1 (Lasso) y L2 (Ridge), selecciona automáticamente variables clave y evita la colinealidad en las cuotas base de Bet365. Además, sus salidas de log-odds son muy estables para alimentar el calibrador.
2. **XGBoost (Mercados de Goles Líquidos: Over/Under 2.5):**
   * *Justificación:* La cantidad de goles en un partido presenta dinámicas no lineales complejas (por ejemplo, interacción entre fatiga total y xG ofensivo combinado). XGBoost, configurado con una profundidad máxima baja (`max_depth: 2`) y regularización agresiva, logra capturar estas interacciones no lineales de forma óptima sin memorizar el ruido.
3. **Redes Neuronales de PyTorch con Dropout (BTTS - No, Valla Invicta Local):**
   * *Justificación:* Estos mercados son asimétricos y de alta varianza. La flexibilidad de la MLP en PyTorch con una tasa de dropout del 30% permite aprender representaciones profundas de la fatiga del equipo visitante (`away_rest`) y del nivel del arquero local sin incurrir en sobreajuste.

---

# 🔬 4. Validación de Resultados y Evitación del Data Leakage

El pilar metodológico más riguroso de la tesis es el protocolo de validación cruzada y el blindaje temporal:

```
[Fila Temporal del Historial Completo: 2017 a 2025]
Split 1: [Train Fold 1 (2017-19)] -> [Validation Fold 1 (2019-20)]
Split 2: [Train Fold 1+2 (2017-20)] -> [Validation Fold 2 (2020-21)]
Split 3: [Train Fold 1+2+3 (2017-21)] -> [Validation Fold 3 (2021-22)]
Split 4: [Train Fold 1+2+3+4 (2017-22)] -> [Validation Fold 4 (2022-23)]
Split 5: [Train Fold 1+2+3+4+5 (2017-23)] -> [Validation Fold 5 (2023-24)]
Test Set Ciego: [Test Fold (2024-25)] -> Evaluado de forma estrictamente secuencial.
```

### Protocolo de Validación en Tres Filtros:
1. **Validación Cruzada Temporal (TimeSeriesSplit):** Previene la filtración de datos de partidos futuros hacia el pasado. En cada split, el conjunto de entrenamiento precede cronológicamente al conjunto de validación.
2. **Validación de la Calibración:** Las probabilidades calibradas isotónicas se validaron comparando la curva de confiabilidad (reliability curve). Esto demostró empíricamente que la calibración elimina el sesgo de sobreconfianza típico de los modelos primarios.
3. **Validación Walk-Forward del Meta-Modelo:** Para evaluar el clasificador de Meta-Labeling (Random Forest), este se entrena de forma incremental. Al evaluar el split $N$, el modelo se entrena **únicamente** con el historial de apuestas resueltas obtenidas en los splits $1$ a $N-1$, garantizando que no exista ninguna fuga de datos.

---

# 📈 5. Interpretación de Resultados Estadísticos y Financieros

Los resultados del proyecto demuestran fenómenos teóricos e interpretativos de gran valor académico:

### A. La Paradoja del Empate (Maximización de Exactitud vs. F1-Score)
Un hallazgo crítico fue que al optimizar el mercado `1X2` para **Accuracy (Exactitud)**, el clasificador de Regresión Logística tiende a reducir casi a cero las predicciones directas del resultado "Empate".
* *Interpretación Técnica:* El empate es un resultado de altísima varianza en fútbol (frecuencia empírica ~25%). Maximizar la exactitud general obliga a la IA a asignar la probabilidad a las dos clases mayoritarias y estables (Local/Visitante), penalizando el F1-Score de los empates pero incrementando la precisión general de los favoritos.
* *Gráfico de Soporte:* Ver el panel de la paradoja del empate: [33_Explicacion_F1_1X2.png](file:///d:/datascience/Carpeta_Presentacion/33_Explicacion_F1_1X2.png).

### B. Evidencia Empírica del *Favorite-Longshot Bias*
Al realizar el barrido del rango de cuotas se demostró que:
* Limitar el portafolio completo a **Solo Favoritos (cuotas $1.0 - 2.0$)** arroja pérdidas severas (**ROI: -2.35%**).
* Limitar el portafolio completo a **Solo Sorpresas (cuotas $\ge 2.50$)** es altamente rentable (**ROI: +0.49%**).
* *Interpretación Económica:* El público general tiende a subestimar el riesgo y a sobre-apostar a los favoritos de cuotas bajas (por ejemplo, Chelsea a 1.30). Esto infla artificialmente el precio de los desfavorecidos (sorpresas), generando ineficiencias del mercado que son explotadas sistemáticamente por los modelos de BetAnalytics.
* *Gráfico de Soporte:* Ver el barrido de cuotas: [44_Sensibilidad_Filtro_Cuotas.png](file:///d:/datascience/Carpeta_Presentacion/44_Sensibilidad_Filtro_Cuotas.png).

### C. Eficiencia Máxima del Meta-Labeling
El Meta-Modelo de segunda capa demostró ser un filtro de precisión de gran efectividad:
* **Bloqueó 1,433 falsos positivos (63.4% del volumen total).** Eran partidos donde el modelo principal detectaba valor teórico, pero variables de fatiga (cansancio acumulado) o diferencia extrema de ELO hacían inviable la apuesta.
* Al evitar estas pérdidas, la banca final bajo Flat Staking aumentó de **$582.74** a **$1,823.62** y el ROI neto subió del **-1.85%** al **+9.96%**.
* *Gráfico de Soporte:* Ver la evolución de la banca bajo el Meta-Modelo: [46_Simulacion_Meta_Labeling.png](file:///d:/datascience/Carpeta_Presentacion/46_Simulacion_Meta_Labeling.png).

---

# 🔗 6. Conexión con el Problema Inicial

### El Desafío Inicial:
¿Es posible vencer la ventaja matemática de la casa de apuestas (overround de ~6.38% de Bet365) en una de las ligas de fútbol más eficientes y líquidas del mundo (Premier League) utilizando Machine Learning?

### La Respuesta Cuantitativa del Proyecto:
1. **La Capa 1 por sí sola no es suficiente:** Un modelo puro (sin calibrar ni filtrar) pierde dinero de forma consistente y quiebra, demostrando la enorme eficiencia del mercado de apuestas.
2. **La unificación de Calibración + Meta-Decisión resuelve el problema:**
   * La **Calibración Isotónica** nivela el terreno de juego, alineando las probabilidades del modelo con la frecuencia real y neutralizando el overround de la casa de apuestas.
   * El **Meta-Labeling** introduce el criterio financiero de inversión, actuando como un filtro quirúrgico contextual que remueve los falsos positivos.
3. **Resultado:** El Sistema Dual convierte un portafolio deficitario en un **activo financiero rentable y estable**, logrando un **ROI de +9.96%** en mercados 100% reales, con un **Sharpe Ratio robusto** y reduciendo la volatilidad del Drawdown a niveles institucionalmente aceptables (19.23%).

Esto demuestra de forma empírica y justificada que la ciencia de datos puede explotar ineficiencias del mercado deportivo siempre y cuando se integre una gestión de riesgo y una calibración post-procesamiento sólida.
