import pandas as pd
import numpy as np
import os
import sys
import matplotlib.pyplot as plt

# Asegurar que el directorio base esté en el path para importar src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.config import FEATURES_PATH, TARGETS, BASE_DIR

def prepare_targets(df):
    df_out = df.copy()
    df_out['target_1x2'] = df_out['result_1x2'].astype(int)
    df_out['target_dc_1X'] = (df_out['result_1x2'] >= 1).astype(int)
    df_out['target_dc_X2'] = (df_out['result_1x2'] <= 1).astype(int)
    df_out['target_over_2_5_goals'] = (df_out['total_goals'] > 2.5).astype(int)
    df_out['target_under_2_5_goals'] = (df_out['total_goals'] <= 2.5).astype(int)
    df_out['target_btts'] = df_out['btts'].astype(int)
    df_out['target_btts_no'] = (df_out['btts'] == 0).astype(int)
    df_out['target_home_clean_sheet'] = (df_out['away_goals'] == 0).astype(int)
    return df_out

def main():
    if not os.path.exists(FEATURES_PATH):
        print(f"[Error] No se encontró el dataset {FEATURES_PATH}")
        return
        
    df = pd.read_csv(FEATURES_PATH)
    # Filtrar registros nulos de partidos no jugados (game_id != '0')
    df = df[df['game_id'].astype(str) != '0'].reset_index(drop=True)
    df = prepare_targets(df)
    
    # Lista de targets a analizar con nombres estéticos
    markets = [
        {"name": "1X2 (Match Winner)", "col": "target_1x2", "type": "multiclass"},
        {"name": "Doble Oportunidad 1X", "col": "target_dc_1X", "type": "binary"},
        {"name": "Doble Oportunidad X2", "col": "target_dc_X2", "type": "binary"},
        {"name": "Over 2.5 Goals", "col": "target_over_2_5_goals", "type": "binary"},
        {"name": "Under 2.5 Goals", "col": "target_under_2_5_goals", "type": "binary"},
        {"name": "Ambos Anotan (BTTS)", "col": "target_btts", "type": "binary"},
        {"name": "BTTS - No", "col": "target_btts_no", "type": "binary"},
        {"name": "Valla Invicta Local", "col": "target_home_clean_sheet", "type": "binary"}
    ]
    
    # Configurar la figura (2 filas x 4 columnas)
    fig, axes = plt.subplots(2, 4, figsize=(20, 10))
    axes = axes.flatten()
    
    # Paleta de colores Premium
    c_class_1 = '#4F46E5' # Indigo para clase 1 (Sí)
    c_class_0 = '#94A3B8' # Slate Gray para clase 0 (No)
    
    c_1x2_home = '#3B82F6' # Azul para Local (2)
    c_1x2_draw = '#64748B' # Slate Gray para Empate (1)
    c_1x2_away = '#F59E0B' # Ámbar para Visitante (0)

    for i, m in enumerate(markets):
        ax = axes[i]
        col_data = df[m["col"]]
        total = len(col_data)
        
        # Activar grilla de fondo sutil
        ax.grid(True, linestyle='--', alpha=0.3, zorder=0)
        ax.set_axisbelow(True)
        
        if m["type"] == "multiclass":
            # 1X2 tiene 3 clases: 0 (Visitante), 1 (Empate), 2 (Local)
            counts = col_data.value_counts().sort_index()
            # Asegurar que existan las 3 clases
            for c_val in [0, 1, 2]:
                if c_val not in counts:
                    counts[c_val] = 0
            
            labels = ['Visitante (0)', 'Empate (1)', 'Local (2)']
            percentages = [counts[0]/total * 100, counts[1]/total * 100, counts[2]/total * 100]
            colors = [c_1x2_away, c_1x2_draw, c_1x2_home]
            
            bars = ax.bar(labels, percentages, color=colors, alpha=0.9, width=0.6, edgecolor='none', zorder=3)
            ax.set_ylim(0, 60)
            
            # Anotar porcentajes y cantidades
            for bar, pct, cnt in zip(bars, percentages, [counts[0], counts[1], counts[2]]):
                ax.text(bar.get_x() + bar.get_width()/2, pct + 1, f"{pct:.1f}%\n({cnt})", 
                        ha='center', va='bottom', fontsize=10, fontweight='bold', color='#1E293B')
                
        else:
            # Mercados binarios: 0 (No/Negativo) y 1 (Sí/Positivo)
            counts = col_data.value_counts().sort_index()
            for c_val in [0, 1]:
                if c_val not in counts:
                    counts[c_val] = 0
            
            labels = ['No (0)', 'Sí (1)']
            percentages = [counts[0]/total * 100, counts[1]/total * 100]
            colors = [c_class_0, c_class_1]
            
            bars = ax.bar(labels, percentages, color=colors, alpha=0.9, width=0.5, edgecolor='none', zorder=3)
            ax.set_ylim(0, 100)
            
            # Anotar porcentajes y cantidades
            for bar, pct, cnt in zip(bars, percentages, [counts[0], counts[1]]):
                ax.text(bar.get_x() + bar.get_width()/2, pct + 1, f"{pct:.1f}%\n({cnt})", 
                        ha='center', va='bottom', fontsize=10, fontweight='bold', color='#1E293B')
        
        # Estética del Título y Bordes
        ax.set_title(m["name"], fontsize=13, fontweight='bold', pad=12, color='#1E293B')
        ax.tick_params(axis='both', which='major', labelsize=10)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#CBD5E1')
        ax.spines['bottom'].set_color('#CBD5E1')
        ax.set_ylabel('Porcentaje (%)', fontsize=10, color='#64748B')
        
    plt.suptitle('Distribución y Desbalanceo de Clases en los 8 Mercados de Apuestas\n(Premier League - N = 3,389 partidos evaluados)', 
                 fontsize=18, fontweight='bold', y=0.98, color='#0F172A')
    
    plt.tight_layout(rect=[0, 0.03, 1, 0.94])
    
    # Ruta de destino
    output_dir = r"c:\Users\sergi\Desktop\datascience\Carpeta_Presentacion"
    os.makedirs(output_dir, exist_ok=True)
    fig_path = os.path.join(output_dir, "34_Desbalanceo_Clases_Mercados.png")
    
    plt.savefig(fig_path, dpi=300, bbox_inches='tight')
    print(f"\n[OK] Gráfico de desbalanceo de clases guardado en: {fig_path}")

if __name__ == "__main__":
    main()
