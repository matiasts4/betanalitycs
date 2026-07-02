import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

def run_simulation(sim_df, include_synthetic=True, staking_strategy='flat', cal_mode='iso', 
                   min_odd=1.0, max_odd=100.0, min_prob=0.0, edge_threshold=0.05, 
                   initial_bankroll=1000.0):
    bankroll = initial_bankroll
    history = [bankroll]
    
    bets_count = 0
    wins_count = 0
    wagered = 0.0
    profit = 0.0
    
    for idx, row in sim_df.iterrows():
        # Obtener probabilidades y cuotas
        p_home = row[f'p_home_{cal_mode}']
        p_draw = row[f'p_draw_{cal_mode}']
        p_away = row[f'p_away_{cal_mode}']
        p_dc1X = row[f'p_dc1X_{cal_mode}']
        p_dcX2 = row[f'p_dcX2_{cal_mode}']
        p_over = row[f'p_over_{cal_mode}']
        p_under = row[f'p_under_{cal_mode}']
        
        # Opciones reales
        all_options = {
            'home': {'prob': p_home, 'odd': row['B365H'], 'win': (row['target_1x2'] == 2)},
            'draw': {'prob': p_draw, 'odd': row['B365D'], 'win': (row['target_1x2'] == 1)},
            'away': {'prob': p_away, 'odd': row['B365A'] if 'B365A' in row else row['B365_X2'], 'win': (row['target_1x2'] == 0)},
            'dc_1X': {'prob': p_dc1X, 'odd': row['B365_1X'], 'win': (row['target_dc_1X'] == 1)},
            'dc_X2': {'prob': p_dcX2, 'odd': row['B365_X2'], 'win': (row['target_dc_X2'] == 1)},
            'over': {'prob': p_over, 'odd': row['B365>2.5'], 'win': (row['target_over_2_5_goals'] == 1)},
            'under': {'prob': p_under, 'odd': row['B365<2.5'], 'win': (row['target_under_2_5_goals'] == 1)}
        }
        
        # Opciones sintéticas (si aplica)
        if include_synthetic:
            p_btts = row[f'p_btts_{cal_mode}']
            p_bttsno = row[f'p_bttsno_{cal_mode}']
            p_hcs = row[f'p_hcs_{cal_mode}']
            all_options.update({
                'btts': {'prob': p_btts, 'odd': row['B365_BTTS_Yes'], 'win': (row['target_btts'] == 1)},
                'btts_no': {'prob': p_bttsno, 'odd': row['B365_BTTS_No'], 'win': (row['target_btts_no'] == 1)},
                'hcs': {'prob': p_hcs, 'odd': row['B365_HCS'], 'win': (row['target_home_clean_sheet'] == 1)}
            })
            
        filtered_evs = {}
        for name, opt in all_options.items():
            prob = opt['prob']
            odd = opt['odd']
            ev = prob * odd - 1
            
            # Filtro de cuotas
            if odd < min_odd or odd > max_odd:
                continue
                
            # Filtro de probabilidad
            if prob < min_prob:
                continue
                
            filtered_evs[name] = {
                'ev': ev,
                'odd': odd,
                'win': opt['win']
            }
            
        if not filtered_evs:
            history.append(bankroll)
            continue
            
        best_bet_name = max(filtered_evs, key=lambda k: filtered_evs[k]['ev'])
        best_bet = filtered_evs[best_bet_name]
        
        if best_bet['ev'] >= edge_threshold and bankroll > 0:
            odd = best_bet['odd']
            win = best_bet['win']
            stake = 10.0
            
            if bankroll >= stake and stake > 0.10:
                bets_count += 1
                wagered += stake
                if win:
                    net_profit = stake * (odd - 1)
                    wins_count += 1
                else:
                    net_profit = -stake
                bankroll += net_profit
                profit += net_profit
                
        history.append(bankroll)
        
    roi = (profit / wagered * 100) if wagered > 0 else 0.0
    return history, roi, bets_count

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(current_dir, "predicciones_prueba_calibradas.csv")
    df = pd.read_csv(csv_path)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date').reset_index(drop=True)
    
    dates = [df['date'].iloc[0] - pd.Timedelta(days=1)] + list(df['date'])
    
    # Configuraciones óptimas a graficar
    configs = [
        # (include_synthetic, min_odd, max_odd, min_prob, Label, Color, Style)
        (False, 1.0, 100.0, 0.0, 'Línea Base Reales (Sin Filtros)', '#718096', ':'),         # Slate, dotted
        (False, 1.0, 2.0, 0.0, 'Reales: Solo Favoritos (Odds <= 2.0)', '#4299E1', '--'),      # Light Blue, dashed
        (False, 1.0, 100.0, 0.90, 'Reales: Ultra-Conservador (Prob >= 90%)', '#805AD5', '-.'), # Purple, dash-dot
        (True, 1.0, 100.0, 0.10, 'Portafolio 8: Óptimo Agresivo (Prob >= 10%)', '#E53E3E', '-'), # Red, solid
        (True, 2.5, 100.0, 0.0, 'Portafolio 8: Especulativo (Odds >= 2.50)', '#ED8936', '-'),  # Orange, solid
        (True, 1.0, 100.0, 0.30, 'Portafolio 8: Defensivo (Prob >= 30%)', '#38A169', '-')      # Green, solid
    ]
    
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'DejaVu Sans']
    
    fig, ax = plt.subplots(figsize=(14, 8))
    
    print("Simulando configuraciones óptimas...")
    for include_synth, min_odd, max_odd, min_prob, label, color, style in configs:
        history, roi, bets = run_simulation(
            df, include_synthetic=include_synth, staking_strategy='flat',
            cal_mode='iso', min_odd=min_odd, max_odd=max_odd, min_prob=min_prob
        )
        
        label_text = f"{label} (ROI: {roi:.2f}%, Bets: {bets}, Banca: ${history[-1]:.0f})"
        linewidth = 2.5 if include_synth and min_prob == 0.10 else 1.8
        
        ax.plot(dates, history, label=label_text, color=color, linestyle=style, linewidth=linewidth)
        print(f"  > {label}: Banca Final = ${history[-1]:.2f} | ROI = {roi:.2f}% | Bets = {bets}")
        
    ax.axhline(y=1000.0, color='#718096', linestyle=':', alpha=0.6)
    ax.set_title('Frontera Eficiente: Comparativa de las Mejores Configuraciones de Inversión\n(Staking: Flat 1% | Calibración Isotónica | Contraste Portafolio Real vs Portafolio 8)', fontsize=15, fontweight='bold', pad=15)
    ax.set_xlabel('Línea Temporal de Partidos', fontsize=11)
    ax.set_ylabel('Banca (USD)', fontsize=11)
    ax.grid(True, linestyle='--', alpha=0.4, color='#CBD5E0')
    
    # Leyenda muy premium
    ax.legend(frameon=True, facecolor='white', edgecolor='#E2E8F0', loc='upper left', fontsize=10)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#718096')
    ax.spines['bottom'].set_color('#718096')
    
    def dollar_format(x, pos):
        return f"${x:.0f}"
    ax.yaxis.set_major_formatter(FuncFormatter(dollar_format))
    
    plt.tight_layout()
    fig_path = os.path.abspath(os.path.join(current_dir, "..", "Carpeta_Presentacion", "45_Simulacion_Configuraciones_Optimas.png"))
    plt.savefig(fig_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[OK] Gráfico de mejores configuraciones guardado en: {fig_path}")

if __name__ == '__main__':
    main()
