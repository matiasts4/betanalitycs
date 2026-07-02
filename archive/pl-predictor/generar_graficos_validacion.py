import pandas as pd
import numpy as np
import os
import sys
import matplotlib.pyplot as plt
from sklearn.model_selection import TimeSeriesSplit
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, PowerTransformer
from sklearn.impute import KNNImputer

# Asegurar que el directorio base esté en el path para poder importar src.config
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.config import FEATURES_PATH, FEATURES

def main():
    print(f"Leyendo dataset maestro sanitizado: {FEATURES_PATH}")
    if not os.path.exists(FEATURES_PATH):
        print(f"❌ Error: No se encontró el dataset {FEATURES_PATH}")
        return
        
    df = pd.read_csv(FEATURES_PATH)
    
    # Filtrar partidos no jugados (como en el pipeline oficial)
    df = df[df['game_id'].astype(str) != '0'].reset_index(drop=True)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date').reset_index(drop=True)
    
    # Crear el target Double Chance 1X (Home or Draw)
    df['target_dc_1X'] = (df['result_1x2'] >= 1).astype(int)
    
    X = df[FEATURES]
    y = df['target_dc_1X']
    
    # Definición de pipeline igual al oficial
    def create_pipeline(classifier):
        skewed_features = ['away_xg', 'referee_avg_cards_history', 'B365H', 'B365D', 'B365A', 'h_l5_fls', 'a_l5_fls', 'h_l5_xg', 'a_l5_xg', 'h_l5_xga', 'a_l5_xga']
        skewed_in_features = [f for f in skewed_features if f in FEATURES]
        standard_in_features = [f for f in FEATURES if f not in skewed_in_features]
        
        preprocessor = ColumnTransformer(
            transformers=[
                ('skewed', Pipeline([
                    ('imputer', KNNImputer(n_neighbors=5, weights='distance')),
                    ('yeo_johnson', PowerTransformer(method='yeo-johnson', standardize=True))
                ]), skewed_in_features),
                ('standard', Pipeline([
                    ('imputer', KNNImputer(n_neighbors=5, weights='distance')),
                    ('scaler', StandardScaler())
                ]), standard_in_features)
            ],
            remainder='passthrough'
        )
        
        return Pipeline([
            ('preprocessor', preprocessor),
            ('classifier', classifier)
        ])
        
    # ==========================================
    # 1. GENERACIÓN DE CURVA DE VALIDACIÓN
    # ==========================================
    print("Generando Curva de Validación (max_depth)...")
    max_depths = [2, 3, 4, 5, 6, 7, 8, 10, 12, 15, 20]
    train_scores_mean = []
    val_scores_mean = []
    
    tscv = TimeSeriesSplit(n_splits=5)
    
    for depth in max_depths:
        # Usamos min_samples_leaf=4 como en el script de entrenamiento oficial
        clf = RandomForestClassifier(n_estimators=100, max_depth=depth, min_samples_leaf=4, random_state=42, n_jobs=-1)
        pipeline = create_pipeline(clf)
        
        train_scores = []
        val_scores = []
        
        for train_idx, test_idx in tscv.split(X):
            X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
            y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
            
            pipeline.fit(X_train, y_train)
            
            train_scores.append(pipeline.score(X_train, y_train))
            val_scores.append(pipeline.score(X_test, y_test))
            
        train_scores_mean.append(np.mean(train_scores))
        val_scores_mean.append(np.mean(val_scores))
        print(f"  Profundidad {depth:2d} | Train Acc: {np.mean(train_scores):.4f} | Val Acc: {np.mean(val_scores):.4f}")
        
    # Graficar Curva de Validación
    plt.figure(figsize=(10, 6))
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'DejaVu Sans']
    
    plt.plot(max_depths, train_scores_mean, label='Exactitud Entrenamiento (Train)', color='#C05621', marker='o', linewidth=2) # warm terracotta/bronze
    plt.plot(max_depths, val_scores_mean, label='Exactitud Validación (Test)', color='#2B6CB0', marker='s', linewidth=2) # slate blue
    plt.grid(True, linestyle='--', alpha=0.5, color='#CBD5E0')
    
    # Encontrar óptimo
    optimal_idx = np.argmax(val_scores_mean)
    optimal_depth = max_depths[optimal_idx]
    optimal_score = val_scores_mean[optimal_idx]
    
    plt.axvline(x=optimal_depth, color='#38A169', linestyle=':', linewidth=2, label=f'Óptimo (depth={optimal_depth})')
    plt.scatter(optimal_depth, optimal_score, color='#38A169', s=150, zorder=5)
    
    # Ajustar anotaciones
    plt.annotate(f'Punto Óptimo (max_depth={optimal_depth})\nVal Acc: {optimal_score:.4f}', 
                 xy=(optimal_depth, optimal_score), 
                 xytext=(optimal_depth + 1, optimal_score - 0.035),
                 arrowprops=dict(arrowstyle="->", color='#38A169', lw=1.5),
                 fontsize=10, fontweight='bold', color='#2F855A')
                 
    # Áreas de sobreajuste y subajuste
    plt.axvspan(1.5, 3.5, color='#EDF2F7', alpha=0.4)
    plt.text(2.5, 0.60, 'Zona de Sesgo Alto\n(Subajuste / Underfitting)', color='#4A5568', fontsize=10, ha='center', style='italic')
    
    plt.axvspan(9.5, 20.5, color='#EDF2F7', alpha=0.4)
    plt.text(15, 0.60, 'Zona de Varianza Alta\n(Sobreajuste / Overfitting)', color='#4A5568', fontsize=10, ha='center', style='italic')
    
    plt.title('Curva de Validación: Rendimiento vs. Complejidad (max_depth)\n(Random Forest - Mercado 1X / Home or Draw)', fontsize=14, fontweight='bold', pad=15)
    plt.xlabel('Complejidad del Modelo: Profundidad Máxima de Árboles (max_depth)', fontsize=12)
    plt.ylabel('Exactitud (Accuracy)', fontsize=12)
    plt.legend(loc='lower right', fontsize=11)
    
    # Remover bordes
    ax = plt.gca()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#718096')
    ax.spines['bottom'].set_color('#718096')
    
    plt.tight_layout()
    output_path_val = 'd:/datascience/Carpeta_Presentacion/21_Curva_Validacion_Complejidad.png'
    plt.savefig(output_path_val, dpi=300)
    plt.close()
    print(f"✅ Curva de Validación guardada en: {output_path_val}")
    
    # ==========================================
    # 2. GENERACIÓN DE CURVA DE APRENDIZAJE
    # ==========================================
    print("Generando Curva de Aprendizaje (n_samples)...")
    clf_opt = RandomForestClassifier(n_estimators=100, max_depth=optimal_depth, min_samples_leaf=4, random_state=42, n_jobs=-1)
    pipeline_opt = create_pipeline(clf_opt)
    
    train_sizes = np.linspace(0.1, 1.0, 10)
    train_scores_lc_mean = []
    val_scores_lc_mean = []
    n_samples_list = []
    
    for size in train_sizes:
        train_scores_fold = []
        val_scores_fold = []
        
        for train_idx, test_idx in tscv.split(X):
            n_train = len(train_idx)
            n_sub_train = max(int(size * n_train), 20)  # Mínimo 20 registros
            sub_train_idx = train_idx[:n_sub_train]
            
            X_train_sub, X_test = X.iloc[sub_train_idx], X.iloc[test_idx]
            y_train_sub, y_test = y.iloc[sub_train_idx], y.iloc[test_idx]
            
            pipeline_opt.fit(X_train_sub, y_train_sub)
            
            train_scores_fold.append(pipeline_opt.score(X_train_sub, y_train_sub))
            val_scores_fold.append(pipeline_opt.score(X_test, y_test))
            
        train_scores_lc_mean.append(np.mean(train_scores_fold))
        val_scores_lc_mean.append(np.mean(val_scores_fold))
        
        # Calcular el tamaño promedio usado en el eje X
        avg_samples = int(size * np.mean([len(t_idx) for t_idx, _ in tscv.split(X)]))
        n_samples_list.append(avg_samples)
        print(f"  Tamaño Entrenamiento Promedio: {avg_samples:4d} | Train Acc: {np.mean(train_scores_fold):.4f} | Val Acc: {np.mean(val_scores_fold):.4f}")
        
    # Graficar Curva de Aprendizaje
    plt.figure(figsize=(10, 6))
    
    plt.plot(n_samples_list, train_scores_lc_mean, label='Exactitud Entrenamiento (Train)', color='#C05621', marker='o', linewidth=2)
    plt.plot(n_samples_list, val_scores_lc_mean, label='Exactitud Validación (Test)', color='#2B6CB0', marker='s', linewidth=2)
    plt.grid(True, linestyle='--', alpha=0.5, color='#CBD5E0')
    
    # Marcar zona de convergencia
    convergence_idx = 4
    plt.axvspan(n_samples_list[convergence_idx], n_samples_list[-1], color='#E6FFFA', alpha=0.4)
    plt.text(np.mean([n_samples_list[convergence_idx], n_samples_list[-1]]), 
             np.mean([train_scores_lc_mean[-1], val_scores_lc_mean[-1]]) + 0.05, 
             'Zona de Convergencia de Datos\n(Añadir más partidos históricos no mejora significativamente)', 
             color='#234E52', fontsize=10, ha='center', style='italic', fontweight='semibold')
             
    plt.title('Curva de Aprendizaje: Rendimiento vs. Volumen de Datos de Entrenamiento\n(Random Forest con max_depth=%d)' % optimal_depth, fontsize=14, fontweight='bold', pad=15)
    plt.xlabel('Número de Partidos de Entrenamiento (Tamaño Muestra)', fontsize=12)
    plt.ylabel('Exactitud (Accuracy)', fontsize=12)
    plt.legend(loc='lower right', fontsize=11)
    
    # Remover bordes
    ax = plt.gca()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#718096')
    ax.spines['bottom'].set_color('#718096')
    
    plt.tight_layout()
    output_path_lc = 'd:/datascience/Carpeta_Presentacion/22_Curva_Aprendizaje_Convergencia.png'
    plt.savefig(output_path_lc, dpi=300)
    plt.close()
    print(f"✅ Curva de Aprendizaje guardada en: {output_path_lc}")

if __name__ == "__main__":
    main()
