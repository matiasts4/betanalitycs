# Informe Avanzado: Simulación de Monte Carlo y Sharpe Ratio

Este informe documenta la simulación de Monte Carlo (1,000 iteraciones por escenario) y el análisis de Sharpe Ratio para evaluar la resiliencia y el comportamiento del riesgo de los modelos de Machine Learning (Calibración Isotónica, Umbral del 10%). Las cuotas utilizadas provienen de Bet365 para 1X2, Over/Under y Doble Oportunidad; BTTS y Home Clean Sheet se derivan sintéticamente mediante un modelo Poisson y deben interpretarse con cautela.

## 📊 Resultados de las Simulaciones

| Mercado | Gestión de Capital | Apuestas | Banca Cronológica | ROI Cronológico | Sharpe (Bet) | Sharpe (Anual) | Prob. Quiebra (MC) | Max Drawdown Medio (MC) | Intervalo Banca 95% (MC) | Intervalo ROI 95% (MC) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **1X2 Match Winner** | Flat Stake (1%) | 1584 | $5.20 | -6.28% | -0.0314 | -0.49 | **64.60%** | 89.45% | [$0.00, $1574.15] | [-28.81%, 3.62%] |
| **1X2 Match Winner** | Quarter Kelly | 1770 | $31.61 | -3.52% | -0.0280 | -0.47 | **30.10%** | 96.97% | [$0.00, $893.32] | [-23.63%, -0.27%] |
| **Portfolio Real Combinado** | Flat Stake (1%) | 1821 | $8.84 | -5.44% | -0.0299 | -0.50 | **63.20%** | 89.20% | [$0.00, $1567.69] | [-23.61%, 3.12%] |
| **Portfolio Real Combinado** | Quarter Kelly | 2098 | $20.36 | -2.58% | -0.0301 | -0.55 | **41.30%** | 97.79% | [$0.00, $728.03] | [-20.02%, -0.49%] |

---

## 🔬 Glosario y Definición de Métricas para la Defensa de Tesis

### A. Sharpe Ratio (Bet-by-Bet & Anualizado)
El **Sharpe Ratio** mide la rentabilidad ajustada al riesgo. En finanzas, indica cuánta rentabilidad excedente se obtiene por cada unidad de volatilidad.
* **Sharpe Ratio por Apuesta ($Sharpe_{\text{bet}}$):** Se calcula como el valor medio del retorno de las apuestas ($R_i = \text{Ganancia}/\text{Stake}$) dividido por su desviación estándar: $SR_{\text{bet}} = \frac{\mu_R}{\sigma_R}$.
* **Sharpe Ratio Anualizado:** Se anualiza multiplicando por la raíz cuadrada del número medio de apuestas colocadas por año: $SR_{\text{anual}} = SR_{\text{bet}} \times \sqrt{N_{\text{anual}}}$. Esto permite comparar directamente el portafolio deportivo con activos financieros tradicionales (donde un Sharpe > 1.0 se considera excelente, y > 2.0 es sobresaliente).

### B. Probabilidad de Quiebra (Ruin Probability)
Porcentaje de las 1,000 simulaciones aleatorias de Monte Carlo donde la banca cayó por debajo de **$10 USD** (1% del capital inicial), lo que representa la ruina práctica del inversor.

### C. Máximo Drawdown Medio (MC Max Drawdown)
La caída máxima de capital desde el pico más alto hasta el valle más bajo registrada en promedio a lo largo de las 1,000 simulaciones. Permite entender la racha de pérdidas que el inversor debe tolerar psicológicamente.

### D. Intervalos de Confianza del 95% (CI)
Indica los percentiles $2.5\%$ y $97.5\%$ de la banca y del ROI tras simular 1,000 caminos posibles. Se utiliza un **bootstrap** de las apuestas realmente colocadas en el backtest cronológico: se re-muestrean con reemplazo los pares (cuota, EV, resultado histórico). Esto conserva la distribución empírica conjunta —incluyendo el hecho de que las apuestas ganadoras suelen tener cuotas muy distintas a las perdedoras— y evita que el modelo sobrestime su propio edge.
