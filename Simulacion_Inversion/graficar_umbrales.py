import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

def run_portfolio_simulation(sim_df, edge_threshold, cal_mode='iso'):
    bankroll = 1000.0
    history = [bankroll]
    
    for idx, row in sim_df.iterrows():
        p_home = row[f'p_home_{cal_mode}']
        p_draw = row[f'p_draw_{cal_mode}']
        p_away = row[f'p_away_{cal_mode}']
        p_dc1X = row[f'p_dc1X_{cal_mode}']
        p_dcX2 = row[f'p_dcX2_{cal_mode}']
        p_over = row[f'p_over_{cal_mode}']
        p_under = row[f'p_under_{cal_mode}']
        
        evs = {
            'home': {'ev': p_home * row['B365H'] - 1, 'odd': row['B365H'], 'win': (row['target_1x2'] == 2)},
            'draw': {'ev': p_draw * row['B365D'] - 1, 'odd': row['B365D'], 'win': (row['target_1x2'] == 1)},
            'away': {'ev': p_away * row['B365A'] - 1, 'odd': row['B365A'], 'win': (row['target_1x2'] == 0)},
            'dc_1X': {'ev': p_dc1X * row['B365_1X'] - 1, 'odd': row['B365_1X'], 'win': (row['target_dc_1X'] == 1)},
            'dc_X2': {'ev': p_dcX2 * row['B365_X2'] - 1, 'odd': row['B365_X2'], 'win': (row['target_dc_X2'] == 1)},
            'over': {'ev': p_over * row['B365>2.5'] - 1, 'odd': row['B365>2.5'], 'win': (row['target_over_2_5_goals'] == 1)},
            'under': {'ev': p_under * row['B365<2.5'] - 1, 'odd': row['B365<2.5'], 'win': (row['target_under_2_5_goals'] == 1)}
        }
        
        best_bet_name = max(evs, key=lambda k: evs[k]['ev'])
        best_ev_info = evs[best_bet_name]
        
        if best_ev_info['ev'] >= edge_threshold and bankroll > 0:
            odd = best_ev_info['odd']
            win = best_ev_info['win']
            stake = 10.0  # Flat Staking 1%
            
            if bankroll >= stake:
                if win:
                    net_profit = stake * (odd - 1)
                else:
                    net_profit = -stake
                bankroll += net_profit
                
        history.append(bankroll)
        
    return history

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(current_dir, "predicciones_prueba_calibradas.csv")
    df = pd.read_csv(csv_path)
    
    # Lista de umbrales a probar
    thresholds = [0.05, 0.08, 0.10, 0.12, 0.15, 0.20]
    colors = {
        0.05: '#718096', # Gris (Slate)
        0.08: '#ED8936', # Naranja
        0.10: '#3182CE', # Azul (Sleek Blue)
        0.12: '#E53E3E', # Rojo
        0.15: '#805AD5', # Púrpura
        0.20: '#319795'  # Teal
    }
    
    dates = pd.to_datetime(df['date'])
    first_date = dates.iloc[0] - pd.Timedelta(days=1)
    plot_dates = [first_date] + list(dates)
    
    plt.figure(figsize=(12, 7))
    plt.rcParams['font.family'] = 'sans-serif'
    
    print("Corriendo simulaciones de umbrales...")
    for t in thresholds:
        history = run_portfolio_simulation(df, t, cal_mode='iso')
        
        # Calcular estadísticas rápidas
        final_b = history[-1]
        profit = final_b - 1000.0
        # Contar cuántas apuestas se colocaron (cuando cambia el valor de la banca)
        # Nota: La banca solo cambia si se coloca una apuesta.
        bets_count = sum(1 for i in range(1, len(history)) if history[i] != history[i-1])
        wagered = bets_count * 10.0
        roi = (profit / wagered * 100) if wagered > 0 else 0.0
        
        label_text = f"Umbral {t:.2f} (Bets={bets_count}, Banca Final=${final_b:.2f}, ROI={roi:.2f}%)"
        
        # Resaltar el umbral del 10% que dio el mejor resultado o el del 10%
        linewidth = 2.5 if t in [0.08, 0.10] else 1.5
        alpha = 1.0 if t in [0.08, 0.10] else 0.8
        
        plt.plot(plot_dates, history, label=label_text, color=colors[t], linewidth=linewidth, alpha=alpha)
        
    plt.axhline(y=1000.0, color='black', linestyle=':', alpha=0.6)
    
    plt.title('Comparativa de Umbrales de Ventaja (Edge) en Portafolio Real Combinado\nFlat Staking (1% de Banca Inicial = $10 USD) | Calibración Isotónica', fontsize=13, fontweight='bold', pad=15)
    plt.xlabel('Línea Temporal de Partidos', fontsize=10)
    plt.ylabel('Banca (USD)', fontsize=10)
    plt.grid(True, linestyle='--', alpha=0.5, color='#CBD5E0')
    
    # Formatear eje Y
    def dollar_format(x, pos):
        return f"${x:.0f}"
    plt.gca().yaxis.set_major_formatter(FuncFormatter(dollar_format))
    
    plt.legend(frameon=True, facecolor='white', edgecolor='#E2E8F0', loc='lower left', fontsize=9.5)
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    
    fig_path = os.path.join(current_dir, "38_Simulacion_Portafolio_Real_Umbrales.png")
    plt.tight_layout()
    plt.savefig(fig_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[OK] Gráfico guardado en: {fig_path}")
    
    # Copiar a Carpeta_Presentacion
    pres_fig_path = os.path.abspath(os.path.join(current_dir, "..", "Carpeta_Presentacion", "38_Simulacion_Portafolio_Real_Umbrales.png"))
    try:
        import shutil
        shutil.copy(fig_path, pres_fig_path)
        print(f"[OK] Gráfico copiado a carpeta de presentación: {pres_fig_path}")
    except Exception as e:
        print(f"[Aviso] No se pudo copiar el gráfico: {e}")

if __name__ == "__main__":
    main()
