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
    print(f"[OK] Cargados {len(df)} registros para la visualización total.")
    
    # 7 Configuraciones ordenadas
    configs = [
        "main",
        "oversampling_random",
        "oversampling_smote",
        "undersampling_random",
        "undersampling_tomek",
        "undersampling_centroids",
        "undersampling_nearmiss"
    ]
    config_labels_x = ["Original", "ROS", "SMOTE", "RUS", "Tomek", "Centroids", "NearMiss"]
    
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
    
    classifiers = [
        "Logistic Regression (Elastic Net)",
        "Random Forest",
        "HistGradientBoosting (Early Stopping)",
        "XGBoost (L1/L2 Regularized)",
        "Neural Network (Dropout)"
    ]
    
    styles = {
        "Logistic Regression (Elastic Net)": {"color": "#4A5568", "marker": "o", "ls": "--", "label": "Logistic Regression"},
        "Random Forest": {"color": "#3182CE", "marker": "s", "ls": "-", "label": "Random Forest"},
        "HistGradientBoosting (Early Stopping)": {"color": "#38A169", "marker": "^", "ls": "-", "label": "HistGradientBoosting"},
        "XGBoost (L1/L2 Regularized)": {"color": "#DD6B20", "marker": "D", "ls": "-", "label": "XGBoost"},
        "Neural Network (Dropout)": {"color": "#805AD5", "marker": "*", "ls": "-", "label": "Neural Network (MLP)"}
    }
    
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'DejaVu Sans']
    
    # =================================================================
    # CHART 1: ACCURACY (2x4 Grid)
    # =================================================================
    print("Generando Gráfico Total de Exactitud (Accuracy)...")
    fig, axs = plt.subplots(2, 4, figsize=(24, 12))
    axs_flat = axs.flatten()
    
    for idx, target in enumerate(targets):
        ax = axs_flat[idx]
        ax.set_title(target, fontsize=12, fontweight='bold', pad=8)
        
        for clf in classifiers:
            clf_data = df[(df['target_name'] == target) & (df['model_name'] == clf)]
            vals = []
            for conf in configs:
                val = clf_data[clf_data['mirror_config'] == conf]['accuracy'].values
                vals.append(val[0] if len(val) > 0 else 0)
            ax.plot(config_labels_x, vals, label=styles[clf]["label"], color=styles[clf]["color"], 
                     marker=styles[clf]["marker"], linestyle=styles[clf]["ls"], linewidth=1.5, markersize=6)
                     
        ax.set_ylabel("Accuracy", fontsize=10)
        ax.grid(True, linestyle='--', alpha=0.5, color='#CBD5E0')
        ax.set_ylim(0.40, 0.75)
        
        # Eliminar bordes top/right
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#718096')
        ax.spines['bottom'].set_color('#718096')
        
    handles, labels = axs_flat[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='lower center', ncol=5, frameon=True, facecolor='white', edgecolor='#E2E8F0', fontsize=12, bbox_to_anchor=(0.5, 0.01))
    plt.suptitle("Comparativa de Exactitud (Accuracy): Todos los Modelos en Todos los Mercados e Hitos de Resampling", fontsize=16, fontweight='bold', y=0.96)
    plt.tight_layout(rect=[0, 0.05, 1, 0.92])
    output_acc = 'd:/datascience/Carpeta_Presentacion/27_Comparativa_Completa_Accuracy.png'
    plt.savefig(output_acc, dpi=300)
    plt.close()
    print(f"  [OK] Guardado: {output_acc}")
    
    # =================================================================
    # CHART 2: F1-SCORE (2x4 Grid)
    # =================================================================
    print("Generando Gráfico Total de F1-Score...")
    fig, axs = plt.subplots(2, 4, figsize=(24, 12))
    axs_flat = axs.flatten()
    
    for idx, target in enumerate(targets):
        ax = axs_flat[idx]
        ax.set_title(target, fontsize=12, fontweight='bold', pad=8)
        
        for clf in classifiers:
            clf_data = df[(df['target_name'] == target) & (df['model_name'] == clf)]
            vals = []
            for conf in configs:
                val = clf_data[clf_data['mirror_config'] == conf]['f1_score'].values
                vals.append(val[0] if len(val) > 0 else 0)
            ax.plot(config_labels_x, vals, color=styles[clf]["color"], 
                     marker=styles[clf]["marker"], linestyle=styles[clf]["ls"], linewidth=1.5, markersize=6)
                     
        ax.set_ylabel("F1-Score", fontsize=10)
        ax.grid(True, linestyle='--', alpha=0.5, color='#CBD5E0')
        ax.set_ylim(0.00, 0.85)
        
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#718096')
        ax.spines['bottom'].set_color('#718096')
        
    fig.legend(handles, labels, loc='lower center', ncol=5, frameon=True, facecolor='white', edgecolor='#E2E8F0', fontsize=12, bbox_to_anchor=(0.5, 0.01))
    plt.suptitle("Comparativa de F1-Score: Todos los Modelos en Todos los Mercados e Hitos de Resampling", fontsize=16, fontweight='bold', y=0.96)
    plt.tight_layout(rect=[0, 0.05, 1, 0.92])
    output_f1 = 'd:/datascience/Carpeta_Presentacion/28_Comparativa_Completa_F1.png'
    plt.savefig(output_f1, dpi=300)
    plt.close()
    print(f"  [OK] Guardado: {output_f1}")
    
    # =================================================================
    # CHART 3: ROC-AUC (2x4 Grid)
    # =================================================================
    print("Generando Gráfico Total de ROC-AUC...")
    fig, axs = plt.subplots(2, 4, figsize=(24, 12))
    axs_flat = axs.flatten()
    
    for idx, target in enumerate(targets):
        ax = axs_flat[idx]
        ax.set_title(target, fontsize=12, fontweight='bold', pad=8)
        
        if target == "1X2 (Match Winner)":
            # Caso especial: Target multiclase, mostrar N/A estético en el centro
            ax.text(0.5, 0.5, "N/A\n(Target Multiclase)", fontsize=14, color='#A0AEC0', 
                    ha='center', va='center', fontweight='bold', transform=ax.transAxes)
            ax.set_xticks([])
            ax.set_yticks([])
        else:
            for clf in classifiers:
                clf_data = df[(df['target_name'] == target) & (df['model_name'] == clf)]
                vals = []
                for conf in configs:
                    val = clf_data[clf_data['mirror_config'] == conf]['roc_auc'].values
                    vals.append(val[0] if len(val) > 0 else 0)
                ax.plot(config_labels_x, vals, color=styles[clf]["color"], 
                         marker=styles[clf]["marker"], linestyle=styles[clf]["ls"], linewidth=1.5, markersize=6)
                         
            ax.set_ylabel("ROC-AUC", fontsize=10)
            ax.grid(True, linestyle='--', alpha=0.5, color='#CBD5E0')
            ax.set_ylim(0.40, 0.75)
            
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#718096')
        ax.spines['bottom'].set_color('#718096')
        
    fig.legend(handles, labels, loc='lower center', ncol=5, frameon=True, facecolor='white', edgecolor='#E2E8F0', fontsize=12, bbox_to_anchor=(0.5, 0.01))
    plt.suptitle("Comparativa de ROC-AUC: Todos los Modelos en Todos los Mercados e Hitos de Resampling", fontsize=16, fontweight='bold', y=0.96)
    plt.tight_layout(rect=[0, 0.05, 1, 0.92])
    output_auc = 'd:/datascience/Carpeta_Presentacion/29_Comparativa_Completa_ROC_AUC.png'
    plt.savefig(output_auc, dpi=300)
    plt.close()
    print(f"  [OK] Guardado: {output_auc}")

if __name__ == "__main__":
    main()
