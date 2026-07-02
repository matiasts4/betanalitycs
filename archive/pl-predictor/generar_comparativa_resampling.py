import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt

def main():
    csv_path = "models/mirrors/mirror_comparison_results.csv"
    if not os.path.exists(csv_path):
        print(f"❌ Error: No se encontró el archivo de resultados {csv_path}. ¿Ya terminó el entrenamiento?")
        return
        
    df = pd.read_csv(csv_path)
    print(f"✅ Cargados {len(df)} registros de resultados.")
    
    # Queremos comparar el MEJOR modelo para cada target bajo cada configuración espejo
    # Para ello, agrupamos por mirror_config y target_name y tomamos el máximo valor de accuracy y f1_score
    best_per_config = df.groupby(['mirror_config', 'target_name']).agg({
        'accuracy': 'max',
        'f1_score': 'max',
        'roc_auc': 'max'
    }).reset_index()
    
    # Targets clave para visualizar desbalance
    key_targets = [
        "Double Chance 1X (Home or Draw)",
        "Home Clean Sheet",
        "1X2 (Match Winner)",
        "BTTS (Both Teams To Score)"
    ]
    
    # Filtrar resultados para los targets clave
    plot_df = best_per_config[best_per_config['target_name'].isin(key_targets)].copy()
    
    # Nombre estético para las técnicas de resampling
    config_labels = {
        "main": "Original (Sin Resampling)",
        "oversampling_random": "Random Oversampling (ROS)",
        "oversampling_smote": "SMOTE (Oversampling)",
        "undersampling_random": "Random Undersampling (RUS)",
        "undersampling_tomek": "Tomek Links (Undersampling)",
        "undersampling_centroids": "Cluster Centroids (Undersampling)",
        "undersampling_nearmiss": "NearMiss (Undersampling)"
    }
    plot_df['config_label'] = plot_df['mirror_config'].map(config_labels)
    
    # Paleta de colores académica y armoniosa (tonos Slate, Blues y Muted Warm)
    colors = {
        "main": "#2D3748",                     # Slate oscuro (Línea base)
        "oversampling_random": "#4299E1",      # Blue
        "oversampling_smote": "#3182CE",       # Darker Blue
        "undersampling_random": "#ED8936",     # Orange
        "undersampling_tomek": "#DD6B20",      # Darker Orange
        "undersampling_centroids": "#48BB78",  # Green
        "undersampling_nearmiss": "#38A169"    # Darker Green
    }
    
    # Configuración de tipografía académica
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'DejaVu Sans']
    
    # ==========================================
    # GRÁFICO 1: COMPARATIVA DE EXACTITUD (ACCURACY)
    # ==========================================
    fig, ax = plt.subplots(figsize=(12, 7))
    
    x = np.arange(len(key_targets))
    width = 0.11
    
    configs = list(colors.keys())
    
    for i, config in enumerate(configs):
        config_data = plot_df[plot_df['mirror_config'] == config]
        acc_values = []
        for target in key_targets:
            val = config_data[config_data['target_name'] == target]['accuracy'].values
            acc_values.append(val[0] if len(val) > 0 else 0)
            
        pos = x + (i - len(configs)/2 + 0.5) * width
        ax.bar(pos, acc_values, width, label=config_labels[config], color=colors[config], edgecolor='white', linewidth=0.5)
        
    ax.set_title('Comparativa de Modelos Espejo: Impacto del Resampling en Exactitud (Accuracy)\n(Evaluación Cruzada Temporal con 5 Splits en Premier League)', fontsize=14, fontweight='bold', pad=15)
    ax.set_xticks(x)
    
    # Nombres más cortos para los ticks del gráfico
    short_target_names = [
        "Doble Oportunidad 1X\n(Desbalance 67/33)",
        "Valla Invicta Local (CS)\n(Desbalance 70/30)",
        "Resultado 1X2 (Multiclase)\n(Desbalance 44/33/23)",
        "Ambos Anotan (BTTS)\n(Balanceado 53/47)"
    ]
    ax.set_xticklabels(short_target_names, fontsize=11)
    ax.set_ylabel('Exactitud Promedio (Accuracy)', fontsize=12)
    ax.set_ylim(0.40, 0.76)
    ax.grid(True, linestyle='--', alpha=0.5, color='#CBD5E0')
    
    # Leyenda posicionada de forma limpia
    ax.legend(loc='upper right', frameon=True, facecolor='white', edgecolor='#E2E8F0', fontsize=10)
    
    # Línea base punteada en los resultados originales (para contraste visual inmediato)
    for idx, target in enumerate(key_targets):
        orig_val = plot_df[(plot_df['mirror_config'] == 'main') & (plot_df['target_name'] == target)]['accuracy'].values
        if len(orig_val) > 0:
            ax.hlines(y=orig_val[0], xmin=idx-0.4, xmax=idx+0.4, colors='#718096', linestyles=':', linewidth=1.5)
            
    # Remover bordes
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#718096')
    ax.spines['bottom'].set_color('#718096')
    
    plt.tight_layout()
    output_path = 'd:/datascience/Carpeta_Presentacion/23_Comparativa_Tecnicas_Resampling.png'
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"✅ Gráfico comparativo guardado en: {output_path}")

if __name__ == "__main__":
    main()
