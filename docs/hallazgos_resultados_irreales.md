# Hallazgos: Por qué los resultados anteriores no eran realistas

> Resumen ejecutivo de la auditoría Data Science a las simulaciones de inversión y al motor de cuotas/combinadas.

---

## 1. Monte Carlo: permutación histórica + probabilidades del modelo

### Problema
`Simulacion_Inversion/simulacion_montecarlo.py` originalmente:
1. Extraía las apuestas elegibles del backtest cronológico.
2. **Barajaba** el orden de esas apuestas 1,000 veces.
3. Usaba los **resultados históricos reales** de cada apuesta en el nuevo orden.

Esto es problemático porque:
- Para *Flat Stake* el orden no importa, así que la "simulación" no aportaba varianza real.
- Para *Kelly* el orden sí importa, pero el método reutilizaba los targets reales, no la incertidumbre del modelo.
- Peor aún, cuando se cambió a muestreo binomial con `p = (EV + 1) / odd`, se usaron las probabilidades del modelo para muestrear. Como el modelo sobreestima su propio edge, las simulaciones arrojaban bancas de **miles de millones de dólares**.

### Corrección
Se reemplazó por un **bootstrap** de las apuestas **realmente colocadas** en el backtest cronológico:
- Se re-muestrean con reemplazo los pares `(cuota, EV, resultado histórico)`.
- Se conserva la distribución conjunta real, incluyendo el hecho de que las apuestas ganadoras suelen tener cuotas muy diferentes a las perdedoras.
- Se recalcula el stake en cada camino según la estrategia (Flat o Quarter Kelly).

### Resultado después de la corrección
Los intervalos de confianza del 95% ahora son coherentes con el backtest cronológico (predominantemente negativos), y la probabilidad de ruina es alta (~30-65% según el escenario).

---

## 2. Perfil de cuotas: ganadores vs. perdedores

En el mercado 1X2, las apuestas colocadas mostraban:

| Métrica | Valor |
|---------|-------|
| Win rate empírico | 24.75% |
| Cuota media de las victorias | 3.79 |
| Cuota media de las derrotas | 5.47 |
| Cuota media global | 5.05 |

**Implicación**: aunque el win rate es cercano al 25%, las victorias ocurren en apuestas de cuota baja y las derrotas en cuota alta. Cualquier simulación que asuma una probabilidad de éxito homogénea sobreestimará fuertemente el ROI.

---

## 3. Mercados sintéticos presentados como reales

`Simulacion_Inversion/simular_estrategias_apuestas.py` genera cuotas para BTTS, BTTS-No y Home Clean Sheet mediante un modelo Poisson a partir de las cuotas 1X2 y Over/Under de Bet365.

### Problema
Estas cuotas **no provienen de ningún bookmaker real**. Presentarlas junto a cuotas Bet365 sin distinción puede inducir a pensar que todo el portfolio usa datos reales.

### Corrección
- Se añadió la columna `Fuente_Cuotas` en `reporte_simulacion_calibrada.csv`.
- Se creó el mercado `portfolio_real` que solo incluye 1X2, Over/Under y Double Chance (este último también sintético pero derivado por arbitraje).
- Se actualizaron los gráficos y los textos del informe para distinguir "Real (Bet365)" vs "Sintético (Poisson/Arbitraje)".

---

## 4. Calibración isotónica con leakage interno

El uso de `CalibratedClassifierCV(..., cv=2)` por defecto hace una validación cruzada interna, lo que permite que el calibrador vea datos que luego se usan para evaluar. Eso mejora artificialmente la calibración reportada.

### Corrección
Se usa `cv='prefit'`:
1. Entrenar modelo base en el 80% del fold de entrenamiento.
2. Calibrar únicamente sobre el 20% restante.
3. Predecir sobre el fold de test.

Esto elimina el leakage dentro de la propia calibración.

---

## 5. Meta-labeling

`Simulacion_Inversion/simular_meta_decision.py` ya usaba validación walk-forward (entrena meta-modelo en splits anteriores, evalúa en el actual), por lo que no requirió una corrección estructural.

### Advertencia
Los resultados del sistema dual muestran ~6.6% ROI, mientras que la línea base es negativa. Aunque la validación es temporalmente correcta, resultados positivos en una única walk-forward pueden deberse a:
- Régimen favorable en el periodo evaluado.
- Overfitting del meta-modelo a la distribución del pasado reciente.
- Leakage residual en features como `home_elo`/`away_elo` si no se recomputan por fecha.

Se recomienda validar con ventanas de test más largas, múltiples configuraciones de `edge_threshold` y análisis de estabilidad del meta-modelo.

---

## 6. Recomendaciones para reportar resultados

1. **Nunca reportar cuotas sintéticas como reales.** Siempre incluir una columna o nota de fuente.
2. **Reportar el ROI cronológico como métrica principal**, no el ROI de Monte Carlo.
3. **Usar Monte Carlo solo para ilustrar varianza/ruina**, no para proyectar ganancias esperadas.
4. **Incluir el drawdown máximo y la probabilidad de ruina** junto al ROI.
5. **Validar cualquier resultado positivo con al menos una ventana de test independiente** que el modelo no haya visto en ninguna etapa (entrenamiento, calibración, meta-labeling).

---

## Archivos clave modificados

- `Simulacion_Inversion/simulacion_montecarlo.py`
- `Simulacion_Inversion/simular_estrategias_apuestas.py`
- `Simulacion_Inversion/simular_meta_decision.py`
- `Simulacion_Inversion/test_montecarlo_bootstrap.py`
- `Simulacion_Inversion/test_meta_labeling_temporal.py`
- `docs/plan_correcciones_betanalytics.md`
- `docs/bitacora_cambios_odds_y_parlays.md`
