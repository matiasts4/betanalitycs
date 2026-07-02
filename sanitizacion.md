# Checklist de Sanitización y Preprocesamiento de Datos

Dedicado a la metodología formal de limpieza, depuración y encuadre analítico.

## 1. Analítico Exploratorio Inicial (EDA)
- [ ] Ejecutar reporte crudo inicial (`df.info()`, `df.describe()`).
- [ ] Buscar observaciones duplicadas, valores nulos y calcular la varianza y desviación típica.
- [ ] Evaluar relaciones entre variables usando la matriz de correlaciones, Scatterplots (gráficos de dispersión) y la prueba Chi-cuadrado específicamente para features categóricos.
- [ ] Estudiar las distribuciones: visualizar mediante Boxplots e Histogramas, evaluar la modalidad de la distribución (unimodal, bimodal, etc.) y emplear el Test de Kolmogorov-Smirnov.

## 2. Limpieza de Datos Incorrectos
- [ ] **Homogeneización de formato:** Utilizar diccionarios, NumPy, Pandas y el manejo de `datetime` para solucionar cuando el código se cae o existen inconsistencias.
- [ ] **Detección Fuera de Rango (OOR):** Chequear umbrales teóricos máximos o mínimos (ej: evitar edad negativa). Tratarlos como valores nulos o bien afrontarlos con imputación iterativa (LGBM, KNN).
- [ ] **Limpieza de Ruido:** 
  - Para ruido en imágenes: recurrir a modelos como DDPM, DGN o filtros puros (Gaussianos/Blur).
  - Para ruido en audio: procesarlo mediante filtros de reducción espectral o Wiener.

## 3. Resolución de Datos Inútiles (Depuración Estructural)
- [ ] **Destrucción de variables constantes:** Eliminar implacablemente cualquier feature con varianza cero (completamente concentrados).
- [ ] **Solventar Multicolinealidad:** Eliminar copias frente a alta correlación entre features (quedándose con un representante) o aplicar vías de Reducción Dimensional.
- [ ] **Cortar Fugas de Información (Leakage):** Diagnosticar si tu modelo es sospechosamente bueno revisando la "importancia de las features" (Feature importance). Dropear entonces las variables filtradas desde el target, o bien "jugar con los tiempos (skip) del modelo" entre X e Y.

## 4. Tratamiento de Valores Faltantes (Missing Values)
- [ ] **Para MCAR (Completamente Random):** 
  - Imputar empleando la Media, Mediana o Moda. 
  - Alternativa: eliminar los registros si no impactan estructuralmente.
- [ ] **Para MAR (Random condicionado):** 
  - Realizar imputación estructurada basándose en los algoritmos de K-NN o Máxima Verosimilitud.
- [ ] **Para MNAR (No Random, sistemático):** 
  - Levantar marcas temporales o Dummies Ad-Hoc.
  - Evaluar proactivamente la opción resoluta principal: **"Encontrar más data"**.

## 5. Outliers y Comportamiento Atípico
- [ ] Filtrado unidimensional utilizando Boxplots e IQR.
- [ ] Filtrado multidimensional aislando anomalías profundas mediante algoritmos como Isolation Forests o ECOD.
- [ ] **Toma de decisiones:** Entender que no es del todo cierto que los outliers son inútiles; de hecho, en muchos casos es **exactamente lo que estás buscando**. Conservarlos es un paso válido, pero tener extremado cuidado con las normalizaciones posteriores (ej: `min_max_scaler`).

## 6. Curado de Distribución (Transformación Numérica)
- [ ] Tratar los features numéricos de alta asimetría (skewed).
- [ ] Suavizado e inducido normal mediante transformaciones como el Logaritmo `Log(Xi+k)`, `Box-Cox` (limitado a distribuciones positivas) y/o `Yeo-Johnson` (excelente porque soporta valores nulos y negativos).

## 7. Feature Engineering y Setup de Algoritmos (Transformación)
- [ ] **Categóricas Nominales:** Aplicar transformaciones nativas puras como el `One-hot Encoder` y `Dummy encoding` (o escoger entre "... 15 más"). 
- [ ] **Categóricas Ordinales:** Recurrir a herramientas orgánicas orientadas como el `Ordinal Encoding` o `Target Encoding`.
- [ ] **En Supervisión Avanzada:** Transformación hacia Weights of Evidence (`WOE & IV`) o `Catboost Encoding`.
- [ ] **Ser su propio Jefe (Heurísticas Propias):** Inyectar algoritmos o reglas ad-hoc construyendo:
  - **Métricas RFM** (Recency, Frequency, Monetary).
  - **Métricas de distancia** (Euclidiana, Manhattan, Coseno, Hamming, Jaccard).
- [ ] **Normalización Total:** Acomodar la escala ejecutando el `Min Max Scaler` o bien la pura `Estandarización`.
