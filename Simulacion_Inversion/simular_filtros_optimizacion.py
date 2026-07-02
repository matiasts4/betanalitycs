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
        # Obtener probabilidades y armar cuotas para las 10 opciones de apuesta
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
            'under': {'prob': p_under, 'odd': row['B365<2.5'], 'win': (row['target_under_2_5_goals'] == 1)},
            'btts': {'prob': p_btts, 'odd': row['B365_BTTS_Yes'], 'win': (row['target_btts'] == 1)},
            'btts_no': {'prob': p_bttsno, 'odd': row['B365_BTTS_No'], 'win': (row['target_btts_no'] == 1)},
            'hcs': {'prob': p_hcs, 'odd': row['B365_HCS'], 'win': (row['target_home_clean_sheet'] == 1)}
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
                'f_star': f_star,
                'win': opt['win']
            }
            
        if not filtered_evs:
            history.append(bankroll)
            continue
            
        # Seleccionar la opción de mayor EV de las que pasaron los filtros
        best_bet_name = max(filtered_evs, key=lambda k: filtered_evs[k]['ev'])
        best_bet = filtered_evs[best_bet_name]
        
        if best_bet['ev'] >= edge_threshold and bankroll > 0:
            odd = best_bet['odd']
            ev = best_bet['ev']
            f_star = best_bet['f_star']
            win = best_bet['win']
            
            if staking_strategy == 'flat':
                stake = 10.0
            elif staking_strategy == 'kelly':
                f_star_capped = min(max(f_star, 0.0), 0.10)
                stake = f_star_capped * bankroll
            elif staking_strategy == 'quarter':
                f_star_scaled = 0.25 * f_star
                f_star_capped = min(max(f_star_scaled, 0.0), 0.025)
                stake = f_star_capped * bankroll
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
        
    # Calcular Max Drawdown
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
        'max_dd': max_dd,
        'history': history
    }

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(current_dir, "predicciones_prueba_calibradas.csv")
    df = pd.read_csv(csv_path)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date').reset_index(drop=True)
    
    # Grid search parameters
    odds_filters = [
        ('Sin Filtro', 1.0, 100.0),
        ('Moderado (1.4-5.0)', 1.4, 5.0),
        ('Conservador (1.6-4.0)', 1.6, 4.0)
    ]
    
    prob_filters = [
        ('Sin Filtro', 0.0),
        ('Prob >= 20%', 0.20),
        ('Prob >= 30%', 0.30),
        ('Prob >= 40%', 0.40)
    ]
    
    kelly_filters = [
        ('Sin Filtro', 0.0),
        ('Kelly >= 0.2%', 0.002),
        ('Kelly >= 0.4%', 0.004)
    ]
    
    strategies = ['flat', 'quarter']
    
    results = []
    
    print("Corriendo Grid Search para optimización de filtros...")
    for strat in strategies:
        for odd_name, min_odd, max_odd in odds_filters:
            for prob_name, min_prob in prob_filters:
                for k_name, min_k in kelly_filters:
                    # El filtro Kelly solo aplica a estrategias tipo Kelly
                    if strat == 'flat' and min_k > 0.0:
                        continue
                        
                    res = run_simulation_with_filters(
                        df, staking_strategy=strat, cal_mode='iso',
                        min_odd=min_odd, max_odd=max_odd, min_prob=min_prob, min_kelly=min_k
                    )
                    
                    results.append({
                        'Estrategia': strat.upper(),
                        'Filtro Cuotas': odd_name,
                        'Filtro Probabilidad': prob_name,
                        'Filtro Kelly': k_name if strat != 'flat' else 'N/A',
                        'Banca Final': res['final_bankroll'],
                        'ROI': res['roi'],
                        'Apuestas': res['bets'],
                        'Win Rate': res['win_rate'],
                        'Max Drawdown': res['max_dd']
                    })
                    
    results_df = pd.DataFrame(results)
    results_df.to_csv(os.path.join(current_dir, "reporte_optimizacion_filtros.csv"), index=False)
    print("[OK] Resultados consolidados guardados en: reporte_optimizacion_filtros.csv")
    
    # Mostrar Top 5 para Flat y Kelly por ROI
    print("\n==========================================================================================")
    print("                TOP 5 CONFIGURACIONES DE FILTROS BAJO FLAT STAKING")
    print("==========================================================================================")
    top_flat = results_df[results_df['Estrategia'] == 'FLAT'].sort_values('ROI', ascending=False).head(5)
    print(top_flat[['Filtro Cuotas', 'Filtro Probabilidad', 'Banca Final', 'ROI', 'Apuestas', 'Max Drawdown']].to_string(index=False))
    print("==========================================================================================")
    
    print("\n==========================================================================================")
    print("                TOP 5 CONFIGURACIONES DE FILTROS BAJO QUARTER KELLY")
    print("==========================================================================================")
    top_kelly = results_df[results_df['Estrategia'] == 'QUARTER'].sort_values('ROI', ascending=False).head(5)
    print(top_kelly[['Filtro Cuotas', 'Filtro Probabilidad', 'Filtro Kelly', 'Banca Final', 'ROI', 'Apuestas', 'Max Drawdown']].to_string(index=False))
    print("==========================================================================================")
    
    # -------------------------------------------------------------------------
    # CONFIGURAR Y DIBUJAR LOS GRÁFICOS COMPARATIVOS
    # -------------------------------------------------------------------------
    dates = [df['date'].iloc[0] - pd.Timedelta(days=1)] + list(df['date'])
    
    # Definir configuraciones representativas para graficar
    plot_configs = [
        # (Label, min_odd, max_odd, min_prob, min_kelly, color)
        ('Sin Filtros (Línea Base)', 1.0, 100.0, 0.0, 0.0, '#718096'),        # Slate
        ('Filtro Moderado (Odds 1.4-5.0)', 1.4, 5.0, 0.0, 0.0, '#4299E1'),    # Blue
        ('Filtro Conservador + Prob >= 20%', 1.6, 4.0, 0.20, 0.002, '#ED8936'), # Orange
        ('Filtro Estricto + Prob >= 30%', 1.6, 4.0, 0.30, 0.004, '#38A169')     # Green
    ]
    
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'DejaVu Sans']
    
    # 1. Gráfico Flat Staking
    fig, ax = plt.subplots(figsize=(12, 6.5))
    for label, min_odd, max_odd, min_prob, min_k, color in plot_configs:
        res = run_simulation_with_filters(
            df, staking_strategy='flat', cal_mode='iso',
            min_odd=min_odd, max_odd=max_odd, min_prob=min_prob, min_kelly=0.0
        )
        ax.plot(dates, res['history'], label=f"{label} (ROI: {res['roi']:.2f}%)", color=color, linewidth=2.0)
        
    ax.axhline(y=1000.0, color='black', linestyle=':', alpha=0.6)
    ax.set_title('Impacto de Filtros de Riesgo en Portafolio Combinado (Staking: Flat 1%)\n(Validación Cruzada Temporal - Cuotas Reales y Sintéticas Corregidas)', fontsize=13, fontweight='bold', pad=12)
    ax.set_xlabel('Línea Temporal de Partidos', fontsize=10)
    ax.set_ylabel('Banca (USD)', fontsize=10)
    ax.grid(True, linestyle='--', alpha=0.5, color='#CBD5E0')
    ax.legend(frameon=True, facecolor='white', edgecolor='#E2E8F0', loc='upper left', fontsize=9.5)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    def dollar_format(x, pos):
        return f"${x:.0f}"
    ax.yaxis.set_major_formatter(FuncFormatter(dollar_format))
    
    plt.tight_layout()
    fig_flat_path = os.path.abspath(os.path.join(current_dir, "..", "Carpeta_Presentacion", "41_Simulacion_Filtros_Flat.png"))
    plt.savefig(fig_flat_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[OK] Gráfico Flat Staking guardado en: {fig_flat_path}")
    
    # 2. Gráfico Quarter Kelly Staking
    fig, ax = plt.subplots(figsize=(12, 6.5))
    for label, min_odd, max_odd, min_prob, min_k, color in plot_configs:
        res = run_simulation_with_filters(
            df, staking_strategy='quarter', cal_mode='iso',
            min_odd=min_odd, max_odd=max_odd, min_prob=min_prob, min_kelly=min_k
        )
        ax.plot(dates, res['history'], label=f"{label} (ROI: {res['roi']:.2f}%)", color=color, linewidth=2.0)
        
    ax.axhline(y=1000.0, color='black', linestyle=':', alpha=0.6)
    ax.set_title('Impacto de Filtros de Riesgo en Portafolio Combinado (Staking: Quarter Kelly)\n(Validación Cruzada Temporal - Cuotas Reales y Sintéticas Corregidas)', fontsize=13, fontweight='bold', pad=12)
    ax.set_xlabel('Línea Temporal de Partidos', fontsize=10)
    ax.set_ylabel('Banca (USD)', fontsize=10)
    ax.grid(True, linestyle='--', alpha=0.5, color='#CBD5E0')
    ax.legend(frameon=True, facecolor='white', edgecolor='#E2E8F0', loc='upper left', fontsize=9.5)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.yaxis.set_major_formatter(FuncFormatter(dollar_format))
    
    plt.tight_layout()
    fig_kelly_path = os.path.abspath(os.path.join(current_dir, "..", "Carpeta_Presentacion", "42_Simulacion_Filtros_Kelly.png"))
    plt.savefig(fig_kelly_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[OK] Gráfico Quarter Kelly guardado en: {fig_kelly_path}")

if __name__ == '__main__':
    main()
