import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, "models", "tuning_comparison_results.csv")
    
    if not os.path.exists(csv_path):
        print(f"[Error] No se encontró el archivo de resultados de sintonización: {csv_path}")
        return
        
    df = pd.read_csv(csv_path)
    print(f"[OK] Cargados {len(df)} registros para la comparativa Baseline vs. Optuna.")
    
    # 8 Targets ordenados
    targets = [
        "1X2 (Match Winner)",
        "Double Chance 1X (Home or Draw)",
        "Double Chance X2 (Away or Draw)",
        "Over 2.5 Goals",
        "Under 2.5 Goals",
        "BTTS (Both Teams To Score)",
        "BTTS - No",
        "Home Clean Sheet"
    ]
    
    # 5 Modelos en orden corto para etiquetas del eje X
    model_labels = {
        "Logistic Regression (Elastic Net)": "Logistic\nReg.",
        "Random Forest": "Random\nForest",
        "HistGradientBoosting (Early Stopping)": "HistGB",
        "XGBoost (L1/L2 Regularized)": "XGBoost",
        "Neural Network (Dropout)": "MLP\nNeuralNet"
    }
    
    classifiers = list(model_labels.keys())
    
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'DejaVu Sans']
    
    # Crear figura de 2x4 subplots
    fig, axs = plt.subplots(2, 4, figsize=(24, 12))
    axs_flat = axs.flatten()
    
    bar_width = 0.35
    
    # Paleta de colores diferenciados para Baseline y Optuna
    color_baseline = "#A0AEC0"  # Gris Slate medio
    color_optuna = "#3182CE"    # Azul Royal brillante
    
    for idx, target in enumerate(targets):
        ax = axs_flat[idx]
        ax.set_title(target, fontsize=13, fontweight='bold', pad=10)
        
        target_df = df[df['Mercado'] == target]
        
        x = np.arange(len(classifiers))
        
        baseline_vals = []
        optuna_vals = []
        
        for clf in classifiers:
            row = target_df[target_df['Modelo'] == clf]
            if len(row) > 0:
                baseline_vals.append(row['Línea Base'].values[0])
                optuna_vals.append(row['Optimizado'].values[0])
            else:
                baseline_vals.append(0.0)
                optuna_vals.append(0.0)
                
        # Graficar barras adyacentes
        rects1 = ax.bar(x - bar_width/2, baseline_vals, bar_width, label='Línea Base (Original)', color=color_baseline, edgecolor='white', linewidth=0.5)
        rects2 = ax.bar(x + bar_width/2, optuna_vals, bar_width, label='Optimizado (Optuna)', color=color_optuna, edgecolor='white', linewidth=0.5)
        
        ax.set_ylabel("Accuracy Promedio", fontsize=10)
        ax.set_xticks(x)
        ax.set_xticklabels([model_labels[clf] for clf in classifiers], fontsize=9)
        ax.grid(True, linestyle='--', alpha=0.5, color='#CBD5E0')
        ax.set_ylim(0.40, 0.75)
        
        # Añadir etiquetas de valor arriba de las barras con la mejora
        for i in range(len(classifiers)):
            diff = optuna_vals[i] - baseline_vals[i]
            if diff > 0.001:
                # Anotar la mejora en verde sobre la barra de Optuna
                ax.text(x[i] + bar_width/2, optuna_vals[i] + 0.005, f"+{diff:.2%}", 
                        ha='center', va='bottom', fontsize=8, color='#2F855A', fontweight='bold')
                        
        # Eliminar bordes top/right para estilo académico limpio
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#718096')
        ax.spines['bottom'].set_color('#718096')
        
    # Añadir leyenda unificada
    handles, labels = axs_flat[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='lower center', ncol=2, frameon=True, facecolor='white', edgecolor='#E2E8F0', fontsize=12, bbox_to_anchor=(0.5, 0.01))
    
    # Título principal de la figura
    plt.suptitle("Impacto de la Sintonización de Hiperparámetros con Optuna en Todos los Mercados\n(Comparativa de Exactitud: Hiperparámetros Baseline vs. Optimización Bayesiana TPE)", fontsize=17, fontweight='bold', y=0.96)
    
    plt.tight_layout(rect=[0, 0.06, 1, 0.91])
    
    output_path = 'd:/datascience/Carpeta_Presentacion/30_Comparativa_Baseline_vs_Optuna.png'
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"[OK] Gráfico comparativo de optimización guardado en: {output_path}")

if __name__ == "__main__":
    main()
