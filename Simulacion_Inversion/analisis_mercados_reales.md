# Análisis de Inversión: Simulación Exclusiva en Mercados Reales de Bet365

Este informe detalla el comportamiento de los modelos de Machine Learning y las calibraciones de probabilidad cuando se limitan **estrictamente a mercados con cuotas reales o replicadas por arbitraje financiero exacto**. 

Se han eliminado por completo los mercados de goles que utilizaban cuotas aproximadas por el modelo Poisson (*Ambos Anotan / BTTS* y *Home Clean Sheet*).

---

## 📊 1. Resumen de Resultados

Banca inicial: **$1,000 USD** | Período de Simulación: **2,356 partidos** (Línea de tiempo consolidada).

### A. Estrategia de Stake Fijo (Flat Staking - 1% de Banca Inicial = $10 USD)

En esta estrategia, el tamaño de la apuesta es constante, lo que permite evaluar el rendimiento bruto del modelo frente a la ventaja de la casa sin amplificar la varianza por estimaciones de probabilidad.

| Mercado / Cartera | Calibración | Banca Final | ROI | Apuestas Colocadas | Tasa de Acierto (Win Rate) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **1X2 Match Winner** | Sin Calibrar | $3.60 | -6.58% | 1,515 | 29.90% |
| | **Isotónica** | **$822.60** | **-0.88%** | 2,022 | **27.05%** |
| | Sigmoide | $545.60 | -2.29% | 1,982 | 24.52% |
| **Double Chance 1X** | Sin Calibrar | $544.75 | -11.41% | 399 | 51.13% |
| | **Isotónica** | **$498.06** | **-9.80%** | 512 | **54.49%** |
| | Sigmoide | $380.24 | -13.80% | 449 | 46.77% |
| **Double Chance X2** | Sin Calibrar | $808.97 | -4.57% | 418 | 35.17% |
| | Isotónica | $731.96 | -5.58% | 480 | 49.17% |
| | **Sigmoide** | **$954.86** | **-1.09%** | 414 | **46.14%** |
| **Over 2.5 Goals** | Sin Calibrar | $850.40 | -3.21% | 466 | 46.14% |
| | **Isotónica** | **$867.00** | **-1.91%** | 697 | **52.65%** |
| | Sigmoide | $749.10 | -4.17% | 601 | 48.59% |
| **Under 2.5 Goals** | Sin Calibrar | $734.30 | -3.19% | 832 | 37.86% |
| | **Isotónica** | **$966.00** | **-0.42%** | 816 | **43.75%** |
| | Sigmoide | $937.60 | -0.81% | 766 | 40.73% |
| **Portfolio Real Combinado** | Sin Calibrar | $0.38 | -6.97% | 1,434 | 32.22% |
| | **Isotónica** | **$582.74** | **-1.85%** | 2,260 | **32.74%** |
| | Sigmoide | $3.29 | -4.71% | 2,117 | 27.87% |

---

### B. Estrategia de Reinversión Geométrica (Quarter Kelly - Máx 2.5% de Banca)

Bajo esta estrategia, el tamaño de la apuesta depende de la ventaja estimada por el modelo (`EV`). Si el modelo no está bien calibrado y sobreestima su ventaja, Kelly sobreapuesta de forma agresiva acelerando la pérdida.

| Mercado / Cartera | Calibración | Banca Final | ROI | Apuestas Colocadas | Tasa de Acierto (Win Rate) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **1X2 Match Winner** | Sin Calibrar | $25.44 | -11.38% | 1,776 | 29.39% |
| | **Isotónica** | **$82.87** | **-3.10%** | 2,022 | **27.05%** |
| | Sigmoide | $103.23 | **-2.32%** | 1,982 | 24.52% |
| **Double Chance 1X** | Sin Calibrar | $288.97 | -12.54% | 399 | 51.13% |
| | **Isotónica** | **$246.12** | **-11.10%** | 512 | **54.49%** |
| | Sigmoide | $189.66 | -15.79% | 449 | 46.77% |
| **Double Chance X2** | Sin Calibrar | $562.86 | -6.86% | 418 | 35.17% |
| | Isotónica | $477.14 | -6.51% | 480 | 49.17% |
| | **Sigmoide** | **$725.08** | **-3.37%** | 414 | **46.14%** |
| **Over 2.5 Goals** | Sin Calibrar | $637.33 | -5.08% | 466 | 46.14% |
| | **Isotónica** | **$641.60** | **-2.60%** | 697 | **52.65%** |
| | Sigmoide | $446.06 | -6.29% | 601 | 48.59% |
| **Under 2.5 Goals** | Sin Calibrar | $354.26 | -3.80% | 832 | 37.86% |
| | **Isotónica** | **$593.13** | **-1.65%** | 816 | **43.75%** |
| | Sigmoide | $534.43 | -2.13% | 766 | 40.73% |
| **Portfolio Real Combinado** | Sin Calibrar | $8.36 | -8.98% | 2126 | 31.89% |
| | **Isotónica** | **$69.60** | **-1.75%** | 2,260 | **32.74%** |
| | Sigmoide | $25.61 | -3.92% | 2189 | 28.10% |

---

## 🔬 2. Análisis Científico: ¿Por qué la estrategia es perdedora en mercados 100% reales?

La transición a mercados con cuotas reales de Bet365 revela la cruda realidad cuantitativa del mercado de apuestas deportivas:

### A. La Eficiencia de Bet365 en la Premier League
La Premier League inglesa es uno de los mercados deportivos más líquidos y eficientes del mundo. Cientos de millones de dólares se transan en cada partido. Bet365 ajusta sus cuotas de manera óptima utilizando modelos de última generación y corrigiéndolas según el flujo del dinero de apostadores profesionales (lo que elimina cualquier sesgo residual antes del silbatazo inicial).
* Para ganarle a Bet365 en estos mercados, un modelo no solo debe tener "cierta capacidad de predicción", sino que debe tener una precisión que supere el **overround (el margen de ganancia de la casa)**, el cual suele oscilar entre el **4% y el 7%**.
* Con un ROC-AUC de aproximadamente $0.52 - 0.55$, los modelos de producción tienen un desempeño respetable, pero insuficiente para superar la ventaja matemática incorporada del corredor de apuestas.

### B. El Impacto Mitigador de la Calibración Isotónica
Aunque los resultados globales son negativos, la **Calibración Isotónica** demuestra un valor científico sobresaliente para la tesis:
* En el mercado **1X2 (Match Winner)** con Flat Stake, el modelo sin calibrar cae casi a cero (**$3.60**, ROI de **-6.58%**). Al aplicar la Calibración Isotónica, la banca final se mantiene en **$822.60** (ROI de **-0.88%**). Esto significa que la calibración mitigó casi todo el impacto negativo del overround de la casa, dejando al modelo al borde del punto de equilibrio.
* En **Under 2.5 Goals**, la calibración isotónica llevó la banca final a **$966.00** (ROI de **-0.42%**), comparado con los **$734.30** (ROI de **-3.19%**) del modelo base.

Esto demuestra que **la calibración cumple exactamente con su función teórica**: evita que el modelo sobreestime su ventaja (`EV`) en cuotas sobrevaloradas, filtrando apuestas impulsivas de bajo valor esperado y estabilizando drásticamente la curva de capital.

---

## 📈 3. Visualización de las Curvas de Capital

Se han generado gráficos independientes del crecimiento de la banca para los 5 mercados y su portafolio real bajo ambas estrategias:

1. **Stake Fijo (1%):** [36_Simulacion_Mercados_Reales_Flat.png](file:///d:/datascience/Carpeta_Presentacion/36_Simulacion_Mercados_Reales_Flat.png)
   * *Qué muestra:* Se puede observar de forma lineal cómo el modelo sin calibrar (línea gris/roja) decae con rapidez hacia la quiebra. Por otro lado, la curva de la Calibración Isotónica (azul) muestra una resistencia notable, amortiguando las rachas de pérdidas y manteniéndose cerca del capital inicial.
   
2. **Quarter Kelly:** [37_Simulacion_Mercados_Reales_Kelly.png](file:///d:/datascience/Carpeta_Presentacion/37_Simulacion_Mercados_Reales_Kelly.png)
   * *Qué muestra:* Al ser una estrategia perdedora a largo plazo, el criterio de Kelly acelera la caída. Sin embargo, se aprecia claramente que las versiones calibradas (especialmente la Isotónica en azul) caen a un ritmo mucho más lento que las versiones sin calibrar debido a la correcta contención del tamaño de las apuestas cuando el edge real es bajo.
