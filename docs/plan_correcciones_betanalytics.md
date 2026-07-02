# Plan de Correcciones y Robustez — BetAnalytics

> Documento de aterrizaje del plan de correcciones solicitado por el usuario.  
> Aquí se registran los hallazgos del análisis tipo Data Science, las fases de corrección y el estado de cada una, para no perderse ningún punto dada la magnitud del cambio.

---

## 1. Contexto y objetivo

El proyecto ha incorporado recientemente lógicas nuevas muy importantes:

- **Cuotas reales de múltiples casas de apuestas** (Bet365, Pinnacle, Betfair, etc.) y scraping desde BetExplorer.
- **Apuestas combinadas**: dobles/triples multi-partido y Same-Game Parlays (SGP) con descuento de correlación.
- **Simulaciones de inversión** con múltiples estrategias de capital (flat, Kelly, fracciones de Kelly).

El usuario quiere saber si los ROI/resultados que se muestran **son reales** o producto de:

- Data leakage / look-ahead bias.
- Overfitting o evaluación optimista.
- Sobreestimación de cuotas (defaults, cuotas fabricadas, cuotas sintéticas mostradas como reales).
- Bugs de lógica en SGP, EV, Kelly o simulaciones.
- Fragilidad en scraping.

**Objetivo**: auditar, corregir y documentar cada punto crítico, y dejar las simulaciones con supuestos realistas y bien separados (reales vs. sintéticos).

---

## 2. Hallazgos principales del análisis

| # | Hallazgo | Severidad | Archivos afectados |
|---|----------|-----------|-------------------|
| 2.1 | `compute_elo_map` y `build_team_last5` usaban todo el DataFrame sin corte temporal: **look-ahead bias en features**. | Crítica | `archive/pl-predictor/src/api.py`, `backtester.py`, `upcoming.py` |
| 2.2 | La fórmula de SGP usaba probabilidad conjunta sin correlación ni precio real de cuota, inflando el EV. | Crítica | `archive/pl-predictor/src/parlay_engine.py` |
| 2.3 | `odds_source` default era `max`, pero cuando no había scraper caía a cuotas mock sin etiquetar. | Alta | `archive/pl-predictor/src/odds_client.py`, `db.py`, frontend |
| 2.4 | `odds_scraper_free.py` tenía scraping frágil: parseo por índice, sin mapeo de nombres de equipos, promedio mal calculado. | Alta | `archive/pl-predictor/src/odds_scraper_free.py` |
| 2.5 | En el frontend se fabricaban cuotas si faltaban, el edge estaba invertido (`1/odd - prob` en lugar de `prob - 1/odd`), y las queries no se invalidaban. | Alta | `pl-web/src/lib/api.ts`, `Dashboard.tsx`, componentes |
| 2.6 | Las simulaciones de Monte Carlo barajaban resultados históricos (permutación) en lugar de muestrear binomialmente según la probabilidad estimada; además Kelly usaba `wagered` global en lugar del wagered de cada simulación. | Alta | `Simulacion_Inversion/simulacion_montecarlo.py` |
| 2.7 | Mercados BTTS y Home Clean Sheet se generaban con cuotas **sintéticas** (modelo Poisson) pero se reportaban junto a cuotas reales sin distinción clara. | Media | `Simulacion_Inversion/simular_estrategias_apuestas.py` |
| 2.8 | La calibración isotónica usaba `cv=2` por defecto, lo que genera leakage interno dentro de la calibración. | Media | `Simulacion_Inversion/simular_estrategias_apuestas.py` |
| 2.9 | Meta-labeling (si existe) debe validarse con splits temporales anidados para no filtrar información del futuro. | Media | Pendiente de verificación |

---

## 3. Fases de corrección

### Fase 1 — Eliminar look-ahead bias en features (✅ hecho)

- [x] Agregar parámetro `cutoff_date` a `compute_elo_map` y `build_team_last5`.
- [x] Recomputar Elo/form **por fecha de partido** en el backtester.
- [x] Pasar `match_date` desde `upcoming.py`.
- [x] Hacer que `evaluate_market_result` devuelva `None` para mercados desconocidos y que los callers lo salten.

### Fase 2 — Cuotas: etiquetado, defaults y scraping (✅ hecho)

- [x] Agregar columna `odds_is_simulated` en SQLite y propagarla a la API.
- [x] Cuotas mock etiquetadas como `is_simulated=True` y poblar `max_odds` / `all_providers`.
- [x] Default de `odds_source` cambiado a `average`.
- [x] Scraper BetExplorer con mapeo de nombres de equipos, parseo por encabezados, promedio real y `is_simulated=False`.

### Fase 3 — Frontend: edge real, no fabricar cuotas, invalidar queries (✅ hecho)

- [x] Quitar fabricación de cuotas en `api.ts`.
- [x] Corregir fórmula de edge: `edge = prob - 1/odd`.
- [x] Tolerancia flotante en `findProviderForOdd`.
- [x] Reducir `staleTime` a 2 min.
- [x] Invalidar queries dependientes tras actualizar cuotas.
- [x] Mostrar banner cuando las cuotas son simuladas.
- [x] Manejar odds/edge/provider nulos en componentes.

### Fase 4 — Simulaciones realistas (✅ hecho)

- [x] **4.1 Calibración isotónica**: cambiar a `cv='prefit'` para calibrar solo sobre el fold de calibración.
- [x] **4.2 Monte Carlo**: reemplazar permutación histórica por **bootstrap** de las apuestas realmente colocadas, conservando la distribución conjunta (cuota, EV, resultado). Esto evita que el modelo sobrestime su propio edge.
- [x] **4.3 Mercados sintéticos**: separar explícitamente BTTS/HCS generados por Poisson, agregar columna `Fuente_Cuotas` en el reporte y agregar el portafolio `portfolio_real` (solo cuotas reales).
- [x] **4.4 Meta-labeling**: verificar validación walk-forward en `simular_meta_decision.py`; agregar tests de separación temporal y usar DataFrame con nombres de features en `predict_proba`.

### Fase 5 — Tests y documentación

- [x] **5.1 Tests unitarios críticos**: SGP, temporalidad, EV, mercado desconocido.
- [ ] **5.2 Documentación**: actualizar `bitacora_cambios_odds_y_parlays.md`, `implementaciones_odds_y_parlays.md` y `README.md` con los cambios, supuestos y limitaciones.

---

## 4. Criterios de aceptación

1. Los tests unitarios existentes siguen pasando y se agregan tests para Monte Carlo y mercados sintéticos.
2. El frontend compila sin errores.
3. Los scripts de Python compilan (`python -m py_compile`) y, donde sea posible, se ejecutan sobre datos de prueba.
4. Los ROI mostrados distingen claramente:
   - Cuotas reales (Bet365 / máximo / promedio).
   - Cuotas simuladas/mock.
   - Cuotas sintéticas derivadas (BTTS/HCS vía Poisson).
5. El informe de Monte Carlo refleja varianza realista con intervalos de confianza por muestreo binomial.
6. La documentación explica por qué los resultados anteriores podían ser optimistas y qué cambios los hicieron robustos.

---

## 6. Hallazgos más importantes tras la corrección

1. **Monte Carlo original era irrealista**: la permutación de resultados históricos, combinada con usar las probabilidades del modelo para muestrear, producía bancas de miles de millones de dólares. El bootstrap sobre apuestas realmente colocadas muestra resultados coherentes con el backtest cronológico (predominantemente negativos).

2. **Las apuestas ganadoras tienen cuotas más bajas que las perdedoras**: en 1X2, las victorias tienen cuota media ~3.8 mientras que las derrotas ~5.5. Muestrear con una probabilidad uniforme ignoraba este sesgo y sobrestimaba la rentabilidad.

3. **BTTS y Home Clean Sheet no son cuotas reales**: se derivan de un modelo Poisson a partir de 1X2 y O/U. Ahora se etiquetan como `Sintético (Poisson/Arbitraje)` y existe un `portfolio_real` separado.

4. **El meta-labeling muestra resultados positivos pero requieren más validación**: la estrategía dual obtiene ~6.6% ROI. Si bien usa walk-forward, los resultados positivos merecen validación con ventanas de test más largas y análisis de robustez ante cambios de régimen.

## 7. Archivos de tests añadidos/actualizados

- `archive/pl-predictor/tests/test_corrections.py` — SGP, temporalidad, EV, mercado desconocido.
- `Simulacion_Inversion/test_montecarlo_bootstrap.py` — bootstrap realista de Monte Carlo.
- `Simulacion_Inversion/test_meta_labeling_temporal.py` — separación temporal del meta-modelo.

## 8. Próximos pasos recomendados

1. Ejecutar y documentar los resultados corregidos de Monte Carlo en presentaciones/informes.
2. Realizar un análisis de sensibilidad del meta-labeling con diferentes umbrales y ventanas walk-forward.
3. Considerar eliminar o restringir mercados sintéticos en cualquier presentación que afirme "cuotas reales".
4. Actualizar `docs/bitacora_cambios_odds_y_parlays.md` y `README.md` con estos hallazgos.
