import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt

def main():
    csv_path = "models/mirrors/mirror_comparison_results.csv"
    if not os.path.exists(csv_path):
        print(f"[Error] Error: No se encontró el archivo de resultados {csv_path}.")
        return
        
    df = pd.read_csv(csv_path)
    print(f"[OK] Cargados {len(df)} registros para la comparativa completa.")
    
    # Definición ordenada de las técnicas de resampling
    configs = [
        "main",
        "oversampling_random",
        "oversampling_smote",
        "undersampling_random",
        "undersampling_tomek",
        "undersampling_centroids",
        "undersampling_nearmiss"
    ]
    
    # Nombre estético corto para el eje X
    config_labels_x = ["Original", "ROS", "SMOTE", "RUS", "Tomek", "Centroids", "NearMiss"]
    
    classifiers = [
        "Logistic Regression (Elastic Net)",
        "Random Forest",
        "HistGradientBoosting (Early Stopping)",
        "XGBoost (L1/L2 Regularized)",
        "Neural Network (Dropout)"
    ]
    
    # Estilos de línea, marcadores y colores para cada clasificador
    styles = {
        "Logistic Regression (Elastic Net)": {"color": "#4A5568", "marker": "o", "ls": "--", "label": "Logistic Regression"},
        "Random Forest": {"color": "#3182CE", "marker": "s", "ls": "-", "label": "Random Forest"},
        "HistGradientBoosting (Early Stopping)": {"color": "#38A169", "marker": "^", "ls": "-", "label": "HistGradientBoosting"},
        "XGBoost (L1/L2 Regularized)": {"color": "#DD6B20", "marker": "D", "ls": "-", "label": "XGBoost"},
        "Neural Network (Dropout)": {"color": "#805AD5", "marker": "*", "ls": "-", "label": "Neural Network (MLP)"}
    }
    
    # Configuración de tipografía académica
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'DejaVu Sans']
    
    # Crear figura 2x2
    fig, axs = plt.subplots(2, 2, figsize=(18, 12))
    ((ax1, ax2), (ax3, ax4)) = axs
    
    # Targets de interés
    t_dc = "Double Chance 1X (Home or Draw)"
    t_cs = "Home Clean Sheet"
    
    # -----------------------------------------------------------------
    # SUBPLOT 1: Double Chance 1X - Accuracy
    # -----------------------------------------------------------------
    ax1.set_title("A. Doble Oportunidad 1X - Exactitud (Accuracy)", fontsize=12, fontweight='bold', pad=10)
    for clf in classifiers:
        clf_data = df[(df['target_name'] == t_dc) & (df['model_name'] == clf)]
        vals = []
        for conf in configs:
            val = clf_data[clf_data['mirror_config'] == conf]['accuracy'].values
            vals.append(val[0] if len(val) > 0 else 0)
        ax1.plot(config_labels_x, vals, label=styles[clf]["label"], color=styles[clf]["color"], 
                 marker=styles[clf]["marker"], linestyle=styles[clf]["ls"], linewidth=2, markersize=8)
    ax1.set_ylabel("Accuracy", fontsize=11)
    ax1.grid(True, linestyle='--', alpha=0.5, color='#CBD5E0')
    ax1.set_ylim(0.48, 0.72)
    
    # -----------------------------------------------------------------
    # SUBPLOT 2: Double Chance 1X - F1-Score
    # -----------------------------------------------------------------
    ax2.set_title("B. Doble Oportunidad 1X - F1-Score", fontsize=12, fontweight='bold', pad=10)
    for clf in classifiers:
        clf_data = df[(df['target_name'] == t_dc) & (df['model_name'] == clf)]
        vals = []
        for conf in configs:
            val = clf_data[clf_data['mirror_config'] == conf]['f1_score'].values
            vals.append(val[0] if len(val) > 0 else 0)
        ax2.plot(config_labels_x, vals, color=styles[clf]["color"], 
                 marker=styles[clf]["marker"], linestyle=styles[clf]["ls"], linewidth=2, markersize=8)
    ax2.set_ylabel("F1-Score", fontsize=11)
    ax2.grid(True, linestyle='--', alpha=0.5, color='#CBD5E0')
    ax2.set_ylim(0.55, 0.82)
    
    # -----------------------------------------------------------------
    # SUBPLOT 3: Home Clean Sheet - Accuracy
    # -----------------------------------------------------------------
    ax3.set_title("C. Valla Invicta Local - Exactitud (Accuracy)", fontsize=12, fontweight='bold', pad=10)
    for clf in classifiers:
        clf_data = df[(df['target_name'] == t_cs) & (df['model_name'] == clf)]
        vals = []
        for conf in configs:
            val = clf_data[clf_data['mirror_config'] == conf]['accuracy'].values
            vals.append(val[0] if len(val) > 0 else 0)
        ax3.plot(config_labels_x, vals, color=styles[clf]["color"], 
                 marker=styles[clf]["marker"], linestyle=styles[clf]["ls"], linewidth=2, markersize=8)
    ax3.set_ylabel("Accuracy", fontsize=11)
    ax3.grid(True, linestyle='--', alpha=0.5, color='#CBD5E0')
    ax3.set_ylim(0.45, 0.72)
    
    # -----------------------------------------------------------------
    # SUBPLOT 4: Home Clean Sheet - F1-Score
    # -----------------------------------------------------------------
    ax4.set_title("D. Valla Invicta Local - F1-Score", fontsize=12, fontweight='bold', pad=10)
    for clf in classifiers:
        clf_data = df[(df['target_name'] == t_cs) & (df['model_name'] == clf)]
        vals = []
        for conf in configs:
            val = clf_data[clf_data['mirror_config'] == conf]['f1_score'].values
            vals.append(val[0] if len(val) > 0 else 0)
        ax4.plot(config_labels_x, vals, color=styles[clf]["color"], 
                 marker=styles[clf]["marker"], linestyle=styles[clf]["ls"], linewidth=2, markersize=8)
    ax4.set_ylabel("F1-Score", fontsize=11)
    ax4.grid(True, linestyle='--', alpha=0.5, color='#CBD5E0')
    ax4.set_ylim(0.00, 0.50)
    
    # Leyenda unificada para la cuadrícula
    handles, labels = ax1.get_legend_handles_labels()
    fig.legend(handles, labels, loc='lower center', ncol=5, frameon=True, facecolor='white', edgecolor='#E2E8F0', fontsize=12, bbox_to_anchor=(0.5, 0.02))
    
    # Título general
    plt.suptitle("Estudio de Rendimiento Cruzado: Todos los Modelos vs. Todas las Técnicas de Resampling\n(Evaluación Cruzada Temporal con 5 Splits en Premier League)", fontsize=16, fontweight='bold', y=0.96)
    
    # Remover bordes para estilo académico limpio
    for ax in [ax1, ax2, ax3, ax4]:
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#718096')
        ax.spines['bottom'].set_color('#718096')
        
    plt.tight_layout(rect=[0, 0.08, 1, 0.90])
    
    output_path = 'd:/datascience/Carpeta_Presentacion/26_Comparativa_Completa_Modelos_Resampling.png'
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"[OK] Gráfico de comparativa cruzada completa guardado en: {output_path}")

if __name__ == "__main__":
    main()
