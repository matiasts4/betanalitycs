import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt

def main():
    csv_path = "models/optimized_models_comparison_results.csv"
    if not os.path.exists(csv_path):
        print(f"[Error] No se encontró el archivo de resultados {csv_path}.")
        return
        
    df_main = pd.read_csv(csv_path)
    print(f"[OK] Cargados {len(df_main)} registros para los modelos optimizados.")
    
    # Targets de interés para graficar
    key_targets = [
        "Double Chance 1X (Home or Draw)",
        "Home Clean Sheet",
        "1X2 (Match Winner)",
        "BTTS (Both Teams To Score)"
    ]
    
    plot_df = df_main[df_main['target_name'].isin(key_targets)].copy()
    
    # Clasificadores evaluados
    classifiers = [
        "Logistic Regression (Elastic Net)",
        "Random Forest",
        "HistGradientBoosting (Early Stopping)",
        "XGBoost (L1/L2 Regularized)",
        "Neural Network (Dropout)"
    ]
    
    # Paleta de colores académica diferenciada para cada clasificador
    colors = {
        "Logistic Regression (Elastic Net)": "#4A5568",     # Charcoal Grey
        "Random Forest": "#3182CE",                         # Royal Blue
        "HistGradientBoosting (Early Stopping)": "#38A169", # Forest Green
        "XGBoost (L1/L2 Regularized)": "#DD6B20",           # Terracotta Orange
        "Neural Network (Dropout)": "#805AD5"               # Deep Purple
    }
    
    short_target_names = [
        "Doble Op. 1X\n(67/33)",
        "Valla Invicta Local\n(70/30)",
        "Resultado 1X2\n(44/33/23)",
        "Ambos Anotan\n(53/47)"
    ]
    
    # Estructura del gráfico: 2 paneles (Accuracy y F1-Score)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 7))
    
    x = np.arange(len(key_targets))
    width = 0.15  # Ancho de las barras para dar espacio a los 5 modelos
    
    # -----------------------------------------------------------------
    # PANEL 1: COMPARATIVA DE ACCURACY
    # -----------------------------------------------------------------
    for i, clf in enumerate(classifiers):
        clf_data = plot_df[plot_df['model_name'] == clf]
        acc_values = []
        for target in key_targets:
            val = clf_data[clf_data['target_name'] == target]['accuracy'].values
            acc_values.append(val[0] if len(val) > 0 else 0)
            
        pos = x + (i - len(classifiers)/2 + 0.5) * width
        ax1.bar(pos, acc_values, width, label=clf.split(" (")[0], color=colors[clf], edgecolor='white', linewidth=0.5)
        
    ax1.set_title("A. Exactitud (Accuracy) de los Modelos", fontsize=13, fontweight='bold', pad=10)
    ax1.set_xticks(x)
    ax1.set_xticklabels(short_target_names, fontsize=10)
    ax1.set_ylabel("Accuracy Promedio", fontsize=11)
    ax1.set_ylim(0.40, 0.75)
    ax1.grid(True, linestyle='--', alpha=0.5, color='#CBD5E0')
    
    # -----------------------------------------------------------------
    # PANEL 2: COMPARATIVA DE F1-SCORE
    # -----------------------------------------------------------------
    for i, clf in enumerate(classifiers):
        clf_data = plot_df[plot_df['model_name'] == clf]
        f1_values = []
        for target in key_targets:
            val = clf_data[clf_data['target_name'] == target]['f1_score'].values
            f1_values.append(val[0] if len(val) > 0 else 0)
            
        pos = x + (i - len(classifiers)/2 + 0.5) * width
        ax2.bar(pos, f1_values, width, label=clf.split(" (")[0], color=colors[clf], edgecolor='white', linewidth=0.5)
        
    ax2.set_title("B. F1-Score de los Modelos", fontsize=13, fontweight='bold', pad=10)
    ax2.set_xticks(x)
    ax2.set_xticklabels(short_target_names, fontsize=10)
    ax2.set_ylabel("F1-Score Promedio", fontsize=11)
    ax2.set_ylim(0.15, 0.85)
    ax2.grid(True, linestyle='--', alpha=0.5, color='#CBD5E0')
    
    # Leyenda unificada para ambos paneles
    handles, labels = ax1.get_legend_handles_labels()
    fig.legend(handles, labels, loc='lower center', ncol=5, frameon=True, facecolor='white', edgecolor='#E2E8F0', fontsize=11, bbox_to_anchor=(0.5, -0.01))
    
    # Título general
    plt.suptitle("Comparativa de Modelos de Machine Learning Optimizados (Optuna)\n(Evaluación Cruzada Temporal con 5 Splits en Premier League)", fontsize=15, fontweight='bold', y=0.96)
    
    # Remover bordes para estilo académico limpio
    for ax in [ax1, ax2]:
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#718096')
        ax.spines['bottom'].set_color('#718096')
        
    plt.tight_layout(rect=[0, 0.08, 1, 0.90])
    
    output_path = 'd:/datascience/Carpeta_Presentacion/25_Comparativa_Modelos_Original.png'
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"[OK] Gráfico comparativo de modelos guardado en: {output_path}")

if __name__ == "__main__":
    main()
