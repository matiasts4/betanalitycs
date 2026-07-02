import pandas as pd
import os

def main():
    csv_path = "models/mirrors/mirror_comparison_results.csv"
    md_path = "d:/datascience/Carpeta_Presentacion/23_Estudio_Desbalance_Resampling.md"
    
    if not os.path.exists(csv_path):
        print(f"❌ Error: No se encontró {csv_path}")
        return
        
    df = pd.read_csv(csv_path)
    
    # 1. Definir la plantilla limpia original de 23_Estudio_Desbalance_Resampling.md
    template = """# Estudio Comparativo: Tratamiento del Desbalanceo de Clases mediante Modelos Espejo (BetAnalytics)

Este informe documenta el estudio avanzado de remuestreo (resampling) realizado para evaluar el impacto del desbalanceo de clases en la predicción de mercados deportivos de la Premier League ($N = 3,389$ partidos).

Sirve como material de apoyo metodológico oficial para tu defensa de tesis, respondiendo a la inquietud académica de evaluar técnicas de sobremuestreo y submuestreo frente a la línea base limpia del proyecto.

---

## 1. ⚖️ El Problema del Desbalanceo en Pronósticos Deportivos

El desbalanceo de clases ocurre cuando una de las categorías del target está subrepresentada. En la literatura de machine learning, se suele clasificar el desbalanceo en tres niveles:
* **Leve/Moderado:** La clase minoritaria representa entre el $15\%$ y el $40\%$ del dataset.
* **Severo:** La clase minoritaria representa menos del $15\%$ (típico en detección de fraudes, fallas de maquinaria o enfermedades raras).

### Distribución de Clases en BetAnalytics:
Al analizar nuestros 8 mercados objetivos bajo el conjunto de entrenamiento histórico, observamos las siguientes proporciones:

* **Double Chance 1X (Home or Draw):** $67.36\\%$ (1) vs. $32.64\\%$ (0). *Desbalanceo leve/moderado.*
* **Home Clean Sheet (Valla Invicta Local):** $70.20\\%$ (0 - Recibe Gol) vs. $29.80\\%$ (1 - Valla Invicta). *Desbalanceo leve/moderado.*
* **1X2 Resultado (Multiclase):** Local $44.14\\%$, Visitante $32.64\\%$, Empate $23.22\\%$. *Distribución natural de fútbol.*
* **Over/Under 2.5 Goles & Ambos Anotan (BTTS):** Distribuciones muy cercanas al $50/50$ (prácticamente balanceadas).

A diferencia de otros dominios (como fraude financiero), en fútbol las clases minoritarias representan proporciones altas ($23\\% - 33\\%$). Este estudio evalúa si alterar artificialmente estas proporciones naturales mejora la capacidad predictiva.

---

## 2. 🎛️ Fundamentos de las Técnicas de Resampling Evaluadas

Entrenamos **7 configuraciones espejo** de nuestro sistema de modelos predictivos. Cada configuración representa un enfoque metodológico diferente:

### A. Sobremuestreo (Oversampling)
1. **Random Oversampling (ROS):** Reclona de manera aleatoria observaciones de la clase minoritaria hasta igualar la clase mayoritaria.
   * *Riesgo:* Puede inducir a un sobreajuste (overfitting) severo, ya que el modelo entrena con registros duplicados exactos.
2. **SMOTE (Synthetic Minority Over-sampling Technique):** Genera nuevas muestras sintéticas interpolando linealmente entre los $k$ vecinos más cercanos de la clase minoritaria en el espacio de características.
   * *Ventaja:* Introduce variabilidad en lugar de solo copiar.
   * *Riesgo:* Si las clases están solapadas (común en fútbol), puede generar muestras sintéticas ruidosas en zonas de la clase contraria.

### B. Submuestreo (Undersampling)
3. **Random Undersampling (RUS):** Elimina aleatoriamente observaciones de la clase mayoritaria hasta equilibrar las proporciones.
   * *Riesgo:* Descarta una enorme cantidad de partidos históricos valiosos, reduciendo el tamaño de la muestra de entrenamiento.
4. **Tomek Links:** Detecta pares de puntos de clases opuestas que son sus vecinos más cercanos entre sí (enlaces de Tomek). Elimina el punto que pertenece a la clase mayoritaria.
   * *Efecto:* No equilibra las clases al 50/50, sino que **limpia la frontera de decisión** y elimina el ruido en las zonas de solapamiento.
5. **Cluster Centroids:** Agrupa las muestras de la clase mayoritaria mediante un algoritmo KMeans (donde el número de clusters es igual al tamaño de la clase minoritaria) y sustituye los datos originales por los centroides de dichos clusters.
6. **NearMiss (Versión 1):** Selecciona las muestras de la clase mayoritaria que tienen la menor distancia promedio a los $k$ vecinos más cercanos de la clase minoritaria.

---

## 3. 🛡️ Rigor Metodológico: Prevención de Leakage en Resampling

Un error común y grave en ciencia de datos es aplicar técnicas de balanceo (como SMOTE) a **todo el dataset** antes de realizar la validación cruzada. Esto genera **fuga de datos (data leakage)** porque el conjunto de prueba termina conteniendo muestras sintéticas creadas a partir de información que debería ser invisible (el conjunto de validación).

### Nuestra Implementación:
Utilizamos la librería `imbalanced-learn` y encapsulamos los samplers en pipelines dinámicos (`imblearn.pipeline.Pipeline`).
* Durante la validación cruzada temporal (`TimeSeriesSplit(n_splits=5)`), el balanceo se aplica **estrictamente sobre los pliegues de entrenamiento (train folds)**.
* Los pliegues de validación/prueba (test folds) permanecen **100% inalterados e intactos**, preservando las proporciones reales del fútbol para medir la generalización real en producción.

---

## 4. 📊 Resultados Numéricos Comparativos

A continuación se presentan las tablas de rendimiento del mejor modelo entrenado para cada mercado clave bajo las 7 configuraciones espejo:

### A. Comparativa de Exactitud (Accuracy)
| Configuración Espejo | Resultado 1X2 (Multiclase) | Doble Oportunidad 1X | Valla Invicta Local (CS) | Ambos Anotan (BTTS) |
| :--- | :---: | :---: | :---: | :---: |
| **Original (Línea Base)** | **0.5298** | **0.7071** | **0.7064** | **0.5323** |
| **Random Oversampling (ROS)** | 0.4926 | 0.6812 | 0.6663 | 0.5273 |
| **SMOTE (Oversampling)** | 0.4883 | 0.6784 | 0.6440 | 0.5206 |
| **Random Undersampling (RUS)** | 0.4876 | 0.6624 | 0.5702 | 0.5241 |
| **Tomek Links (Undersampling)** | 0.5238 | 0.7053 | 0.6943 | 0.5099 |
| **Cluster Centroids (Undersampling)** | 0.4894 | 0.6606 | 0.5709 | 0.5184 |
| **NearMiss (Undersampling)** | 0.4514 | 0.6160 | 0.5106 | 0.5181 |

### B. Comparativa de F1-Score
| Configuración Espejo | Resultado 1X2 (Multiclase) | Doble Oportunidad 1X | Valla Invicta Local (CS) | Ambos Anotan (BTTS) |
| :--- | :---: | :---: | :---: | :---: |
| **Original (Línea Base)** | 0.4631 | **0.8056** | 0.2896 | **0.6090** |
| **Random Oversampling (ROS)** | 0.4859 | 0.7726 | 0.4329 | 0.5763 |
| **SMOTE (Oversampling)** | 0.4897 | 0.7647 | 0.4308 | 0.5847 |
| **Random Undersampling (RUS)** | 0.4900 | 0.7301 | 0.4346 | 0.5799 |
| **Tomek Links (Undersampling)** | 0.4792 | 0.8004 | 0.3360 | 0.5037 |
| **Cluster Centroids (Undersampling)** | 0.4879 | 0.7341 | 0.4286 | 0.5735 |
| **NearMiss (Undersampling)** | 0.4575 | 0.6816 | **0.4373** | 0.5738 |

---

## 5. 📉 Visualización del Impacto del Resampling (Multimétrica)

El gráfico general a continuación contrasta el rendimiento de las 7 configuraciones espejo a través de tres dimensiones críticas (Exactitud, F1-Score y ROC-AUC) para los mercados analizados:

![Comparativa General de Resampling](file:///d:/datascience/Carpeta_Presentacion/24_Comparativa_Multimetrica_Resampling.png)

A continuación, para un análisis granular y exhaustivo de cómo responde **cada modelo clasificador individual** (Logistic Regression, Random Forest, HistGradientBoosting, XGBoost, y Neural Network) a cada una de las técnicas de remuestreo, se presentan las curvas de rendimiento cruzadas en cuadrículas de 2x4 que cubren **todos los mercados (targets)** y **las tres métricas analizadas**:

### A. Comparativa Completa de Exactitud (Accuracy)
El siguiente gráfico muestra la exactitud de todos los modelos a través de todos los métodos de resampling en las 8 variables predictivas:

![Comparativa Completa de Accuracy](file:///d:/datascience/Carpeta_Presentacion/27_Comparativa_Completa_Accuracy.png)

### B. Comparativa Completa de F1-Score
El siguiente gráfico muestra el F1-Score de todos los modelos a través de todos los métodos de resampling en las 8 variables predictivas:

![Comparativa Completa de F1-Score](file:///d:/datascience/Carpeta_Presentacion/28_Comparativa_Completa_F1.png)

### C. Comparativa Completa de ROC-AUC
El siguiente gráfico muestra el ROC-AUC de todos los modelos a través de todos los métodos de resampling en las 8 variables predictivas. Para el mercado multiclase `1X2 (Match Winner)`, se detalla estéticamente como *N/A (No Aplicable)* dado que esta métrica está definida estrictamente para clasificaciones binarias:

![Comparativa Completa de ROC-AUC](file:///d:/datascience/Carpeta_Presentacion/29_Comparativa_Completa_ROC_AUC.png)

---

## 6. 🧠 Conclusiones y Defensa Científica (¿Por qué no usar Resampling?)

Estos resultados proveen una justificación matemática sólida y elegante que te permitirá defender metodológicamente tu diseño ante el jurado de tesis:

### A. La Caída Generalizada de la Exactitud (Accuracy)
El remuestreo (tanto over como undersampling) **redujo la exactitud general en todos los mercados**:
* En **Doble Oportunidad 1X**, la exactitud cayó de **70.71%** (Original) a **67.84%** (SMOTE) y **61.60%** (NearMiss).
* En **Valla Invicta Local**, la exactitud se desplomó de **70.64%** (Original) a **66.63%** (ROS) y **51.06%** (NearMiss).
* *Explicación Científica:* El fútbol es un deporte con un **alto solapamiento de características** (los datos de partidos donde un equipo empata o pierde de local son muy similares a donde gana). Al balancear las clases al 50/50 de forma artificial, forzamos a los algoritmos a expandir excesivamente el límite de decisión de la clase minoritaria. Esto provoca que el modelo realice muchas más predicciones positivas de las que corresponden, disparando los **Falsos Positivos (Error Tipo I)** y arruinando el Accuracy.

### B. El Dilema del F1-Score vs. Exactitud en Valla Invicta
* **El Fenómeno:** En `Home Clean Sheet` (Valla Invicta, desbalance 70/30), la línea base tiene un F1-score bajo ($0.2896$) pero una exactitud muy alta ($70.64\%$). Las técnicas de resampling (como NearMiss) suben el F1-Score a un máximo de **0.4373**, pero reducen la exactitud general al **51.06%** (casi equivalente al azar).
* *Por qué ocurre:* La línea base original predice con cautela la valla invicta local (ya que estadísticamente ocurre solo el 29.8% de las veces). Al remuestrear, obligamos al modelo a volverse "agresivo" prediciendo vallas invictas. Aunque esto eleva la recuperación (Recall) de la clase minoritaria (y por ende el F1-Score), la tasa de Falsos Positivos se dispara, reduciendo la exactitud a niveles inaceptables.

### C. La Destrucción de la Calibración de Probabilidades (Negocio y Apuestas)
La conclusión de negocio más fuerte para tu tesis es sobre el **sistema de inversión**:
* Para colocar apuestas con **Valor Esperado positivo ($EV+$)**, dependemos de que las probabilidades estimadas por el modelo ($\hat{p}$) estén perfectamente calibradas con el mundo real:
  $$EV = (\hat{p} \times \text{Cuota}) - 1$$
* Si el modelo estima que la probabilidad de una Valla Invicta Local es del $50\%$ (debido al balanceo artificial del dataset de entrenamiento), cuando la probabilidad real histórica bajo esas condiciones de variables es de solo $30\%$, el sistema calculará un EV+ erróneo y **apostará dinero real en eventos perdedores**, destruyendo la rentabilidad financiera.
* *Recomendación:* **Se debe conservar la Línea Base Original (Sin Resampling)**, ya que preserva las frecuencias y probabilidades reales del deporte, permitiendo una correcta calibración probabilística indispensable para la gestión de capital y valor esperado.
"""
    
    # 2. Mapeos para la tabla gigante
    config_map = {
        "main": "Original (Línea Base)",
        "oversampling_random": "ROS (Oversampling)",
        "oversampling_smote": "SMOTE (Oversampling)",
        "undersampling_random": "RUS (Undersampling)",
        "undersampling_tomek": "Tomek Links (RUS)",
        "undersampling_centroids": "Cluster Centroids (RUS)",
        "undersampling_nearmiss": "NearMiss (RUS)"
    }
    
    target_map = {
        "1X2 (Match Winner)": "1X2 (Match Winner)",
        "Double Chance 1X (Home or Draw)": "Doble Oportunidad 1X",
        "Double Chance X2 (Away or Draw)": "Doble Oportunidad X2",
        "Over 2.5 Goals": "Over 2.5 Goles",
        "Under 2.5 Goals": "Under 2.5 Goles",
        "BTTS (Both Teams To Score)": "BTTS (Ambos Anotan)",
        "BTTS - No": "BTTS - No",
        "Home Clean Sheet": "Valla Invicta Local"
    }
    
    model_map = {
        "Logistic Regression (Elastic Net)": "Logistic Regression (Elastic Net)",
        "Random Forest": "Random Forest",
        "HistGradientBoosting (Early Stopping)": "HistGradientBoosting (Early Stopping)",
        "XGBoost (L1/L2 Regularized)": "XGBoost",
        "Neural Network (Dropout)": "Neural Network (MLP)"
    }
    
    df_mapped = df.copy()
    df_mapped['mirror_config'] = df_mapped['mirror_config'].map(config_map)
    df_mapped['target_name'] = df_mapped['target_name'].map(target_map)
    df_mapped['model_name'] = df_mapped['model_name'].map(model_map)
    
    df_mapped['target_name'] = pd.Categorical(df_mapped['target_name'], categories=list(target_map.values()), ordered=True)
    df_mapped['mirror_config'] = pd.Categorical(df_mapped['mirror_config'], categories=list(config_map.values()), ordered=True)
    df_mapped['model_name'] = pd.Categorical(df_mapped['model_name'], categories=list(model_map.values()), ordered=True)
    
    df_mapped = df_mapped.sort_values(['target_name', 'mirror_config', 'model_name']).reset_index(drop=True)
    
    # 3. Construir tabla markdown gigante
    md_lines = []
    md_lines.append("### C. Matriz Completa de Resultados (280 Combinaciones)")
    md_lines.append("Esta tabla exhaustiva detalla el rendimiento obtenido por cada uno de los 5 clasificadores en cada una de las 7 configuraciones espejo para la totalidad de las 8 variables predictivas:")
    md_lines.append("")
    md_lines.append("| Mercado (Target) | Configuración Espejo | Clasificador (Modelo) | Exactitud (Accuracy) | F1-Score | ROC-AUC |")
    md_lines.append("| :--- | :--- | :--- | :---: | :---: | :---: |")
    
    for idx, row in df_mapped.iterrows():
        acc_str = f"{row['accuracy']:.4f}"
        f1_str = f"{row['f1_score']:.4f}"
        if row['target_name'] == "1X2 (Match Winner)":
            auc_str = "N/A (Multiclase)"
        else:
            auc_str = f"{row['roc_auc']:.4f}"
        md_lines.append(f"| {row['target_name']} | {row['mirror_config']} | {row['model_name']} | {acc_str} | {f1_str} | {auc_str} |")
        
    md_table_content = "\n".join(md_lines)
    
    # 4. Insertar tabla en la plantilla limpia
    # Buscamos el final de la sección 4, justo antes de "## 5. 📉 Visualización"
    insertion_anchor = "## 5. 📉 Visualización del Impacto del Resampling (Multimétrica)"
    
    if insertion_anchor in template:
        # Reemplazar e insertar antes del ancla
        new_md_content = template.replace(insertion_anchor, md_table_content + "\n\n---\n\n" + insertion_anchor)
        
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(new_md_content)
        print("✅ Plantilla restaurada y tabla gigante insertada exitosamente en el markdown.")
    else:
        print("❌ Error: No se encontró el ancla en la plantilla.")

if __name__ == "__main__":
    main()
