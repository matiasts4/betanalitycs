import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

def run_simulation_with_filters(sim_df, staking_strategy='flat', cal_mode='iso', 
                                min_odd=1.0, max_odd=100.0, min_prob=0.0, min_kelly=0.0,
                                edge_threshold=0.05, initial_bankroll=1000.0):
    bankroll = initial_bankroll
    history = [bankroll]
    
    bets_count = 0
    wins_count = 0
    wagered = 0.0
    profit = 0.0
    
    for idx, row in sim_df.iterrows():
        # Obtener probabilidades y cuotas para las 10 opciones de apuesta
        p_home = row[f'p_home_{cal_mode}']
        p_draw = row[f'p_draw_{cal_mode}']
        p_away = row[f'p_away_{cal_mode}']
        p_dc1X = row[f'p_dc1X_{cal_mode}']
        p_dcX2 = row[f'p_dcX2_{cal_mode}']
        p_over = row[f'p_over_{cal_mode}']
        p_under = row[f'p_under_{cal_mode}']
        p_btts = row[f'p_btts_{cal_mode}']
        p_bttsno = row[f'p_bttsno_{cal_mode}']
        p_hcs = row[f'p_hcs_{cal_mode}']
        
        all_options = {
            'home': {'prob': p_home, 'odd': row['B365H'], 'win': (row['target_1x2'] == 2)},
            'draw': {'prob': p_draw, 'odd': row['B365D'], 'win': (row['target_1x2'] == 1)},
            'away': {'prob': p_away, 'odd': row['B365A'], 'win': (row['target_1x2'] == 0)},
            'dc_1X': {'prob': p_dc1X, 'odd': row['B365_1X'], 'win': (row['target_dc_1X'] == 1)},
            'dc_X2': {'prob': p_dcX2, 'odd': row['B365_X2'], 'win': (row['target_dc_X2'] == 1)},
            'over': {'prob': p_over, 'odd': row['B365>2.5'], 'win': (row['target_over_2_5_goals'] == 1)},
            'under': {'prob': p_under, 'odd': row['B365<2.5'], 'win': (row['target_under_2_5_goals'] == 1)}
        }
        
        filtered_evs = {}
        for name, opt in all_options.items():
            prob = opt['prob']
            odd = opt['odd']
            ev = prob * odd - 1
            
            # 1. Filtro de Cuotas
            if odd < min_odd or odd > max_odd:
                continue
                
            # 2. Filtro de Probabilidad Mínima
            if prob < min_prob:
                continue
                
            # 3. Filtro de Kelly
            f_star = ev / (odd - 1) if odd > 1.0 else 0.0
            if staking_strategy in ['kelly', 'quarter'] and f_star < min_kelly:
                continue
                
            # Guardar si pasa los filtros
            filtered_evs[name] = {
                'ev': ev,
                'odd': odd,
                'prob': prob,
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
            stake = 10.0 # Flat staking 1% de banca inicial ($1000)
            
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
    
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'DejaVu Sans']
    
    # ─────────────────────────────────────────────────────────────────────────
    # GRÁFICO 1: BARRIDO DE 10 FILTROS DE PROBABILIDAD MÍNIMA
    # ─────────────────────────────────────────────────────────────────────────
    print("Corriendo barrido de filtros de probabilidad...")
    prob_thresholds = [0.0, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90]
    
    fig, ax = plt.subplots(figsize=(13, 7.5))
    
    # Usar un mapa de colores degradado (de azul a naranja/rojo)
    cmap = plt.get_cmap('plasma')
    
    for idx, p_thresh in enumerate(prob_thresholds):
        color = cmap(idx / len(prob_thresholds))
        history, roi, bets = run_simulation_with_filters(
            df, staking_strategy='flat', cal_mode='iso',
            min_odd=1.0, max_odd=100.0, min_prob=p_thresh
        )
        label_text = f"Prob >= {p_thresh:.0%} (ROI: {roi:.2f}%, Bets: {bets})" if p_thresh > 0.0 else f"Sin Filtro (ROI: {roi:.2f}%, Bets: {bets})"
        ax.plot(dates, history, label=label_text, color=color, linewidth=2.0 if p_thresh in [0.0, 0.30] else 1.2)
        print(f"  > Prob >= {p_thresh:.0%}: Banca Final = ${history[-1]:.2f} | ROI = {roi:.2f}% | Bets = {bets}")
        
    ax.axhline(y=1000.0, color='#718096', linestyle=':', alpha=0.6)
    ax.set_title('Sensibilidad del Portafolio de Mercados Reales al Filtro de Probabilidad Mínima\n(Staking: Flat 1% | Calibración Isotónica | 10 Escenarios Evaluados)', fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel('Línea Temporal de Partidos', fontsize=11)
    ax.set_ylabel('Banca (USD)', fontsize=11)
    ax.grid(True, linestyle='--', alpha=0.4, color='#CBD5E0')
    
    # Colocar la leyenda de forma limpia
    ax.legend(frameon=True, facecolor='white', edgecolor='#E2E8F0', loc='upper left', fontsize=9.5, ncol=2)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#718096')
    ax.spines['bottom'].set_color('#718096')
    
    def dollar_format(x, pos):
        return f"${x:.0f}"
    ax.yaxis.set_major_formatter(FuncFormatter(dollar_format))
    
    plt.tight_layout()
    fig1_path = os.path.abspath(os.path.join(current_dir, "..", "Carpeta_Presentacion", "43_Sensibilidad_Filtro_Probabilidad.png"))
    plt.savefig(fig1_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[OK] Gráfico de sensibilidad de probabilidad guardado en: {fig1_path}")
    
    # ─────────────────────────────────────────────────────────────────────────
    # GRÁFICO 2: BARRIDO DE FILTROS DE RANGO DE CUOTAS
    # ─────────────────────────────────────────────────────────────────────────
    print("\nCorriendo barrido de filtros de rango de cuotas...")
    odds_configs = [
        ('Sin Filtros (1.0 - 100.0)', 1.0, 100.0, '#2D3748'),          # Slate oscuro
        ('Solo Favoritos (1.0 - 2.0)', 1.0, 2.0, '#3182CE'),            # Blue
        ('Favoritos y Empates (1.0 - 3.5)', 1.0, 3.5, '#4299E1'),      # Light Blue
        ('Solo Sorpresas (2.5 - 100.0)', 2.5, 100.0, '#E53E3E'),        # Red
        ('Rango Moderado (1.4 - 5.0)', 1.4, 5.0, '#ED8936'),            # Orange
        ('Rango Conservador (1.6 - 4.0)', 1.6, 4.0, '#38A169'),         # Green
        ('Rango Estrecho (1.8 - 3.0)', 1.8, 3.0, '#805AD5')             # Purple
    ]
    
    fig, ax = plt.subplots(figsize=(13, 7.5))
    
    for label, min_odd, max_odd, color in odds_configs:
        history, roi, bets = run_simulation_with_filters(
            df, staking_strategy='flat', cal_mode='iso',
            min_odd=min_odd, max_odd=max_odd, min_prob=0.0
        )
        ax.plot(dates, history, label=f"{label} (ROI: {roi:.2f}%, Bets: {bets})", color=color, linewidth=2.0 if min_odd==1.0 and max_odd==100.0 else 1.5)
        print(f"  > {label}: Banca Final = ${history[-1]:.2f} | ROI = {roi:.2f}% | Bets = {bets}")
        
    ax.axhline(y=1000.0, color='#718096', linestyle=':', alpha=0.6)
    ax.set_title('Sensibilidad del Portafolio de Mercados Reales a Filtros de Rango de Cuotas\n(Staking: Flat 1% | Calibración Isotónica | 7 Configuraciones de Mercado)', fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel('Línea Temporal de Partidos', fontsize=11)
    ax.set_ylabel('Banca (USD)', fontsize=11)
    ax.grid(True, linestyle='--', alpha=0.4, color='#CBD5E0')
    ax.legend(frameon=True, facecolor='white', edgecolor='#E2E8F0', loc='upper left', fontsize=9.5)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#718096')
    ax.spines['bottom'].set_color('#718096')
    ax.yaxis.set_major_formatter(FuncFormatter(dollar_format))
    
    plt.tight_layout()
    fig2_path = os.path.abspath(os.path.join(current_dir, "..", "Carpeta_Presentacion", "44_Sensibilidad_Filtro_Cuotas.png"))
    plt.savefig(fig2_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[OK] Gráfico de sensibilidad de cuotas guardado en: {fig2_path}")

if __name__ == '__main__':
    main()
