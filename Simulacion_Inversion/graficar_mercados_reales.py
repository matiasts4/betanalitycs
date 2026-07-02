import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

def run_single_simulation(sim_df, market_type, initial_bankroll=1000.0, edge_threshold=0.05, staking_strategy='flat', cal_mode='uncal'):
    bankroll = initial_bankroll
    history = [bankroll]
    
    bets_count = 0
    wins_count = 0
    wagered = 0.0
    profit = 0.0
    
    for idx, row in sim_df.iterrows():
        evs = {}
        
        if market_type == '1x2':
            p_home = row[f'p_home_{cal_mode}']
            p_draw = row[f'p_draw_{cal_mode}']
            p_away = row[f'p_away_{cal_mode}']
            
            evs = {
                'home': {'ev': p_home * row['B365H'] - 1, 'odd': row['B365H'], 'prob': p_home, 'win': (row['target_1x2'] == 2)},
                'draw': {'ev': p_draw * row['B365D'] - 1, 'odd': row['B365D'], 'prob': p_draw, 'win': (row['target_1x2'] == 1)},
                'away': {'ev': p_away * row['B365A'] - 1, 'odd': row['B365A'], 'prob': p_away, 'win': (row['target_1x2'] == 0)}
            }
        elif market_type == 'double_chance_1x':
            p_dc1X = row[f'p_dc1X_{cal_mode}']
            ev_dc1X = p_dc1X * row['B365_1X'] - 1
            evs = {
                'dc_1X': {'ev': ev_dc1X, 'odd': row['B365_1X'], 'prob': p_dc1X, 'win': (row['target_dc_1X'] == 1)}
            }
        elif market_type == 'double_chance_x2':
            p_dcX2 = row[f'p_dcX2_{cal_mode}']
            ev_dcX2 = p_dcX2 * row['B365_X2'] - 1
            evs = {
                'dc_X2': {'ev': ev_dcX2, 'odd': row['B365_X2'], 'prob': p_dcX2, 'win': (row['target_dc_X2'] == 1)}
            }
        elif market_type == 'over':
            p_over = row[f'p_over_{cal_mode}']
            ev_over = p_over * row['B365>2.5'] - 1
            evs = {
                'over': {'ev': ev_over, 'odd': row['B365>2.5'], 'prob': p_over, 'win': (row['target_over_2_5_goals'] == 1)}
            }
        elif market_type == 'under':
            p_under = row[f'p_under_{cal_mode}']
            ev_under = p_under * row['B365<2.5'] - 1
            evs = {
                'under': {'ev': ev_under, 'odd': row['B365<2.5'], 'prob': p_under, 'win': (row['target_under_2_5_goals'] == 1)}
            }
        elif market_type == 'portfolio_real':
            # Portafolio que contiene unicamente los 5 mercados reales/arbitrados
            p_home = row[f'p_home_{cal_mode}']
            p_draw = row[f'p_draw_{cal_mode}']
            p_away = row[f'p_away_{cal_mode}']
            p_dc1X = row[f'p_dc1X_{cal_mode}']
            p_dcX2 = row[f'p_dcX2_{cal_mode}']
            p_over = row[f'p_over_{cal_mode}']
            p_under = row[f'p_under_{cal_mode}']
            
            evs = {
                'home': {'ev': p_home * row['B365H'] - 1, 'odd': row['B365H'], 'prob': p_home, 'win': (row['target_1x2'] == 2)},
                'draw': {'ev': p_draw * row['B365D'] - 1, 'odd': row['B365D'], 'prob': p_draw, 'win': (row['target_1x2'] == 1)},
                'away': {'ev': p_away * row['B365A'] - 1, 'odd': row['B365A'], 'prob': p_away, 'win': (row['target_1x2'] == 0)},
                'dc_1X': {'ev': p_dc1X * row['B365_1X'] - 1, 'odd': row['B365_1X'], 'prob': p_dc1X, 'win': (row['target_dc_1X'] == 1)},
                'dc_X2': {'ev': p_dcX2 * row['B365_X2'] - 1, 'odd': row['B365_X2'], 'prob': p_dcX2, 'win': (row['target_dc_X2'] == 1)},
                'over': {'ev': p_over * row['B365>2.5'] - 1, 'odd': row['B365>2.5'], 'prob': p_over, 'win': (row['target_over_2_5_goals'] == 1)},
                'under': {'ev': p_under * row['B365<2.5'] - 1, 'odd': row['B365<2.5'], 'prob': p_under, 'win': (row['target_under_2_5_goals'] == 1)}
            }
            
        if not evs:
            history.append(bankroll)
            continue
            
        best_bet_name = max(evs, key=lambda k: evs[k]['ev'])
        best_ev_info = evs[best_bet_name]
        
        if best_ev_info['ev'] >= edge_threshold and bankroll > 0:
            odd = best_ev_info['odd']
            prob = best_ev_info['prob']
            ev = best_ev_info['ev']
            win = best_ev_info['win']
            
            if staking_strategy == 'flat':
                stake = 10.0
            elif staking_strategy == 'kelly':
                f_star = ev / (odd - 1)
                f_star = min(max(f_star, 0.0), 0.10)
                stake = f_star * bankroll
            elif staking_strategy == 'quarter':
                f_star = 0.25 * (ev / (odd - 1))
                f_star = min(max(f_star, 0.0), 0.025)
                stake = f_star * bankroll
            else:
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
        
    return history

def plot_real_markets(df, staking_strategy='flat', filename='real_markets.png', title_suffix='(Flat Staking)'):
    market_types = [
        ('1x2', 'Ganador de Partido (1X2)'),
        ('double_chance_1x', 'Doble Oportunidad (1X)'),
        ('double_chance_x2', 'Doble Oportunidad (X2)'),
        ('over', 'Over 2.5 Goles'),
        ('under', 'Under 2.5 Goles'),
        ('portfolio_real', 'Portafolio Combinado Real')
    ]
    
    cal_modes = ['uncal', 'iso', 'sig']
    colors = {
        'uncal': '#718096', # Slate
        'iso': '#3182CE',   # Blue
        'sig': '#38A169'    # Green
    }
    labels = {
        'uncal': 'Sin Calibrar (Baseline)',
        'iso': 'Calibración Isotónica',
        'sig': 'Calibración Sigmoide (Platt)'
    }
    
    dates = pd.to_datetime(df['date'])
    # Prepend the first date minus 1 day to align with history index 0
    first_date = dates.iloc[0] - pd.Timedelta(days=1)
    plot_dates = [first_date] + list(dates)
    
    fig, axs = plt.subplots(3, 2, figsize=(16, 12))
    axs = axs.ravel()
    
    for idx, (m_type, m_title) in enumerate(market_types):
        ax = axs[idx]
        
        for c_mode in cal_modes:
            history = run_single_simulation(df, m_type, initial_bankroll=1000.0, edge_threshold=0.05, staking_strategy=staking_strategy, cal_mode=c_mode)
            ax.plot(plot_dates, history, label=labels[c_mode], color=colors[c_mode], linewidth=2.0)
            
        ax.axhline(y=1000.0, color='black', linestyle=':', alpha=0.6)
        
        ax.set_title(m_title, fontsize=12, fontweight='bold', pad=8)
        ax.set_xlabel('Línea Temporal', fontsize=9)
        ax.set_ylabel('Banca (USD)', fontsize=9)
        ax.grid(True, linestyle='--', alpha=0.5, color='#CBD5E0')
        ax.legend(frameon=True, facecolor='white', edgecolor='#E2E8F0', loc='lower left', fontsize=8.5)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        # Formatear eje Y
        def dollar_format(x, pos):
            return f"${x:.0f}"
        ax.yaxis.set_major_formatter(FuncFormatter(dollar_format))
        
    plt.suptitle(f'Evolución del Capital en Mercados con Cuotas Reales y de Arbitraje\nEstrategia: {title_suffix} | Banca Inicial: $1,000 USD', fontsize=15, fontweight='bold', y=0.98)
    plt.tight_layout()
    plt.subplots_adjust(top=0.92)
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    fig_path = os.path.join(current_dir, filename)
    plt.savefig(fig_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[OK] Gráfico guardado en: {fig_path}")
    
    # Copiar a Carpeta_Presentacion
    pres_fig_path = os.path.abspath(os.path.join(current_dir, "..", "Carpeta_Presentacion", filename))
    try:
        import shutil
        shutil.copy(fig_path, pres_fig_path)
        print(f"[OK] Gráfico copiado a carpeta de presentación: {pres_fig_path}")
    except Exception as e:
        print(f"[Aviso] No se pudo copiar el gráfico: {e}")

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(current_dir, "predicciones_prueba_calibradas.csv")
    df = pd.read_csv(csv_path)
    
    print("Generando gráficos para mercados reales bajo Flat Staking...")
    plot_real_markets(df, staking_strategy='flat', filename='36_Simulacion_Mercados_Reales_Flat.png', title_suffix='Flat Staking (1% de Banca)')
    
    print("\nGenerando gráficos para mercados reales bajo Quarter Kelly...")
    plot_real_markets(df, staking_strategy='quarter', filename='37_Simulacion_Mercados_Reales_Kelly.png', title_suffix='Quarter Kelly (Máx 2.5% de Banca)')

if __name__ == "__main__":
    main()
