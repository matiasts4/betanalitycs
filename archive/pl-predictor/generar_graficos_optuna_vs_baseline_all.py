import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt

def plot_metric(df, targets, classifiers, model_labels, metric_base_col, metric_opt_col, metric_label, title, output_path, y_min, y_max, show_diff_percentage=True):
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'DejaVu Sans']
    
    fig, axs = plt.subplots(2, 4, figsize=(24, 12))
    axs_flat = axs.flatten()
    
    bar_width = 0.35
    color_baseline = "#A0AEC0"  # Gris Slate
    color_optuna = "#3182CE"    # Azul Royal
    
    for idx, target in enumerate(targets):
        ax = axs_flat[idx]
        ax.set_title(target, fontsize=13, fontweight='bold', pad=10)
        
        target_df = df[df['target_name'] == target]
        x = np.arange(len(classifiers))
        
        baseline_vals = []
        optuna_vals = []
        
        for clf in classifiers:
            row = target_df[target_df['model_name'] == clf]
            if len(row) > 0:
                baseline_vals.append(row[metric_base_col].values[0])
                optuna_vals.append(row[metric_opt_col].values[0])
            else:
                baseline_vals.append(0.0)
                optuna_vals.append(0.0)
                
        # Caso especial para ROC-AUC de multiclase (1X2 Match Winner)
        if metric_label == "ROC-AUC" and target == "1X2 (Match Winner)":
            ax.text(0.5, 0.5, "N/A\n(Target Multiclase)", fontsize=14, color='#A0AEC0', 
                    ha='center', va='center', fontweight='bold', transform=ax.transAxes)
            ax.set_xticks([])
            ax.set_yticks([])
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_visible(False)
            ax.spines['bottom'].set_visible(False)
            continue
            
        # Graficar barras
        rects1 = ax.bar(x - bar_width/2, baseline_vals, bar_width, label='Línea Base (Original)', color=color_baseline, edgecolor='white', linewidth=0.5)
        rects2 = ax.bar(x + bar_width/2, optuna_vals, bar_width, label='Optimizado (Optuna)', color=color_optuna, edgecolor='white', linewidth=0.5)
        
        ax.set_ylabel(f"{metric_label} Promedio", fontsize=10)
        ax.set_xticks(x)
        ax.set_xticklabels([model_labels[clf] for clf in classifiers], fontsize=9)
        ax.grid(True, linestyle='--', alpha=0.5, color='#CBD5E0')
        ax.set_ylim(y_min, y_max)
        
        # Anotar diferencia porcentual
        if show_diff_percentage:
            for i in range(len(classifiers)):
                diff = optuna_vals[i] - baseline_vals[i]
                if diff > 0.001:
                    ax.text(x[i] + bar_width/2, optuna_vals[i] + 0.005, f"+{diff:.2%}", 
                            ha='center', va='bottom', fontsize=8, color='#2F855A', fontweight='bold')
                            
        # Limpieza de bordes
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#718096')
        ax.spines['bottom'].set_color('#718096')
        
    handles, labels = axs_flat[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='lower center', ncol=2, frameon=True, facecolor='white', edgecolor='#E2E8F0', fontsize=12, bbox_to_anchor=(0.5, 0.01))
    
    plt.suptitle(title, fontsize=17, fontweight='bold', y=0.96)
    plt.tight_layout(rect=[0, 0.06, 1, 0.91])
    
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"[OK] Gráfico comparativo de {metric_label} guardado en: {output_path}")

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, "models", "baseline_vs_optimized_metrics.csv")
    
    if not os.path.exists(csv_path):
        print(f"[Error] No se encontró el archivo de métricas cruzadas: {csv_path}")
        return
        
    df = pd.read_csv(csv_path)
    print(f"[OK] Cargados {len(df)} registros para la generación de gráficos de comparación.")
    
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
    
    model_labels = {
        "Logistic Regression (Elastic Net)": "Logistic\nReg.",
        "Random Forest": "Random\nForest",
        "HistGradientBoosting (Early Stopping)": "HistGB",
        "XGBoost (L1/L2 Regularized)": "XGBoost",
        "Neural Network (Dropout)": "MLP\nNeuralNet"
    }
    
    classifiers = list(model_labels.keys())
    
    # 1. Gráfico de Accuracy
    plot_metric(
        df=df,
        targets=targets,
        classifiers=classifiers,
        model_labels=model_labels,
        metric_base_col="accuracy_baseline",
        metric_opt_col="accuracy_optuna",
        metric_label="Accuracy",
        title="Impacto de la Sintonización de Hiperparámetros con Optuna en Todos los Mercados\n(Comparativa de Exactitud: Hiperparámetros Baseline vs. Optimización Bayesiana TPE)",
        output_path='d:/datascience/Carpeta_Presentacion/30_Comparativa_Baseline_vs_Optuna.png',
        y_min=0.40,
        y_max=0.75,
        show_diff_percentage=True
    )
    
    # 2. Gráfico de F1-Score
    plot_metric(
        df=df,
        targets=targets,
        classifiers=classifiers,
        model_labels=model_labels,
        metric_base_col="f1_baseline",
        metric_opt_col="f1_optuna",
        metric_label="F1-Score",
        title="Impacto de la Sintonización de Hiperparámetros con Optuna en Todos los Mercados\n(Comparativa de F1-Score: Hiperparámetros Baseline vs. Optimización Bayesiana TPE)",
        output_path='d:/datascience/Carpeta_Presentacion/31_Comparativa_F1_Baseline_vs_Optuna.png',
        y_min=0.00,
        y_max=0.85,
        show_diff_percentage=True
    )
    
    # 3. Gráfico de ROC-AUC
    plot_metric(
        df=df,
        targets=targets,
        classifiers=classifiers,
        model_labels=model_labels,
        metric_base_col="auc_baseline",
        metric_opt_col="auc_optuna",
        metric_label="ROC-AUC",
        title="Impacto de la Sintonización de Hiperparámetros con Optuna en Todos los Mercados\n(Comparativa de ROC-AUC: Hiperparámetros Baseline vs. Optimización Bayesiana TPE)",
        output_path='d:/datascience/Carpeta_Presentacion/32_Comparativa_ROC_AUC_Baseline_vs_Optuna.png',
        y_min=0.40,
        y_max=0.75,
        show_diff_percentage=True
    )
    
    print("\n[OK] ¡Todos los gráficos comparativos (Accuracy, F1, ROC-AUC) creados exitosamente!")

if __name__ == "__main__":
    main()
