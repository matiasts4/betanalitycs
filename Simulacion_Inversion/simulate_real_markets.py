import pandas as pd
import numpy as np
import sys
import os

# Configurar rutas para importar desde archive/pl-predictor
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'Desktop', 'datascience')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'Desktop', 'datascience', 'Simulacion_Inversion')))

from simular_estrategias_apuestas import run_single_simulation

csv_path = "d:/datascience/Simulacion_Inversion/predicciones_prueba_calibradas.csv"
df = pd.read_csv(csv_path)

# Modificar run_single_simulation para un portafolio de solo 5 mercados reales
def run_real_only_portfolio_simulation(sim_df, initial_bankroll=1000.0, edge_threshold=0.05, staking_strategy='quarter', cal_mode='uncal'):
    bankroll = initial_bankroll
    history = [bankroll]
    
    bets_count = 0
    wins_count = 0
    wagered = 0.0
    profit = 0.0
    
    for idx, row in sim_df.iterrows():
        p_home = row[f'p_home_{cal_mode}']
        p_draw = row[f'p_draw_{cal_mode}']
        p_away = row[f'p_away_{cal_mode}']
        p_dc1X = row[f'p_dc1X_{cal_mode}']
        p_dcX2 = row[f'p_dcX2_{cal_mode}']
        p_over = row[f'p_over_{cal_mode}']
        p_under = row[f'p_under_{cal_mode}']
        
        # Solo mercados reales (1X2, Over/Under, Double Chance)
        evs = {
            'home': {'ev': p_home * row['B365H'] - 1, 'odd': row['B365H'], 'prob': p_home, 'win': (row['target_1x2'] == 2)},
            'draw': {'ev': p_draw * row['B365D'] - 1, 'odd': row['B365D'], 'prob': p_draw, 'win': (row['target_1x2'] == 1)},
            'away': {'ev': p_away * row['B365A'] - 1, 'odd': row['B365A'], 'prob': p_away, 'win': (row['target_1x2'] == 0)},
            'dc_1X': {'ev': p_dc1X * row['B365_1X'] - 1, 'odd': row['B365_1X'], 'prob': p_dc1X, 'win': (row['target_dc_1X'] == 1)},
            'dc_X2': {'ev': p_dcX2 * row['B365_X2'] - 1, 'odd': row['B365_X2'], 'prob': p_dcX2, 'win': (row['target_dc_X2'] == 1)},
            'over': {'ev': p_over * row['B365>2.5'] - 1, 'odd': row['B365>2.5'], 'prob': p_over, 'win': (row['target_over_2_5_goals'] == 1)},
            'under': {'ev': p_under * row['B365<2.5'] - 1, 'odd': row['B365<2.5'], 'prob': p_under, 'win': (row['target_under_2_5_goals'] == 1)}
        }
        
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
            elif staking_strategy == 'half':
                f_star = 0.5 * (ev / (odd - 1))
                f_star = min(max(f_star, 0.0), 0.05)
                stake = f_star * bankroll
            elif staking_strategy == 'quarter':
                f_star = 0.25 * (ev / (odd - 1))
                f_star = min(max(f_star, 0.0), 0.025)
                stake = f_star * bankroll
            elif staking_strategy == 'edge':
                f_star = 0.5 * ev
                f_star = min(max(f_star, 0.0), 0.05)
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
        
    h_arr = np.array(history)
    peaks = np.maximum.accumulate(h_arr)
    peaks = np.where(peaks == 0, 1.0, peaks)
    drawdowns = (peaks - h_arr) / peaks
    max_dd = float(np.max(drawdowns) * 100)
    
    roi = (profit / wagered * 100) if wagered > 0 else 0.0
    win_rate = (wins_count / bets_count * 100) if bets_count > 0 else 0.0
    
    return {
        'final_bankroll': bankroll,
        'roi': roi,
        'bets': bets_count,
        'win_rate': win_rate,
        'max_dd': max_dd
    }

print("Simulating Portfolio with 5 Real Markets (Flat Stake - 1%):")
for cal_mode in ['uncal', 'iso', 'sig']:
    res = run_real_only_portfolio_simulation(df, initial_bankroll=1000.0, edge_threshold=0.05, staking_strategy='flat', cal_mode=cal_mode)
    print(f"  Cal={cal_mode.upper():<5} | Banca Final=${res['final_bankroll']:.2f} | ROI={res['roi']:.2f}% | Apuestas={res['bets']} | WinRate={res['win_rate']:.2f}% | MaxDD={res['max_dd']:.2f}%")

print("\nSimulating Portfolio with 5 Real Markets (Quarter Kelly):")
for cal_mode in ['uncal', 'iso', 'sig']:
    res = run_real_only_portfolio_simulation(df, initial_bankroll=1000.0, edge_threshold=0.05, staking_strategy='quarter', cal_mode=cal_mode)
    print(f"  Cal={cal_mode.upper():<5} | Banca Final=${res['final_bankroll']:.2f} | ROI={res['roi']:.2f}% | Apuestas={res['bets']} | WinRate={res['win_rate']:.2f}% | MaxDD={res['max_dd']:.2f}%")
