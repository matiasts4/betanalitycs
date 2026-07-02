# Bitácora de Cambios: Implementación de Cuotas Reales y Motor de Parlays/SGP

Este documento detalla **cada uno de los archivos modificados, creados y testeados** durante el desarrollo de la arquitectura de cuotas reales (históricas/en vivo) y el motor de apuestas combinadas (Dobles/SGP). Úsalo como guía para la revisión exhaustiva del código.

---

## 📂 Archivos Creados (Nuevos)

### 1. [parlay_engine.py](file:///d:/betanalitycs/archive/pl-predictor/src/parlay_engine.py)
* **Propósito:** El motor matemático central de las apuestas combinadas.
* **Detalle de Implementación:**
  * **`build_multi_match_parlays(odds_source)`**: Agrupa partidos independientes con EV+ real y genera combinaciones Dobles (2 patas) y Triples (3 patas).
  * **`build_same_game_parlays(odds_source)`**: Agrupa mercados del mismo partido (Victoria Local, Over/Under 2.5, BTTS, Clean Sheet) y aplica los coeficientes de co-ocurrencia (`SGP_CORRELATIONS`) para obtener la probabilidad conjunta corregida y la cuota estimada con descuento de correlación.
  * **`build_parlays()`**: Orquestador principal que consolida y devuelve ambas listas.

### 2. [odds_scraper_free.py](file:///d:/betanalitycs/archive/pl-predictor/src/odds_scraper_free.py)
* **Propósito:** Scraper en tiempo real para eventos futuros desde BetExplorer.
* **Detalle de Implementación:**
  * Implementa **SeleniumBase en modo anti-detección (UC)** para eludir las protecciones de Cloudflare.
  * Navega el fixture de próximos partidos, entra a cada partido y pulsa en las pestañas de cuotas (`1X2`, `O/U`, `BTTS`).
  * Consolida y extrae las cuotas de **11 bookmakers** (incluyendo Bet365, Pinnacle, Betfair Exchange, 888sport, Unibet, Bwin, etc.).
  * Calcula el promedio (`Avg_*`) y el máximo absoluto (`Max_*`), y los estructura en un diccionario detallado (`all_providers_odds`).

### 3. [historical_odds_merger.py](file:///d:/betanalitycs/archive/pl-predictor/src/historical_odds_merger.py)
* **Propósito:** Script de saneamiento histórico.
* **Detalle de Implementación:**
  * Integra y consolida las cuotas de mercado máximas (`Max_Home`, `Max_Draw`, `Max_Away`, `Max_Over2.5`, `Max_Under2.5`) a partir de archivos CSV históricos en `historical_sanitized_v11.csv` para la simulación de Line Shopping.

---

## 🛠️ Archivos Modificados (Existentes)

### 4. [db.py](file:///d:/betanalitycs/archive/pl-predictor/src/db.py)
* **Propósito:** Capa de persistencia en SQLite.
* **Cambios Realizados:**
  * Modificada la estructura de la tabla `upcoming_matches` para admitir cuotas máximas e individuales por columnas (`odds_max_home`, `odds_max_draw`, etc.) y el mapa JSON de todos los proveedores en `all_providers_odds`.
  * Actualizadas las funciones de escritura `save_upcoming_matches()` y lectura `get_upcoming_matches()` para que realicen la inserción y mapeo simétrico de estas cuotas.

### 5. [api.py](file:///d:/betanalitycs/archive/pl-predictor/src/api.py)
* **Propósito:** Capa API REST en Flask.
* **Cambios Realizados:**
  * Añadida la ruta **POST** `/api/matches/upcoming/update` para disparar el scraper en vivo en segundo plano y persistir los cambios.
  * Añadida la ruta **GET** `/api/matches/parlays` para exponer las combinadas sugeridas (`doubles`, `trebles` y `same_game`) al frontend.

### 6. [api.ts](file:///d:/betanalitycs/pl-web/src/lib/api.ts)
* **Propósito:** Interfaz de datos y consultas en TypeScript (React).
* **Cambios Realizados:**
  * Añadidas interfaces de tipado para combinadas (`APIParlaySelection`, `APIParlayItem`, `APIParlaysResponse`).
  * Rediseñada la función `mapAPIUpcomingToMockMatch` para calcular el EV real en base a la cuota máxima cargada de SQLite y detectar qué bookmaker específico ofrece esa cuota máxima (usando `findProviderForOdd()`).
  * Agregado el hook react-query `useAPIParlays(oddsSource)` y el mutador de actualización.

### 7. [Dashboard.tsx](file:///d:/betanalitycs/pl-web/src/pages/Dashboard.tsx)
* **Propósito:** Panel de control web principal.
* **Cambios Realizados:**
  * Añadido el estado `parlayTab` para alternar entre combinadas tradicionales ("Multi-Partido") y SGPs ("Mismo Partido").
  * Diseñado el bloque visual responsivo para SGPs, mostrando los mercados cruzados, cuotas descontadas reales, EV%, Kelly y la casa de apuestas recomendada.

### 8. [MatchCard.tsx](file:///d:/betanalitycs/pl-web/src/components/MatchCard.tsx)
* **Propósito:** Componente de tarjeta de partido.
* **Cambios Realizados:**
  * Modificado el banner de **Mejor Pick** en próximos partidos para que imprima dinámicamente el proveedor (ej. `Mejor Pick (Pinnacle)` o `Mejor Pick (Betfair Exchange)`), corroborando el uso real de cuotas multi-proveedor.

---

## 🧪 Archivos de Test y Scratch (Persistidos)

* **[scratch/run_parlay_backtest.py](file:///C:/Users/PC/.gemini/antigravity-ide/brain/47aaf45e-dbea-4325-a4fa-b8db42641466/scratch/run_parlay_backtest.py):** Simulador histórico de 1,140 partidos que calcula y compara la rentabilidad de las tres estrategias bajo apuestas planas ($10 fijas) y compuestas (Kelly).
* **[scratch/test_sgp_calculations.py](file:///C:/Users/PC/.gemini/antigravity-ide/brain/47aaf45e-dbea-4325-a4fa-b8db42641466/scratch/test_sgp_calculations.py):** Test unitario que valida matemáticamente el descuento de correlación, EV y Kelly de las Same-Game Parlays.
* **[scratch/test_parlay_engine.py](file:///C:/Users/PC/.gemini/antigravity-ide/brain/47aaf45e-dbea-4325-a4fa-b8db42641466/scratch/test_parlay_engine.py):** Test unitario que valida la multiplicación de cuotas y la independencia de dobles/triples.
* **[scratch/calculate_joint_ratios.py](file:///C:/Users/PC/.gemini/antigravity-ide/brain/47aaf45e-dbea-4325-a4fa-b8db42641466/scratch/calculate_joint_ratios.py):** Script de extracción empírica de correlaciones a partir de los 3,420 partidos históricos.
* **[scratch/test_scraper_e2e.py](file:///C:/Users/PC/.gemini/antigravity-ide/brain/47aaf45e-dbea-4325-a4fa-b8db42641466/scratch/test_scraper_e2e.py):** Test de scraping completo de detalles en BetExplorer.

---

## 🔍 Correcciones de Robustez Aplicadas (Post-Análisis Data Science)

### 9. Look-Ahead Bias en Features
* **Archivos:** `archive/pl-predictor/src/api.py`, `backtester.py`, `upcoming.py`
* **Cambio:** Se agregó un `cutoff_date` a `compute_elo_map` y `build_team_last5` para que Elo y forma se calculen solo con partidos anteriores a la fecha de predicción. El backtester recompute estas features por fecha de partido.

### 10. Fórmula SGP Corregida
* **Archivo:** `archive/pl-predictor/src/parlay_engine.py`
* **Cambio:** Se extrajo `calculate_sgp()` y se corrige para usar la probabilidad conjunta con correlación y el precio real de cuota SGP. El default de `odds_source` pasó a `average`.

### 11. Cuotas Mock Etiquetadas y Scraper Robustecido
* **Archivos:** `archive/pl-predictor/src/db.py`, `odds_client.py`, `odds_scraper_free.py`
* **Cambio:** Se añadió `odds_is_simulated` a SQLite; las cuotas mock se etiquetan como simuladas; el scraper de BetExplorer usa mapeo de nombres de equipos, parseo por encabezados y promedio real.

### 12. Frontend: Edge, Cuotas y Simulated Banner
* **Archivos:** `pl-web/src/lib/api.ts`, `Dashboard.tsx`, `MatchCard.tsx`, `OddsButton.tsx`
* **Cambio:** Se eliminó la fabricación de cuotas, se corrigió la fórmula de edge (`prob - 1/odd`), se añadió tolerancia flotante, invalidación de queries y banner de cuotas simuladas.

### 13. Simulaciones Realistas
* **Archivos:** `Simulacion_Inversion/simulacion_montecarlo.py`, `simular_estrategias_apuestas.py`, `simular_meta_decision.py`
* **Cambios clave:**
  * Monte Carlo pasa de permutación histórica a **bootstrap** de apuestas realmente colocadas.
  * Se separan mercados sintéticos (`BTTS`, `HCS`, `DC`) con columna `Fuente_Cuotas`.
  * Se añade `portfolio_real` usando solo cuotas reales de Bet365.
  * Calibración isotónica usa `cv='prefit'` sobre modelo entrenado en 80% y calibrado en 20%.
  * Meta-labeling validado con walk-forward y tests de separación temporal.

### 14. Tests
* **Archivos:** `archive/pl-predictor/tests/test_corrections.py`, `Simulacion_Inversion/test_montecarlo_bootstrap.py`, `Simulacion_Inversion/test_meta_labeling_temporal.py`
* **Cobertura:** SGP, temporalidad, EV, mercados desconocidos, bootstrap Monte Carlo y separación temporal del meta-modelo.
