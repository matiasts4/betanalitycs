# Análisis de Backtesting Histórico: Simples vs. Combinadas vs. Same-Game Parlays (2023-2026)

Este documento detalla el análisis comparativo del rendimiento del predictor bajo dos esquemas de gestión de capital: **Apuestas Planas (Fixed Staking)** y **Apuestas Compuestas (Kelly Compounding)** en un histórico de **1,140 partidos** de la Premier League.

---

## 📊 Resultados de Simulación Comparativa (Capital Inicial: $1,000.00)

### 1. Simulación bajo Cuotas Máximas (Line Shopping)

| Estrategia | Gestión de Capital | Banca Final / Ganancia | Yield / ROI Real | Apuestas Totales | Win Rate | Max Drawdown |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Simples** | Plana (Fija $10) | **+$882.60** | **`7.28%`** | 1,212 | $45.71\%$ | N/A |
| **Simples** | Compuesta (Kelly) | **$20,662.00** | **`1966.20%`** | 1,212 | $45.71\%$ | $71.19\%$ |
| **Combinadas Dobles** | Plana (Fija $10) | **+$1,201.87** | **`52.71%`** | 228 | $17.98\%$ | N/A |
| **Combinadas Dobles** | Compuesta (Kelly) | **$3,234.73** | **`223.47%`** | 228 | $17.98\%$ | $52.63\%$ |
| **Same-Game Parlays** | Plana (Fija $10) | **+$159.81** | **`11.41%`** | 140 | $30.00\%$ | N/A |
| **Same-Game Parlays** | Compuesta (Kelly) | **$1,033.44** | **`3.34%`** | 140 | $30.00\%$ | $7.07\%$ |

---

### 2. Simulación bajo Cuotas Promedio (Average / Bet365)

| Estrategia | Gestión de Capital | Banca Final / Ganancia | Yield / ROI Real | Apuestas Totales | Win Rate | Max Drawdown |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Simples** | Plana (Fija $10) | **+$592.60** | **`6.09%`** | 973 | $45.12\%$ | N/A |
| **Simples** | Compuesta (Kelly) | **$4,132.48** | **`313.25%`** | 973 | $45.12\%$ | $80.36\%$ |
| **Combinadas Dobles** | Plana (Fija $10) | **+$1,125.34** | **`49.36%`** | 228 | $19.30\%$ | N/A |
| **Combinadas Dobles** | Compuesta (Kelly) | **$2,826.84** | **`182.68%`** | 228 | $19.30\%$ | $49.20\%$ |
| **Same-Game Parlays** | Plana (Fija $10) | **-$22.59** | **`-2.11%`** | 107 | $26.17\%$ | N/A |
| **Same-Game Parlays** | Compuesta (Kelly) | **$1,004.93** | **`0.49%`** | 107 | $26.17\%$ | $6.01\%$ |

---

## 💡 Análisis de los Resultados y Aclaración de Métricas

### 1. ¿Por qué el ROI Compuesto parece tan alto? (Compounding Kelly)
El retorno exponencial de las apuestas simples (`+1966.20%` en Kelly) se debe exclusivamente al **interés compuesto**. Al usar el criterio de Kelly fraccional, la cantidad apostada se adapta dinámicamente al tamaño de la banca actual. Si la banca sube a $10,000, una apuesta del $5\%$ equivale a $500; si la apuesta se acierta, el crecimiento es exponencial.
* **El Control Plana (Yield Real):** Cuando eliminamos el interés compuesto y evaluamos apuestas fijas de $10 (Flat Staking), el ROI de las apuestas simples baja a un **`7.28%`** (cuotas máximas) y **`6.09%`** (cuotas promedio). Esto se alinea perfectamente con los rendimientos históricos esperados del modelo.

### 2. El Espectacular Yield de las Combinadas Dobles (`52.71%` ROI)
El motor de combinadas dobles muestra un ROI plano de **`52.71%`** con cuotas máximas. Esto ocurre porque somos extremadamente selectivos:
* Solo se realizan **228 combinadas en total** (frente a 1,212 simples) durante las 3 temporadas.
* Al elegir exclusivamente las **top 2 dobles con mayor EV de cada jornada**, el filtro de calidad es altísimo, lo que dispara el Yield.
* *Nota de banca:* Su banca Kelly final ($3,234.73) es menor a la de simples ($20,662.00) porque, al tener 5 veces menos apuestas, el interés compuesto ha tenido menos oportunidades/iteraciones para multiplicarse.

### 3. La Vital Importancia del "Line Shopping" en Same-Game Parlays
* Con cuotas máximas, las SGPs (Local + Over 2.5) obtienen un Yield plano positivo del **`+11.41%`**.
* Con cuotas promedio, el rendimiento cae a **`-2.11%`** (pérdidas).
* **Conclusión:** Las casas de apuestas aplican un margen tan severo a las combinadas del mismo partido (Crear Apuesta) que **solo es rentable jugarlas si se busca la cuota máxima absoluta del mercado**.
