import pandas as pd
import numpy as np
import os
import sys
import matplotlib.pyplot as plt
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, f1_score
from sklearn.linear_model import LogisticRegression

# Asegurar que el directorio base esté en el path para importar src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.config import FEATURES_PATH, FEATURES, MODELS_DIR, BASE_DIR

def prepare_targets(df):
    df_out = df.copy()
    df_out['target_1x2'] = df_out['result_1x2'].astype(int)
    return df_out

def create_pipeline(classifier, use_tomek=False):
    from sklearn.compose import ColumnTransformer
    from sklearn.preprocessing import StandardScaler, PowerTransformer
    from sklearn.impute import KNNImputer
    from imblearn.pipeline import Pipeline as ImbPipeline
    from imblearn.under_sampling import TomekLinks
    
    skewed_features = ['away_xg', 'referee_avg_cards_history', 'B365H', 'B365D', 'B365A', 'h_l5_fls', 'a_l5_fls', 'h_l5_xg', 'a_l5_xg', 'h_l5_xga', 'a_l5_xga']
    skewed_in_features = [f for f in skewed_features if f in FEATURES]
    standard_in_features = [f for f in FEATURES if f not in skewed_in_features]
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('skewed', ImbPipeline([
                ('imputer', KNNImputer(n_neighbors=5, weights='distance')),
                ('yeo_johnson', PowerTransformer(method='yeo-johnson', standardize=True))
            ]), skewed_in_features),
            ('standard', ImbPipeline([
                ('imputer', KNNImputer(n_neighbors=5, weights='distance')),
                ('scaler', StandardScaler())
            ]), standard_in_features)
        ],
        remainder='passthrough'
    )
    
    steps = [('preprocessor', preprocessor)]
    if use_tomek:
        steps.append(('sampler', TomekLinks()))
    steps.append(('classifier', classifier))
    
    return ImbPipeline(steps)

def main():
    if not os.path.exists(FEATURES_PATH):
        print(f"[Error] No se encontró el dataset {FEATURES_PATH}")
        return
        
    df = pd.read_csv(FEATURES_PATH)
    df = df[df['game_id'].astype(str) != '0'].reset_index(drop=True)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date').reset_index(drop=True)
    df = prepare_targets(df)
    
    X = df[FEATURES]
    y = df['target_1x2']
    
    tscv = TimeSeriesSplit(n_splits=5)
    
    # Cargar hiperparámetros optimizados desde optimized_hyperparams.json
    import json
    json_path = os.path.join(MODELS_DIR, "optimized_hyperparams.json")
    if os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            optimized_data = json.load(f)
        opt_params = optimized_data["1X2 (Match Winner)"]["Logistic Regression (Elastic Net)"]["best_params"]
    else:
        opt_params = {"C": 0.0032, "l1_ratio": 0.0553}
        
    clf_base = LogisticRegression(penalty='elasticnet', solver='saga', l1_ratio=0.5, C=0.1, max_iter=5000, random_state=42)
    clf_opt = LogisticRegression(penalty='elasticnet', solver='saga', l1_ratio=opt_params["l1_ratio"], C=opt_params["C"], max_iter=5000, random_state=42)
    
    pipe_base = create_pipeline(clf_base, use_tomek=False)
    pipe_opt = create_pipeline(clf_opt, use_tomek=True)
    
    all_y_test = []
    preds_base = []
    preds_opt = []
    
    # Validación cruzada temporal acumulando predicciones de prueba
    for train_idx, test_idx in tscv.split(X):
        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
        
        all_y_test.extend(y_test)
        
        # Ajustar y predecir Baseline
        pipe_base.fit(X_train, y_train)
        preds_base.extend(pipe_base.predict(X_test))
        
        # Ajustar y predecir Optuna
        pipe_opt.fit(X_train, y_train)
        preds_opt.extend(pipe_opt.predict(X_test))
        
    all_y_test = np.array(all_y_test)
    preds_base = np.array(preds_base)
    preds_opt = np.array(preds_opt)
    
    # Calcular reportes de clasificación
    report_base = classification_report(all_y_test, preds_base, output_dict=True)
    report_opt = classification_report(all_y_test, preds_opt, output_dict=True)
    
    classes = ['Visitante (0)', 'Empate (1)', 'Local (2)']
    
    # Extraer métricas por clase
    prec_base = [report_base[str(i)]['precision'] for i in range(3)]
    rec_base = [report_base[str(i)]['recall'] for i in range(3)]
    f1_base = [report_base[str(i)]['f1-score'] for i in range(3)]
    
    prec_opt = [report_opt[str(i)]['precision'] for i in range(3)]
    rec_opt = [report_opt[str(i)]['recall'] for i in range(3)]
    f1_opt = [report_opt[str(i)]['f1-score'] for i in range(3)]
    
    # Conteos de predicciones
    unique_true, counts_true = np.unique(all_y_test, return_counts=True)
    unique_pb, counts_pb = np.unique(preds_base, return_counts=True)
    unique_po, counts_po = np.unique(preds_opt, return_counts=True)
    
    # Mapear conteos a las clases fijas
    counts_true_map = {0: 0, 1: 0, 2: 0}
    counts_pb_map = {0: 0, 1: 0, 2: 0}
    counts_po_map = {0: 0, 1: 0, 2: 0}
    
    for u, c in zip(unique_true, counts_true): counts_true_map[u] = c
    for u, c in zip(unique_pb, counts_pb): counts_pb_map[u] = c
    for u, c in zip(unique_po, counts_po): counts_po_map[u] = c
    
    print("\nReporte Baseline:")
    print(classification_report(all_y_test, preds_base, target_names=classes))
    
    print("Reporte Optuna:")
    print(classification_report(all_y_test, preds_opt, target_names=classes))
    
    # Crear gráfico
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))
    for ax in axes:
        ax.grid(True, linestyle='--', alpha=0.5, zorder=0)
        ax.set_axisbelow(True)
    
    # Gráfico 1: Métricas de Empate (F1 y Recall) comparadas
    x = np.arange(len(classes))
    width = 0.35
    
    # Plot de F1-Score
    axes[0].bar(x - width/2, f1_base, width, label='Baseline', color='#4F46E5', alpha=0.85)
    axes[0].bar(x + width/2, f1_opt, width, label='Optuna (Optimizado)', color='#10B981', alpha=0.85)
    axes[0].set_ylabel('F1-Score', fontsize=12, fontweight='bold')
    axes[0].set_title('Comparativa de F1-Score por Clase (1X2)\n(El colapso de la clase Empate)', fontsize=14, fontweight='bold', pad=15)
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(classes, fontsize=11)
    axes[0].legend(frameon=True, facecolor='white', edgecolor='none')
    axes[0].set_ylim(0, 0.7)
    
    # Anotar valores sobre las barras
    for i, v in enumerate(f1_base):
        axes[0].text(i - width/2, v + 0.01, f"{v:.4f}", ha='center', va='bottom', fontsize=10, color='#1E293B')
    for i, v in enumerate(f1_opt):
        axes[0].text(i + width/2, v + 0.01, f"{v:.4f}", ha='center', va='bottom', fontsize=10, color='#1E293B')

    # Gráfico 2: Distribución de Predicciones vs Realidad
    # Queremos mostrar cuántos partidos reales hay de cada clase, y cuántos predice cada modelo.
    labels = ['Visitante', 'Empate', 'Local']
    true_counts = [counts_true_map[0], counts_true_map[1], counts_true_map[2]]
    pb_counts = [counts_pb_map[0], counts_pb_map[1], counts_pb_map[2]]
    po_counts = [counts_po_map[0], counts_po_map[1], counts_po_map[2]]
    
    x_dist = np.arange(len(labels))
    w_dist = 0.25
    
    axes[1].bar(x_dist - w_dist, true_counts, w_dist, label='Frecuencia Real (Datos)', color='#64748B', alpha=0.8)
    axes[1].bar(x_dist, pb_counts, w_dist, label='Predicciones Baseline', color='#4F46E5', alpha=0.85)
    axes[1].bar(x_dist + w_dist, po_counts, w_dist, label='Predicciones Optuna', color='#10B981', alpha=0.85)
    
    axes[1].set_ylabel('Cantidad de Partidos', fontsize=12, fontweight='bold')
    axes[1].set_title('Frecuencia Real de Resultados vs. Predicciones\n(¿Por qué sube la exactitud general?)', fontsize=14, fontweight='bold', pad=15)
    axes[1].set_xticks(x_dist)
    axes[1].set_xticklabels(labels, fontsize=11)
    axes[1].legend(frameon=True, facecolor='white', edgecolor='none')
    
    # Anotar valores sobre las barras de distribución
    for i, v in enumerate(true_counts):
        axes[1].text(i - w_dist, v + 15, str(v), ha='center', va='bottom', fontsize=9, color='#1E293B')
    for i, v in enumerate(pb_counts):
        axes[1].text(i, v + 15, str(v), ha='center', va='bottom', fontsize=9, color='#1E293B')
    for i, v in enumerate(po_counts):
        axes[1].text(i + w_dist, v + 15, str(v), ha='center', va='bottom', fontsize=9, color='#1E293B')
        
    plt.tight_layout()
    
    # Guardar gráfico
    output_dir = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "Carpeta_Presentacion"))
    os.makedirs(output_dir, exist_ok=True)
    fig_path = os.path.join(output_dir, "33_Explicacion_F1_1X2.png")
    plt.savefig(fig_path, dpi=300, bbox_inches='tight')
    print(f"\n[OK] Gráfico guardado exitosamente en: {fig_path}")

if __name__ == "__main__":
    main()
