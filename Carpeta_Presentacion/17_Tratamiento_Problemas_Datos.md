# Guía Metodológica: Tratamiento de Problemas en los Datos (Defensa de Tesis)

Este documento detalla el abordaje científico y la implementación en código de cinco desafíos críticos de preparación de datos en el proyecto de **BetAnalytics**. Utiliza esta guía para justificar metodológicamente tus decisiones de diseño ante el jurado de tesis.

---

## 1. 🕳️ Varianza Cero (Features completamente concentrados)
* **Concepto Teórico:** Las variables con variabilidad nula o extremadamente baja no aportan información predictiva útil. Introducen redundancia y dimensionalidad innecesaria, ralentizando el aprendizaje de los modelos y aumentando el riesgo de sobreajuste.
* **Diagnóstico en BetAnalytics:** Columnas como `league` (siempre contiene "Premier League"), y columnas de texto libre o metadatos de administración como `notes` o `match_report`.
* **Tratamiento Aplicado:** Eliminación implacable antes del entrenamiento de modelos.
* **Línea de Código:** 
  * [sanitizer_pipeline.py](file:///d:/datascience/sanitizer_pipeline.py#L29-L32) ➔ `df.drop(columns=['league', 'notes', 'match_report'])`.

---

## 2. 🚨 Outliers (Atípicos Unidimensionales y Multidimensionales)
* **Concepto Teórico:** Observaciones que se distancian significativamente del comportamiento general del dataset. 
* **Justificación de Conservación en Deportes:** En la ciencia de datos tradicional, se acostumbra eliminar outliers utilizando IQR o Isolation Forest. Sin embargo, en el análisis deportivo de élite, **los valores extremos representan señales genuinas de rendimiento** (por ejemplo, el Elo Rating extremadamente alto del Manchester City, o partidos con un xG de 5.5). Si elimináramos estas filas, le estaríamos quitando a la IA la capacidad de aprender cómo juegan los equipos dominantes.
* **Tratamiento Aplicado:** Mantener el 100% de los registros observados para conservar la señal deportiva, pero proteger el entrenamiento matemático mediante:
  1. **Transformación Yeo-Johnson:** Para comprimir la distribución en colas largas y suavizar el peso relativo de los valores atípicos.
  2. **StandardScaler / PowerTransformer:** Para estandarizar los rangos de las variables y evitar que los outliers dominen el cálculo de gradientes en la Red Neuronal y la Regresión Logística.
* **Precaución Metodológica Crítica (Evitar MinMaxScaler):** 
  Al conservar outliers reales, es imperativo **no utilizar `MinMaxScaler` (normalización de 0 a 1)**. La fórmula de MinMaxScaler es:
  $$x_{norm} = \frac{x - x_{min}}{x_{max} - x_{min}}$$
  Si existe un outlier muy grande (por ejemplo, un xG máximo de $6.67$), el denominador se vuelve gigantesco. Como consecuencia, el 99% de tus datos normales (que oscilan entre $0.5$ y $2.5$) quedarán comprimidos en un rango diminuto (ej. entre $0.05$ y $0.20$), perdiendo casi toda su resolución y variabilidad para los modelos de ML. Al usar **Estandarización (StandardScaler)**, la división se hace por la desviación estándar ($\sigma$) en lugar del rango, lo que preserva la variabilidad interna de los datos comunes sin aplastarlos.
* **Líneas de Código:** 
  * [train_models.py](file:///d:/datascience/archive/pl-predictor/train_models.py#L41-L53) ➔ `ColumnTransformer` encapsulando `PowerTransformer` y `StandardScaler`.

---

## 3. 📐 Skewed Numerical Features (Variables Asimétricas)
* **Concepto Teórico:** Variables cuya distribución no es normal y exhibe una cola pronunciada a la derecha o a la izquierda (alta asimetría). Algoritmos paramétricos (como Redes Neuronales y Regresión Logística con Elastic Net) funcionan de forma óptima cuando los features se asemejan a una campana de Gauss.
* **Tratamiento en BetAnalytics:** Identificamos las variables con asimetría severa como cuotas del mercado (`B365H`, `B365D`, `B365A`), promedios de tarjetas del árbitro (`referee_avg_cards_history`) y promedios de goles esperados (`h_l5_xg`, `a_l5_xg`).
* **Justificación de la Selección de Yeo-Johnson:**
  * La transformación tradicional **Box-Cox** exige estrictamente datos estrictamente positivos ($x > 0$).
  * En fútbol, variables como los goles esperados (`home_xg`) o tarjetas históricas pueden registrar exactamente **$0.0$** (por ejemplo, un equipo que no genera situaciones o un partido sin tarjetas).
  * Por ello, implementamos la transformación **Yeo-Johnson**, la cual soporta matemáticamente valores nulos y cero sin generar indeterminaciones matemáticas.
* **Línea de Código:** 
  * [train_models.py](file:///d:/datascience/archive/pl-predictor/train_models.py#L43-L46) ➔ `('yeo_johnson', PowerTransformer(method='yeo-johnson', standardize=True))`.

---

## 4. 🔀 Multi-colinealidad (Correlación Extrema)
* **Concepto Teórico:** Corresponde a características independientes que están muy correlacionadas entre sí. **Ojo: No confundir con una alta correlación contra la variable target en un modelo supervisado, eso último es totalmente deseable** (representa poder predictivo).
* **¿Cómo se determina? (Diagnóstico):**
  1. **Matriz de Correlación:** Detecta colinealidad directa y obvia entre pares de variables (ej: $r > 0.85$).
  2. **Factor de Inflación de la Varianza (VIF):** Se utiliza para detectar la multicolinealidad más sutil, como combinaciones lineales no obvias de dos o más variables independientes. Los VIF comienzan en 1 y no tienen límite superior:
     * **VIF = 1:** Significa que no existe correlación entre esta variable independiente y cualquier otra.
     * **1 < VIF < 5:** Sugiere una correlación moderada, pero no sería necesario resolverla.
     * **VIF > 5:** Niveles críticos de multicolinealidad.
     
  > [!IMPORTANT]
  > **El criterio real frente al límite del VIF ("La multicolinealidad solo es un problema si es un problema"):**
  > Aunque los estadísticos consideran límites fijos de VIF de 5 o 10, esta es solo una regla general. Si un VIF es de 20, pero todos los coeficientes de las variables se estiman significativamente (errores estándar pequeños y p-valores $< 0.05$), la multicolinealidad **no es un problema práctico**. Por el contrario, si el VIF es de 4.9 (teóricamente seguro) pero las variables que teóricamente deberían ser significativas dejan de serlo al incluir ambas, la colinealidad es el problema real. La significación de las variables y la teoría del dominio de estudio superan a la regla rígida del VIF.

---

### ¿Cómo corregimos la multicolinealidad?
Depende del tipo de multicolinealidad que tengamos:

#### A. Para corregir la Multicolinealidad Estructural
Ocurre debido al diseño de los datos o combinaciones matemáticas de las variables (ej: incluir términos cuadráticos o interacciones).
* **Solución Aplicada:** Centrar los predictores (estandarizar restando la media).
* **¿Qué cambia cuando centramos los predictores?**
  * La interpretación de los coeficientes de regresión sigue siendo la misma (representan el cambio medio en el target dado un cambio de 1 unidad en la variable independiente).
  * Los VIF del modelo con predictores centrados disminuyen a niveles seguros ($< 5$).
  * La precisión de las estimaciones aumenta (disminuyen los errores estándar de los coeficientes de regresión).
  * Pueden variar los signos de los coeficientes de regresión y la significación estadística ($p$-valor) al eliminarse el ruido colineal.
* **¿Qué NO cambia cuando centramos los predictores?**
  * La bondad de ajuste del modelo (el $R^2$ ajustado y múltiple se mantiene idéntico).
  * Las predicciones del modelo y el error estándar de los residuos (RSE).
* **Código del Proyecto:** En [train_models.py](file:///d:/datascience/archive/pl-predictor/train_models.py#L41-L50) implementamos este centrado/estandarización dentro del pipeline usando `StandardScaler` y `PowerTransformer(standardize=True)`.

#### B. Para corregir la Multicolinealidad de los Datos
Ocurre por la naturaleza y recolección propia de la muestra.
* **Soluciones Posibles:**
  1. **Eliminar variables independientes altamente correlacionadas** (la solución más directa).
  2. **Combinar linealmente las variables** (ej: mediante un PCA para crear nuevos predictores independientes).
  3. **Realizar un análisis diseñado para variables altamente correlacionadas** (ej: regresión de Mínimos Cuadrados Parciales - PLS).
  4. **Realizar una regresión que pueda manejar la multicolinealidad** (ej: LASSO y regresión de Ridge).
* **Código del Proyecto (Aplicación y Defensa Metodológica):**
  * **Vulnerabilidad de Estimadores Tradicionales:** Los estimadores tradicionales de regresión (como Variables Instrumentales - IV, Método Generalizado de Momentos - GMM, Máxima Verosimilitud clásica como Probit, Logit y Logit Multinomial) asumen independencia y sufren inflación extrema de errores estándar ante multicolinealidad.
  * **Solución 1 (Eliminación):** Eliminamos las cuotas de Pinnacle (`PSH`, `PSD`, `PSA`) en [sanitizer_pipeline.py](file:///d:/datascience/sanitizer_pipeline.py#L59-L61) por su redundancia del 99% con Bet365.
  * **Solución 4 (Regresión Penalizada):** En lugar de eliminar arbitrariamente variables colineales complejas (como remates totales vs remates al arco), donde es difícil decidir cuál se queda y cuál se va, implementamos la **Regresión Logística con Elastic Net (Lasso + Ridge)** en [train_models.py](file:///d:/datascience/archive/pl-predictor/train_models.py#L107). La penalización sopesa cuánta información nueva aporta una variable frente al costo de inflación de la varianza que introduce, automatizando y objetivando la selección de predictores.
* **Líneas de Código:** 
  * *Eliminación:* [sanitizer_pipeline.py](file:///d:/datascience/sanitizer_pipeline.py#L59-L61) ➔ `df.drop(columns=['PSH', 'PSD', 'PSA'])`.
  * *Centrado:* [train_models.py](file:///d:/datascience/archive/pl-predictor/train_models.py#L41-L50).
  * *Elastic Net:* [train_models.py](file:///d:/datascience/archive/pl-predictor/train_models.py#L107-L110).

---

## 5. 💧 Information Leakage (Fuga de Información)
* **Concepto Teórico:** Ocurre cuando se introduce información del futuro o variables que solo se conocen *después* del evento para predecir el resultado del mismo. Esto da como resultado modelos con un rendimiento falsamente perfecto en validación que fallan por completo en producción en vivo.
* **Abordaje en BetAnalytics:**

### A. Fugas Post-Silbato (Variables dentro del partido)
* **Diagnóstico:** Variables del partido actual como la cantidad final de tarjetas (`total_cards`), faltas comúnmente registradas (`home_match_fouls`) o el marcador final (`score`) no se conocen en el minuto 0 (momento en que se ejecuta la apuesta).
* **Tratamiento:** Eliminación del set de características de entrenamiento.
* **Línea de Código:** 
  * [sanitizer_pipeline.py](file:///d:/datascience/sanitizer_pipeline.py#L55-L57) ➔ `df.drop(columns=['score', 'home_match_fouls', 'away_match_fouls', 'total_cards'])`.

### B. Fuga Temporal en Validación Cruzada (Cross-Validation Leakage)
* **Diagnóstico:** Si utilizáramos una validación cruzada aleatoria estándar (K-Fold normal), la IA entrenaría con partidos del año 2024 para predecir un partido jugado en el año 2018. Esto violaría la causalidad temporal y causaría fuga de información de series de tiempo (cambios en plantillas de equipos, tendencias tácticas a lo largo de los años, etc.).
* **Tratamiento:** Implementación obligatoria de **TimeSeriesSplit (Validación Temporal)**. La muestra se divide en ventanas continuas ordenadas por fecha cronológica. El modelo solo predice el "Futuro" (bloque de testeo) habiendo aprendido estrictamente del "Pasado" (bloque de entrenamiento).
* **Línea de Código:** 
  * [train_models.py](file:///d:/datascience/archive/pl-predictor/train_models.py#L115) ➔ `tscv = TimeSeriesSplit(n_splits=5)`.

---

## 6. 🏷️ Justificación: Variables Categóricas y Test Chi-cuadrado ($\chi^2$)
* **El Problema en la Tesis:** En ciencia de datos convencional, se utiliza el test de independencia de Chi-cuadrado ($\chi^2$) para seleccionar y evaluar la relevancia de variables categóricas frente al target. Sin embargo, en BetAnalytics **los features de entrenamiento son casi al 100% cuantitativos continuos**, por lo que la prueba de Chi-cuadrado no es aplicable a la gran mayoría de las variables.
* **Feature Engineering Aplicado (Evitar codificaciones ineficientes):**
  1. **Nombres de Equipos (`home_team`, `away_team`):** En lugar de aplicar *One-Hot Encoding* (lo cual crearía más de 40 columnas dispersas y provocaría sobreajuste a nombres de equipos cuya fortaleza fluctúa con los años), los transformamos en la variable cuantitativa continua **Elo Rating (`home_elo`, `away_elo`)** para capturar dinámicamente la fuerza deportiva real.
  2. **Árbitros (`referee`):** En lugar de tratar el nombre del árbitro como categoría de alta cardinalidad, lo reemplazamos por su **promedio histórico de tarjetas mostradas (`referee_avg_cards_history`)**, obteniendo una variable continua con significado predictivo directo.
  3. **Estadio/Sede (`venue`):** La sede de localía queda implícitamente representada en la división de los features en `home_*` y `away_*`, haciendo innecesario codificarla.
* **Criterio de Evaluación Alternativo:** 
  Al ser variables continuas, evaluamos sus relaciones usando **Coeficientes de Correlación de Pearson/Spearman** (para feature vs feature) y pruebas de diferencia de medias como **ANOVA o T-Student** (para feature continuo vs target categórico), además de las métricas de importancia de características (Feature Importance) de los clasificadores de árbol.
* **Excepción donde aplica Chi-cuadrado:** La única variable categórica binaria en el set es **`is_derby`** (0 o 1). Podría cruzarse frente a `result_1x2` en una tabla de contingencia de $2 \times 3$ usando Chi-cuadrado, pero al representar un solo predictor, no justifica basar el preprocesamiento general en este test.

---

## 7. 🎯 Análisis y Construcción del Target (Labels de Clasificación)

El análisis del target es crucial para definir la viabilidad del proyecto supervisado. En BetAnalytics, estructuramos este estudio bajo las siguientes directrices teóricas y empíricas:

* **¿Qué queremos hacer? (Objetivo Predictivo):**
  Queremos predecir la probabilidad de ocurrencia de distintos eventos deportivos y de mercado de apuestas para partidos futuros de la Premier League. Para ello, construimos **8 targets categóricos** en [train_models.py:L17-L29](file:///d:/datascience/archive/pl-predictor/train_models.py#L17-L29):
  1. `target_1x2`: Resultado final (Gana Local = 2, Empate = 1, Gana Visitante = 0).
  2. `target_dc_1X` / `target_dc_X2`: Doble oportunidad (Local o Empate / Visitante o Empate).
  3. `target_over_2_5_goals` / `target_under_2_5_goals`: Total de goles mayor o menor/igual a 2.5.
  4. `target_btts` / `target_btts_no`: Ambos equipos anotan / No anotan.
  5. `target_home_clean_sheet`: Valla invicta local.

* **¿Tenemos el label? ¿Cuánto tenemos? (Disponibilidad):**
  Sí, contamos con el 100% de los labels para la data de entrenamiento, calculados a partir de los goles reales anotados (`home_goals` y `away_goals`).
  * **Tamaño de muestra etiquetada:** Contamos con **3,389 partidos históricos con etiquetas reales** (temporadas 2017/18 a 2024/25) tras excluir los partidos futuros programados que aún no se han disputado (donde `game_id == '0'`).

* **Si no tenemos datos, ¿los podemos comprar o conseguir?:**
  No es necesario realizar ninguna compra de datos. La base de datos histórica completa de resultados y cuotas es pública y de libre acceso, y ya está consolidada en el dataset.

* **Revisión de Desbalance de Clases (Class Imbalance):**
  Auditamos la distribución de las clases sobre los 3,389 partidos reales de entrenamiento para identificar asimetrías severas:
  
  | Variable Target | Clase 0 (Freq. / %) | Clase 1 (Freq. / %) | Clase 2 (Freq. / %) | Diagnóstico de Desbalance |
  | :--- | :---: | :---: | :---: | :--- |
  | **target_1x2** (Multiclase) | 1,106 (32.6%) | 787 (23.2%) | 1,496 (44.1%) | Sesgo natural de localía en fútbol. No requiere balanceo sintético ya que representa la probabilidad real del deporte. |
  | **target_dc_1X** (Local o Empate)| 1,106 (32.6%) | 2,283 (67.4%) | - | Desbalance moderado esperable (cubre 2 de 3 resultados posibles). |
  | **target_over_2_5_goals** | 1,544 (45.6%) | 1,845 (54.4%) | - | **Distribución ideal** (Casi 50/50). |
  | **target_btts** (Ambos Anotan) | 1,596 (47.1%) | 1,793 (52.9%) | - | **Distribución ideal** (Casi 50/50). |
  | **target_home_clean_sheet** | 2,379 (70.2%) | 1,010 (29.8%) | - | Desbalance moderado natural del deporte (sólo un 30% de los partidos terminan con el visitante en cero goles). |

  *Justificación Metodológica para la Tesis (Descarte de Rebalanceo de Clases):*
  Se determinó que **no corresponde aplicar ninguna técnica de rebalanceo (ni submuestreo ni sobremuestreo)** para este proyecto de inversión y apuestas:
  1. **¿Por qué NO usar submuestreo (Undersampling)?:** Consiste en eliminar registros reales de la clase mayoritaria (ej: borrar partidos ganados de local o partidos sin valla invicta). Al contar con una muestra histórica acotada de 3,389 partidos, eliminar observaciones reales representaría un desperdicio de señal predictiva y restaría robustez general al entrenamiento del modelo.
  2. **¿Por qué NO usar sobremuestreo (Oversampling / SMOTE)?:** Al duplicar partidos o inventarlos sintéticamente combinando características (SMOTE), se destruye la **calibración de probabilidad** del clasificador. En mercados financieros y apuestas, no solo importa predecir la etiqueta final, sino estimar con total precisión la probabilidad del evento para compararla con la cuota del mercado y calcular el Valor Esperado (EV). Alterar las frecuencias reales de ocurrencia de la Premier League anularía esta capacidad.
  3. **Cómo lo resuelven los algoritmos:** Al ser un desbalance muy moderado (máximo $70\% - 30\%$, a diferencia de desbalances severos de $95\% - 5\%$ clásicos de fraudes), los clasificadores lo gestionan de manera nativa:
     * *Árboles de Decisión (Random Forest / XGBoost):* Evalúan de forma secuencial la ganancia de información (entropía/impureza de Gini) y toleran desbalances leves sin perder precisión.
     * *Modelos Paramétricos (Regresión Logística / Red Neuronal):* Optimizan la entropía cruzada (Log-Loss), la cual calibra de forma natural la probabilidad de salida en base a la tasa de ocurrencia real ("base rate") presente en el fútbol.

* **Revisión de la Temporalidad de los Labels:**
  El fútbol es un fenómeno altamente temporal (las plantillas, directores técnicos y rendimientos varían año a año). 
  * Por ello, los labels están indexados estrictamente en orden cronológico por la variable `date`.
  * La validación del modelo respeta esta temporalidad mediante la técnica **TimeSeriesSplit**, asegurando que los bloques de evaluación siempre correspondan a fechas posteriores a los de entrenamiento, evitando cualquier fuga de información temporal (Data Leakage temporal).

---

## 8. 🔄 Transformación de Datos y Feature Engineering ("Sea su propio jefe")

En machine learning, la preparación de datos exige decidir cómo codificar y transformar cada tipo de variable. A continuación, justificamos cómo se aplican los conceptos de tus diapositivas al código de **BetAnalytics**:

### A. Variables Categóricas Nominales (One-Hot, Dummy Encoding, etc.)
* **Enfoque de tus diapositivas:** One-Hot Encoder, Dummy encoding, etc.
* **Aplicación en el Proyecto:** Decidimos **no aplicar One-Hot ni Dummy Encoding a variables de alta cardinalidad** (como `home_team`, `away_team` y `referee`). En su lugar, hicimos una transformación de negocio (Feature Engineering) para convertirlas en métricas cuantitativas continuas (Elo Rating y promedio de tarjetas del árbitro). Esto previene el sobreajuste y la dispersión dimensional de crear más de 40 columnas artificiales.
* **Excepción:** La única variable nominal en el set es **`is_derby`** (clásico regional), que ya se encuentra en formato **Dummy/Binario (0 o 1)** de origen y no requiere codificación adicional.

### B. Variables Categóricas Ordinales (Ordinal, Target Encoding, etc.)
* **Enfoque de tus diapositivas:** Ordinal encoding, Target encoding, etc.
* **Aplicación en el Proyecto:** No contamos con variables categóricas ordinales nativas de texto (como "Bajo/Medio/Alto") en el set predictivo, por lo que no fue necesario aplicar Ordinal o Target Encoding en el pipeline activo.

### C. Variables Numéricas (Tratamiento de Asimetría y Escalamiento)
* **Enfoque de tus diapositivas:**
  * **Distribuciones Asimétricas:** Logaritmo $\text{Log}(X_i+k)$, Box-Cox, Ext. Yeo-Johnson.
  * **Normalización y Escalamiento:** Min Max Scaler, Estandarización.
* **Aplicación en el Proyecto:**
  * **Asimetría:** Aplicamos la transformación de potencia **Yeo-Johnson** en [train_models.py:L45](file:///d:/datascience/archive/pl-predictor/train_models.py#L45). Se prefirió sobre Box-Cox debido a que variables de rendimiento deportivo (como xG o tarjetas) pueden registrar valores de exactamente **$0.0$** (donde Box-Cox falla al exigir datos estrictamente positivos).
  * **Escalamiento:** Descartamos `MinMaxScaler` debido a la presencia de outliers genuinos (evitando el "efecto compresión" que aplasta los datos normales). Implementamos **Estandarización (StandardScaler)** para centrar las variables con media $\mu = 0$ y desviación $\sigma = 1$, estabilizando la física del descenso de gradientes en la Red Neuronal y Regresión Logística.

### D. Feature Engineering ("Sea su propio jefe" - Algoritmos y Heurísticas Propios)
* **Enfoque de tus diapositivas:** WOE & IV, Catboost Encoding, heurísticas propias (ej: RFM, Métricas de distancia).
* **Aplicación en el Proyecto:** En lugar de basarnos en encodings tradicionales supervisados (como WOE o Catboost), tomamos el rol de *"ser nuestro propio jefe"* diseñando **métricas y algoritmos ad-hoc** con fuerte sustento en el dominio del fútbol profesional:
  1. **EWMA de Rendimiento Reciente (Goles Esperados Ponderados):** Diseñamos un promedio móvil ponderado exponencialmente (EWMA) sobre los últimos 5 partidos (`h_l5_xg`, `a_l5_xg`, etc.) en [sanitizer_pipeline.py:L88-L92](file:///d:/datascience/sanitizer_pipeline.py#L88-L92). Esto da más peso a los partidos recientes, capturando mejor la "racha" o momento dinámico del equipo.
  2. **Diferencial de Descanso Físico (`home_rest`, `away_rest`):** Cálculo del número de días transcurridos desde el último partido oficial para medir la fatiga.
  3. **Presión de Descenso (`relegation_pressure`):** Algoritmo propio que mide la cercanía y urgencia matemática de un equipo respecto a la zona de descenso en la tabla de posiciones en tiempo real.

---

## 9. 📋 Matriz Resumen: Columnas Afectadas, Problemas y Tratamientos

La siguiente tabla resume de forma consolidada el censo completo de las variables afectadas en el preprocesamiento de datos y cómo fueron corregidas en tu código:

| Categoría del Problema | Variable(s) Afectada(s) | Diagnóstico / Impacto | Tratamiento Técnico Aplicado | Archivo y Línea de Código |
| :--- | :--- | :--- | :--- | :--- |
| **Varianza Cero** | `league` | Constante ("Premier League") en toda la muestra. | Eliminación física de la columna. | [sanitizer_pipeline.py:L31](file:///d:/datascience/sanitizer_pipeline.py#L31) |
| **Varianza Casi Cero / Ruido** | `notes` | Concentrado al 99.97% en un único valor ("0"). | Eliminación física de la columna. | [sanitizer_pipeline.py:L31](file:///d:/datascience/sanitizer_pipeline.py#L31) |
| **Identificadores Únicos / Ruido**| `match_report` | URLs de reportes. Cardinalidad única por fila. | Eliminación física de la columna. | [sanitizer_pipeline.py:L31](file:///d:/datascience/sanitizer_pipeline.py#L31) |
| **Fuga de Información** | `score`, `home_match_fouls`, `away_match_fouls`, `total_cards` | Variables post-partido no disponibles antes del pitazo inicial. | Eliminación física de la columna. | [sanitizer_pipeline.py:L56](file:///d:/datascience/sanitizer_pipeline.py#L56) |
| **Multicolinealidad** | `PSH`, `PSD`, `PSA` | Cuotas de Pinnacle correlacionadas al $r \approx 0.99$ con Bet365. | Selección de representante (Eliminar Pinnacle). | [sanitizer_pipeline.py:L60](file:///d:/datascience/sanitizer_pipeline.py#L60) |
| **Datos Faltantes (MCAR)** | `attendance` | Un único registro nulo por olvido de registro. | Eliminación del registro (fila `dropna`). | [sanitizer_pipeline.py:L36](file:///d:/datascience/sanitizer_pipeline.py#L36) |
| **Formato e Integridad** | `game_id` | Lectura flotante por defecto de Pandas (ej: `0.0`). | Forzado estricto a String y saneamiento de sufijo `.0`. | [sanitizer_pipeline.py:L23-L27](file:///d:/datascience/sanitizer_pipeline.py#L23-L27) |
| **Formato Temporal** | `date` | Lectura de fechas en formato texto/string. | Parseo estricto a DateTime y ordenamiento. | [sanitizer_pipeline.py:L40](file:///d:/datascience/sanitizer_pipeline.py#L40) |
| **Datos Faltantes (MAR)** | `home_xg`, `away_xg`, `h_l5_xg`, `a_l5_xg`, `h_l5_xga`, `a_l5_xga`, `B365H`, `B365D`, `B365A` | Concentración de nulos en temporadas viejas o inicios de liga. | Imputación KNN ($K=5$, peso por distancia inversa) en validación. | [train_models.py:L44,L48](file:///d:/datascience/archive/pl-predictor/train_models.py#L44) |
| **Outliers Genuinos** | `home_xg`, `away_xg`, `h_l5_xg`, `a_l5_xg`, `home_elo`, `away_elo` | Rendimientos extremos pero válidos de equipos de élite. | Conservación física + transformación Yeo-Johnson y StandardScaler. | [train_models.py:L41-L50](file:///d:/datascience/archive/pl-predictor/train_models.py#L41-L50) |
| **Asimetría (Skewed)** | `away_xg`, `referee_avg_cards_history`, `B365H`, `B365D`, `B365A`, `h_l5_fls`, `a_l5_fls`, `h_l5_xg`... | Distribuciones con sesgo y colas asimétricas pronunciadas. | PowerTransformer Yeo-Johnson (soporta ceros). | [train_models.py:L37,L45](file:///d:/datascience/archive/pl-predictor/train_models.py#L37) |
| **Fuga Temporal (Leakage)** | Todos los features del dataset. | Causalidad del tiempo en series temporales. | División temporal obligatoria vía `TimeSeriesSplit(n_splits=5)`. | [train_models.py:L115](file:///d:/datascience/archive/pl-predictor/train_models.py#L115) |

