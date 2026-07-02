# 🚀 Plan de Implementaciones Futuras — Football Predictor & Betting Simulator

Este documento recopila de manera detallada las propuestas técnicas y metodológicas para evolucionar el proyecto actual (enfocado en la Premier League y predicciones estáticas) hacia un ecosistema dinámico de predicciones, multi-liga, en tiempo real y con soporte para arquitecturas complejas de apuestas como las combinadas.

---

## 🗺️ Mapa de Arquitectura Propuesta

A continuación se muestra cómo se transformaría el flujo de datos del proyecto para incorporar cuotas en tiempo real, múltiples ligas y el motor de apuestas combinadas:

```mermaid
flowchart TD
    subgraph Capa_de_Extraccion [Capa de Extracción (Scrapers & APIs)]
        A1[FBref Scraper (Histórico)] -->|Datos de Partidos y Estadísticas| B[Pipeline de Sanitización]
        A2[APIs de Cuotas (The Odds API / Pinnacle / Betfair)] -->|Cuotas en Vivo y Recientes| C[Motor de Comparación EV+]
        A3[Scrapers Multiliga] -->|LaLiga, Serie A, Bundesliga, etc.| B
    end

    subgraph Capa_de_Modelado [Capa de Modelado y Análisis]
        B -->|Data Sanitizada v8+| D[Modelos ML / Redes Neuronales]
        D -->|Probabilidades de Eventos (1X2, BTTS, O/U)| C
    end

    subgraph Capa_de_Decisión [Motor de Apuestas & Simulación]
        C -->|Cálculo de Valor (EV+)| E[Motor de Combinadas]
        E -->|Lógica de Parlays (Multi-partido / Mismo Partido)| F[Gestión de Banca (Criterio de Kelly)]
        F -->|Recomendación Final de Bet| G[Frontend - pl-web]
    end
```

---

## 📌 Eje 1: Obtención de Cuotas Reales de Mercado en Tiempo Real

Actualmente, el predictor calcula la probabilidad matemática de que ocurran ciertos eventos, pero flaquea en comparar estas probabilidades con las **cuotas reales que ofrecen las casas de apuestas (bookmakers) en tiempo real** antes del inicio del encuentro. Sin esto, no es posible calcular con precisión el **Valor Esperado Positivo (+EV)** para decidir si vale la pena o no realizar una apuesta.

### 🎯 Objetivos de la Implementación
1. **Integración con APIs de Cuotas:** Conectar el backend del proyecto a proveedores de cuotas actualizados (ej. *The Odds API*, *Pinnacle API*, o *Betfair API*) o desarrollar scrapers ligeros y rápidos en Python para casas de apuestas de referencia (ej. Bet365, Pinnacle).
2. **Cálculo Dinámico de Valor (+EV):** Implementar la fórmula de valor para cada mercado (1X2, Over/Under, BTTS):
   $$\text{EV} = (P_{\text{modelo}} \times \text{Cuota Real}) - 1$$
   *Solo se recomendará apostar si $\text{EV} > 0$ (o un umbral mínimo ajustado como $0.05$ o $5\%$).*
3. **Conversión y Comparación de Probabilidades:** Comparar la probabilidad implícita de las casas de apuestas con la probabilidad pura del modelo para detectar discrepancias y sesgos en el mercado de cuotas.

### 🛠️ Diseño Técnico Propuesto
* **Backend (`archive/pl-predictor/src/odds_client.py`):** Un cliente HTTP asíncrono para consumir las cuotas unas horas antes de los partidos. Almacenará las cuotas en una base de datos local (SQLite o similar) asociadas a cada fixture.
* **Pipeline Integrado (`predict_upcoming_bets.py`):**
  1. Descarga fixtures futuros.
  2. Descarga cuotas del mercado para esos fixtures.
  3. Ejecuta los modelos para obtener $P_{\text{modelo}}$.
  4. Calcula el valor esperado (+EV) y sugiere el stake óptimo usando el **Criterio de Kelly Fraccional**:
     $$f^* = \frac{p \cdot b - q}{b} \times \text{Fracción de Seguridad}$$
     *Donde $p$ es la probabilidad del modelo, $b$ son las cuotas netas (Cuota - 1), y $q = 1 - p$.*

---

## 📌 Eje 2: Expansión e Integración de Otras Ligas de Fútbol

El framework OSSEMN y CRISP-DM diseñado para la Premier League es altamente robusto, pero el rendimiento financiero de los modelos puede variar significativamente entre ligas (algunas ligas tienen comportamientos más predecibles, menos empates, o mayor asimetría que favorece al apostador).

### 🎯 Objetivos de la Implementación
1. **Adición de Ligas Clave:** Incorporar ligas europeas y americanas de alto volumen de datos:
   * **Ligas Top:** LaLiga (España), Serie A (Italia), Bundesliga (Alemania), Ligue 1 (Francia).
   * **Ligas Alternativas:** MLS (EE.UU.), Brasileirão (Brasil), EFL Championship (Segunda División Inglesa).
2. **Extracción y Modularización del Scraper:** Ajustar `pl-scraper` para que sea parametrizable por liga, descargando datos históricos y de jugadores desde FBref con el mismo nivel de detalle.
3. **Calibración de Métricas Globales (ELO):** Alinear la escala de ELO para que contemple partidos domésticos de cada liga y, opcionalmente, partidos internacionales (Champions/Europa League) para evitar distorsiones al cruzar datos.

### 🛠️ Diseño Técnico Propuesto
* **Estructura Multiliga en Base de Datos:** Estandarizar las rutas y nombres de archivos usando un identificador de liga (ej. `laliga`, `bundesliga`):
  * `archive/data/historical/laliga_match_features_v4.csv`
  * `archive/data/historical/bundesliga_match_features_v4.csv`
* **Modelos Específicos por Liga:** Entrenar instancias individuales de los clasificadores (RandomForest, XGBoost) por liga, ya que el estilo de juego (promedio de goles, tarjetas, localía) varía geográficamente.
* **Frontend Adaptable (`pl-web`):** Modificar la UI para agregar un selector desplegable de liga en el Dashboard, la sección de Backtesting y el Simulador de Inversiones, adaptando los escudos de los equipos y perfiles de árbitros dinámicamente.

---

## 📌 Eje 3: Implementación de Apuestas Combinadas (Parlays / Accumulators)

Las apuestas combinadas unen múltiples selecciones en una sola apuesta. Las cuotas de cada evento se multiplican entre sí, ofreciendo retornos financieros masivos a cambio de una reducción exponencial en la probabilidad de acierto.

### 🎯 Objetivos de la Implementación
1. **Apuestas Combinadas Multi-partido (Parlay Tradicional):** Combinar predicciones de alta confianza de diferentes partidos en la misma jornada (por ejemplo, victorias de 3 favoritos claros en Premier League y LaLiga).
2. **Apuestas Combinadas del Mismo Partido (Same-Game Parlay / Bet Builder):** Combinar múltiples mercados de un mismo partido (ej. *Local Gana* + *Ambos Anotan (BTTS)* + *Más de 2.5 Goles*).
3. **Modelado de Probabilidades Conjuntas:**
   * Para eventos independientes (diferentes partidos), la probabilidad conjunta se calcula fácilmente:
     $$P(A \cap B) = P(A) \times P(B)$$
   * Para eventos dependientes (mismo partido), no podemos multiplicar directamente debido a la alta correlación. Se requerirá implementar **modelos de probabilidad condicional** o estructurar la salida de la Red Neuronal para predecir la combinación directa de mercados.

### 🛠️ Lógica de Control de Riesgo y Banca
> [!WARNING]
> Las apuestas combinadas disparan la varianza (mayor riesgo de rachas de pérdidas prolongadas). Es imperativo implementar una gestión de banca estricta para mitigar la quiebra.

* **Fórmula de Cuota Combinada:**
  $$C_{\text{combinada}} = \prod_{i=1}^{n} C_i$$
* **Probabilidad Conjunta Estimada:**
  $$P_{\text{conjunta}} = \prod_{i=1}^{n} P_i \quad \text{(para partidos diferentes)}$$
* **Cálculo de EV+ Combinado:**
  $$\text{EV}_{\text{comb}} = (P_{\text{conjunta}} \times C_{\text{combinada}}) - 1$$
* **Ajuste de Stake (Kelly Fraccional Extremo):** Reducir el stake a una fracción pequeña (ej. $1/10$ o $1/20$ de Kelly) para proteger la banca ante la baja tasa de acierto implícita en combinadas de cuota alta.

---

## 📅 Hoja de Ruta Sugerida (Próximos Pasos)

| Fase | Tarea Principal | Entregable Técnico | Marco CRISP-DM / OSSEMN |
| :--- | :--- | :--- | :--- |
| **Fase 1** | **Integración de Cuotas Reales** | Cliente `odds_client.py` consumiendo API gratuita o web-scraped de cuotas. Comparativa de EV+ en el log/consola de predicciones. | *Data Collection & Preparation* |
| **Fase 2** | **Expansión a Otras Ligas** | Scrapers parametrizados para LaLiga y Serie A. Generación de datasets `historical_sanitized` por liga. | *Data Collection & Modeling* |
| **Fase 3** | **Lógica de Combinadas en Backend** | Algoritmo de selección de combinadas diarias basado en optimización de EV+ y minimización de varianza. | *Evaluation & Deployment* |
| **Fase 4** | **Actualización Web UI** | Integración en React de selectores de liga, visualización de cuotas reales en vivo y sugerencia de Parlays del día. | *Deployment & UI/UX* |

---
> [!NOTE]
> Este documento sirve como brújula técnica. Las decisiones sobre qué APIs de cuotas contratar o qué ligas priorizar se pueden consensuar a medida que se inicie cada fase de desarrollo.
