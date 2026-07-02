import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt

def main():
    csv_path = "models/mirrors/mirror_comparison_results.csv"
    if not os.path.exists(csv_path):
        print(f"[Error] Error: No se encontró el archivo de resultados {csv_path}. ¿Ya terminó el entrenamiento?")
        return
        
    df = pd.read_csv(csv_path)
    print(f"[OK] Cargados {len(df)} registros de resultados.")
    
    # Obtener el máximo de cada métrica (el mejor modelo) por configuración y target
    best_per_config = df.groupby(['mirror_config', 'target_name']).agg({
        'accuracy': 'max',
        'f1_score': 'max',
        'roc_auc': 'max'
    }).reset_index()
    
    # Targets para Accuracy y F1-Score (incluye multiclase)
    targets_acc_f1 = [
        "Double Chance 1X (Home or Draw)",
        "Home Clean Sheet",
        "1X2 (Match Winner)",
        "BTTS (Both Teams To Score)"
    ]
    
    # Targets para ROC-AUC (solo binarios)
    targets_auc = [
        "Double Chance 1X (Home or Draw)",
        "Home Clean Sheet",
        "BTTS (Both Teams To Score)"
    ]
    
    config_labels = {
        "main": "Original (Línea Base)",
        "oversampling_random": "Random Oversampling (ROS)",
        "oversampling_smote": "SMOTE (Oversampling)",
        "undersampling_random": "Random Undersampling (RUS)",
        "undersampling_tomek": "Tomek Links (Undersampling)",
        "undersampling_centroids": "Cluster Centroids (Undersampling)",
        "undersampling_nearmiss": "NearMiss (Undersampling)"
    }
    
    colors = {
        "main": "#2D3748",                     # Slate oscuro (Línea base)
        "oversampling_random": "#4299E1",      # Light Blue
        "oversampling_smote": "#3182CE",       # Dark Blue
        "undersampling_random": "#ED8936",     # Light Orange
        "undersampling_tomek": "#DD6B20",      # Dark Orange
        "undersampling_centroids": "#48BB78",  # Light Green
        "undersampling_nearmiss": "#38A169"    # Dark Green
    }
    
    configs = list(colors.keys())
    
    # Nombres estéticos cortos para los gráficos
    short_labels_4 = [
        "Doble Op. 1X\n(67/33)",
        "Valla Inv. Local\n(70/30)",
        "Resultado 1X2\n(44/33/23)",
        "Ambos Anotan\n(53/47)"
    ]
    short_labels_3 = [
        "Doble Op. 1X\n(67/33)",
        "Valla Inv. Local\n(70/30)",
        "Ambos Anotan\n(53/47)"
    ]
    
    # Tipografía académica
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'DejaVu Sans']
    
    # Crear figura de 3 paneles (1 fila, 3 columnas) con formato widescreen 16:9
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(22, 7.5))
    
    width = 0.11
    
    # -----------------------------------------------------------------
    # PANEL 1: EXACTITUD (ACCURACY)
    # -----------------------------------------------------------------
    x1 = np.arange(len(targets_acc_f1))
    for i, config in enumerate(configs):
        config_data = best_per_config[best_per_config['mirror_config'] == config]
        vals = []
        for target in targets_acc_f1:
            val = config_data[config_data['target_name'] == target]['accuracy'].values
            vals.append(val[0] if len(val) > 0 else 0)
        pos = x1 + (i - len(configs)/2 + 0.5) * width
        ax1.bar(pos, vals, width, color=colors[config], edgecolor='white', linewidth=0.5)
        
    ax1.set_title("A. Exactitud (Accuracy)", fontsize=13, fontweight='bold', pad=10)
    ax1.set_xticks(x1)
    ax1.set_xticklabels(short_labels_4, fontsize=10)
    ax1.set_ylabel("Exactitud Promedio", fontsize=11)
    ax1.set_ylim(0.40, 0.75)
    ax1.grid(True, linestyle='--', alpha=0.5, color='#CBD5E0')
    
    # Línea base punteada
    for idx, target in enumerate(targets_acc_f1):
        orig_val = best_per_config[(best_per_config['mirror_config'] == 'main') & (best_per_config['target_name'] == target)]['accuracy'].values
        if len(orig_val) > 0:
            ax1.hlines(y=orig_val[0], xmin=idx-0.4, xmax=idx+0.4, colors='#718096', linestyles=':', linewidth=1.5)
            
    # -----------------------------------------------------------------
    # PANEL 2: F1-SCORE
    # -----------------------------------------------------------------
    x2 = np.arange(len(targets_acc_f1))
    for i, config in enumerate(configs):
        config_data = best_per_config[best_per_config['mirror_config'] == config]
        vals = []
        for target in targets_acc_f1:
            val = config_data[config_data['target_name'] == target]['f1_score'].values
            vals.append(val[0] if len(val) > 0 else 0)
        pos = x2 + (i - len(configs)/2 + 0.5) * width
        ax2.bar(pos, vals, width, color=colors[config], edgecolor='white', linewidth=0.5)
        
    ax2.set_title("B. F1-Score (Medida de Balance)", fontsize=13, fontweight='bold', pad=10)
    ax2.set_xticks(x2)
    ax2.set_xticklabels(short_labels_4, fontsize=10)
    ax2.set_ylabel("F1-Score Promedio", fontsize=11)
    ax2.set_ylim(0.20, 0.85)
    ax2.grid(True, linestyle='--', alpha=0.5, color='#CBD5E0')
    
    # Línea base punteada
    for idx, target in enumerate(targets_acc_f1):
        orig_val = best_per_config[(best_per_config['mirror_config'] == 'main') & (best_per_config['target_name'] == target)]['f1_score'].values
        if len(orig_val) > 0:
            ax2.hlines(y=orig_val[0], xmin=idx-0.4, xmax=idx+0.4, colors='#718096', linestyles=':', linewidth=1.5)
            
    # -----------------------------------------------------------------
    # PANEL 3: ROC-AUC (SOLO TARGETS BINARIOS)
    # -----------------------------------------------------------------
    x3 = np.arange(len(targets_auc))
    for i, config in enumerate(configs):
        config_data = best_per_config[best_per_config['mirror_config'] == config]
        vals = []
        for target in targets_auc:
            val = config_data[config_data['target_name'] == target]['roc_auc'].values
            vals.append(val[0] if len(val) > 0 else 0)
        pos = x3 + (i - len(configs)/2 + 0.5) * width
        # Usamos label aquí para crear la leyenda unificada al final
        ax3.bar(pos, vals, width, label=config_labels[config], color=colors[config], edgecolor='white', linewidth=0.5)
        
    ax3.set_title("C. Curva ROC (ROC-AUC)", fontsize=13, fontweight='bold', pad=10)
    ax3.set_xticks(x3)
    ax3.set_xticklabels(short_labels_3, fontsize=10)
    ax3.set_ylabel("ROC-AUC Promedio", fontsize=11)
    ax3.set_ylim(0.45, 0.75)
    ax3.grid(True, linestyle='--', alpha=0.5, color='#CBD5E0')
    
    # Línea base punteada
    for idx, target in enumerate(targets_auc):
        orig_val = best_per_config[(best_per_config['mirror_config'] == 'main') & (best_per_config['target_name'] == target)]['roc_auc'].values
        if len(orig_val) > 0:
            ax3.hlines(y=orig_val[0], xmin=idx-0.4, xmax=idx+0.4, colors='#718096', linestyles=':', linewidth=1.5)
            
    # Leyenda unificada abajo de la figura
    fig.legend(loc='lower center', ncol=4, frameon=True, facecolor='white', edgecolor='#E2E8F0', fontsize=11, bbox_to_anchor=(0.5, -0.01))
    
    # Título general de la figura
    plt.suptitle("Estudio Multimétrica: Comparativa del Impacto del Resampling en Modelos Espejo\n(Resultados Consolidados de Validación Cruzada Temporal)", fontsize=16, fontweight='bold', y=0.97)
    
    # Estética de bordes para los tres subplots
    for ax in [ax1, ax2, ax3]:
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#718096')
        ax.spines['bottom'].set_color('#718096')
        
    plt.tight_layout(rect=[0, 0.06, 1, 0.90])
    
    output_path = 'd:/datascience/Carpeta_Presentacion/24_Comparativa_Multimetrica_Resampling.png'
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"[OK] Gráfico comparativo multimétrica guardado en: {output_path}")

if __name__ == "__main__":
    main()
