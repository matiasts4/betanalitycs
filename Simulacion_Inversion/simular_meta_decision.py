import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from sklearn.ensemble import RandomForestClassifier

def get_meta_features(row, bet_type):
    h_elo = row['home_elo']
    a_elo = row['away_elo']
    h_rest = row['home_rest']
    a_rest = row['away_rest']
    
    if bet_type == 'home':
        elo_diff = h_elo - a_elo
        rest_diff = h_rest - a_rest
    elif bet_type == 'away':
        elo_diff = a_elo - h_elo
        rest_diff = a_rest - h_rest
    elif bet_type == 'draw':
        elo_diff = -abs(h_elo - a_elo)  # A mayor disparidad, menor probabilidad de empate
        rest_diff = abs(h_rest - a_rest)
    elif bet_type == 'dc_1X':
        elo_diff = h_elo - a_elo
        rest_diff = h_rest - a_rest
    elif bet_type == 'dc_X2':
        elo_diff = a_elo - h_elo
        rest_diff = a_rest - h_rest
    elif bet_type in ['over', 'under']:
        elo_diff = abs(h_elo - a_elo)  # Disparidad de nivel
        rest_diff = h_rest + a_rest     # Fatiga total de ambos equipos
    else:
        elo_diff = 0.0
        rest_diff = 0.0
        
    return elo_diff, rest_diff

def run_simulation(df, mode='baseline', edge_threshold=0.05, initial_bankroll=1000.0, num_splits=5):
    # Validacion walk-forward: el meta-modelo solo entrena con apuestas de splits
    # anteriores y se evalua en el split actual. Esto evita leakage temporal.
    n_records = len(df)
    split_size = n_records // num_splits
    
    bankroll = initial_bankroll
    history = [bankroll]
    
    bets_count = 0
    wins_count = 0
    wagered = 0.0
    profit = 0.0
    bets_avoided = 0
    
    # Lista para recolectar el historial de apuestas de cara al entrenamiento del Meta-Modelo
    historical_bets = []
    
    # Simular split por split (Walk-Forward)
    for s_idx in range(num_splits):
        start_idx = s_idx * split_size
        end_idx = (s_idx + 1) * split_size if s_idx < num_splits - 1 else n_records
        
        df_split = df.iloc[start_idx:end_idx]
        
        # 1. Entrenar el Meta-Modelo si estamos en split > 0 y la estrategia requiere Meta-Model
        meta_clf = None
        if s_idx > 0 and mode in ['meta_model', 'dual']:
            # Crear dataset de entrenamiento a partir del historial PREVIO unicamente
            train_records = []
            for b in historical_bets:
                train_records.append({
                    'prob': b['prob'],
                    'odd': b['odd'],
                    'ev': b['ev'],
                    'elo_diff': b['elo_diff'],
                    'rest_diff': b['rest_diff'],
                    'win': int(b['win'])
                })
            
            if len(train_records) >= 30: # Entrenar solo si hay suficientes datos
                train_df = pd.DataFrame(train_records)
                X_meta = train_df[['prob', 'odd', 'ev', 'elo_diff', 'rest_diff']]
                y_meta = train_df['win']
                
                # Clasificador estable para muestras pequenas
                meta_clf = RandomForestClassifier(n_estimators=100, max_depth=3, random_state=42)
                meta_clf.fit(X_meta, y_meta)
        
        # 2. Simular los partidos de este split
        for idx, row in df_split.iterrows():
            # Construir opciones del Portafolio Real (mercados con cuotas reales de Bet365)
            cal_mode = 'iso'
            all_options = {
                'home': {'prob': row[f'p_home_{cal_mode}'], 'odd': row['B365H'], 'win': (row['target_1x2'] == 2)},
                'draw': {'prob': row[f'p_draw_{cal_mode}'], 'odd': row['B365D'], 'win': (row['target_1x2'] == 1)},
                'away': {'prob': row[f'p_away_{cal_mode}'], 'odd': row['B365A'], 'win': (row['target_1x2'] == 0)},
                'dc_1X': {'prob': row[f'p_dc1X_{cal_mode}'], 'odd': row['B365_1X'], 'win': (row['target_dc_1X'] == 1)},
                'dc_X2': {'prob': row[f'p_dcX2_{cal_mode}'], 'odd': row['B365_X2'], 'win': (row['target_dc_X2'] == 1)},
                'over': {'prob': row[f'p_over_{cal_mode}'], 'odd': row['B365>2.5'], 'win': (row['target_over_2_5_goals'] == 1)},
                'under': {'prob': row[f'p_under_{cal_mode}'], 'odd': row['B365<2.5'], 'win': (row['target_under_2_5_goals'] == 1)}
            }
            
            # Calcular EVs para todas las opciones
            evs = {}
            for name, opt in all_options.items():
                evs[name] = {
                    'ev': opt['prob'] * opt['odd'] - 1,
                    'odd': opt['odd'],
                    'prob': opt['prob'],
                    'win': opt['win']
                }
                
            best_bet_name = max(evs, key=lambda k: evs[k]['ev'])
            best_bet = evs[best_bet_name]
            
            # Obtener variables dinamicas de ELO y Descanso
            elo_diff, rest_diff = get_meta_features(row, best_bet_name)
            
            # Determinar el edge requerido
            if mode in ['dynamic_ev', 'dual']:
                edge_req = edge_threshold * max(1.0, np.sqrt(best_bet['odd'] - 1))
            else:
                edge_req = edge_threshold
                
            # Cumple con el EV requerido?
            passes_ev = best_bet['ev'] >= edge_req
            
            placed_bet = False
            if passes_ev and bankroll > 0:
                # Si pasa la primera capa, consultamos la segunda capa (Meta-Model)
                autorized = True
                
                if meta_clf is not None:
                    # Evaluar prediccion con los mismos nombres de columnas usados en entrenamiento
                    feats = pd.DataFrame([[best_bet['prob'], best_bet['odd'], best_bet['ev'], elo_diff, rest_diff]],
                                         columns=['prob', 'odd', 'ev', 'elo_diff', 'rest_diff'])
                    p_win = meta_clf.predict_proba(feats)[0, 1]
                    
                    if p_win < 0.50:
                        autorized = False
                        bets_avoided += 1
                        
                if autorized:
                    stake = 10.0  # Flat Staking 1%
                    if bankroll >= stake:
                        bets_count += 1
                        wagered += stake
                        if best_bet['win']:
                            net_profit = stake * (best_bet['odd'] - 1)
                            wins_count += 1
                            bet_won = True
                        else:
                            net_profit = -stake
                            bet_won = False
                        bankroll += net_profit
                        profit += net_profit
                        placed_bet = True
                        
            # Registrar la apuesta en el historial si cumplio el EV inicial (para entrenar al Meta-Modelo de cara a futuro)
            # Nota: guardamos el resultado real (win) para entrenar con datos reales
            if passes_ev:
                historical_bets.append({
                    'prob': best_bet['prob'],
                    'odd': best_bet['odd'],
                    'ev': best_bet['ev'],
                    'elo_diff': elo_diff,
                    'rest_diff': rest_diff,
                    'win': best_bet['win']
                })
                
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
        'history': history,
        'avoided': bets_avoided
    }

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    csv_preds = os.path.join(current_dir, "predicciones_prueba_calibradas.csv")
    csv_master = os.path.join(current_dir, "historical_with_ou_odds.csv")
    
    df_preds = pd.read_csv(csv_preds)
    df_master = pd.read_csv(csv_master)
    
    # Cruzar datos por game_id para obtener caracteristicas
    df = pd.merge(df_preds, df_master[['game_id', 'home_elo', 'away_elo', 'home_rest', 'away_rest']], on='game_id', how='left')
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date').reset_index(drop=True)
    
    # Correr las 4 estrategias
    print("Corriendo Simulaciones Comparativas...")
    
    res_base = run_simulation(df, mode='baseline', edge_threshold=0.05)
    print(f"Linea Base Reales: Banca = ${res_base['final_bankroll']:.2f} | ROI = {res_base['roi']:.2f}% | Bets = {res_base['bets']} | Drawdown = {res_base['max_dd']:.2f}%")
    
    res_dyn = run_simulation(df, mode='dynamic_ev', edge_threshold=0.05)
    print(f"Solo EV Dinamico: Banca = ${res_dyn['final_bankroll']:.2f} | ROI = {res_dyn['roi']:.2f}% | Bets = {res_dyn['bets']} | Drawdown = {res_dyn['max_dd']:.2f}%")
    
    res_meta = run_simulation(df, mode='meta_model', edge_threshold=0.05)
    print(f"Solo Meta-Modelo: Banca = ${res_meta['final_bankroll']:.2f} | ROI = {res_meta['roi']:.2f}% | Bets = {res_meta['bets']} | Evitadas = {res_meta['avoided']} | Drawdown = {res_meta['max_dd']:.2f}%")
    
    res_dual = run_simulation(df, mode='dual', edge_threshold=0.05)
    print(f"Sistema Dual (Optimo): Banca = ${res_dual['final_bankroll']:.2f} | ROI = {res_dual['roi']:.2f}% | Bets = {res_dual['bets']} | Evitadas = {res_dual['avoided']} | Drawdown = {res_dual['max_dd']:.2f}%")
    
    # -------------------------------------------------------------------------
    # DIBUJAR LAS CURVAS DE CAPITAL
    # -------------------------------------------------------------------------
    dates = [df['date'].iloc[0] - pd.Timedelta(days=1)] + list(df['date'])
    
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'DejaVu Sans']
    
    fig, ax = plt.subplots(figsize=(13, 7.5))
    
    ax.plot(dates, res_base['history'], label=f"Linea Base Real (ROI: {res_base['roi']:.2f}%, Bets: {res_base['bets']})", color='#718096', linestyle=':', linewidth=1.8)
    ax.plot(dates, res_dyn['history'], label=f"Solo EV Dinamico (ROI: {res_dyn['roi']:.2f}%, Bets: {res_dyn['bets']})", color='#4299E1', linestyle='--', linewidth=1.8)
    ax.plot(dates, res_meta['history'], label=f"Solo Meta-Modelo Capa 2 (ROI: {res_meta['roi']:.2f}%, Bets: {res_meta['bets']})", color='#ED8936', linestyle='-.', linewidth=1.8)
    ax.plot(dates, res_dual['history'], label=f"Sistema Dual (EV Dinamico + Meta-Model) (ROI: {res_dual['roi']:.2f}%, Bets: {res_dual['bets']})", color='#38A169', linestyle='-', linewidth=2.5)
    
    ax.axhline(y=1000.0, color='#2D3748', linestyle=':', alpha=0.5)
    ax.set_title('Impacto de Decisiones de Segunda Capa (Meta-Labeling y EV Dinamico)\n(Portafolio de Mercados Reales | Staking: Flat 1% | Simulacion Walk-Forward Sin Leakage)', fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel('Linea Temporal de Partidos', fontsize=11)
    ax.set_ylabel('Banca (USD)', fontsize=11)
    ax.grid(True, linestyle='--', alpha=0.4, color='#CBD5E0')
    ax.legend(frameon=True, facecolor='white', edgecolor='#E2E8F0', loc='upper left', fontsize=10)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#718096')
    ax.spines['bottom'].set_color('#718096')
    
    def dollar_format(x, pos):
        return f"${x:.0f}"
    ax.yaxis.set_major_formatter(FuncFormatter(dollar_format))
    
    plt.tight_layout()
    fig_path = os.path.abspath(os.path.join(current_dir, "..", "Carpeta_Presentacion", "46_Simulacion_Meta_Labeling.png"))
    plt.savefig(fig_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[OK] Grafico de Meta-Labeling guardado en: {fig_path}")

    # Guardar reporte de resultados
    records = [
        {'Configuracion': 'Linea Base Real', 'Banca Final': f"${res_base['final_bankroll']:.2f}", 'ROI': f"{res_base['roi']:.2f}%", 'Bets': res_base['bets'], 'Evitadas': 0, 'Max Drawdown': f"{res_base['max_dd']:.2f}%"},
        {'Configuracion': 'Solo EV Dinamico', 'Banca Final': f"${res_dyn['final_bankroll']:.2f}", 'ROI': f"{res_dyn['roi']:.2f}%", 'Bets': res_dyn['bets'], 'Evitadas': 0, 'Max Drawdown': f"{res_dyn['max_dd']:.2f}%"},
        {'Configuracion': 'Solo Meta-Modelo', 'Banca Final': f"${res_meta['final_bankroll']:.2f}", 'ROI': f"{res_meta['roi']:.2f}%", 'Bets': res_meta['bets'], 'Evitadas': res_meta['avoided'], 'Max Drawdown': f"{res_meta['max_dd']:.2f}%"},
        {'Configuracion': 'Sistema Dual (Optimo)', 'Banca Final': f"${res_dual['final_bankroll']:.2f}", 'ROI': f"{res_dual['roi']:.2f}%", 'Bets': res_dual['bets'], 'Evitadas': res_dual['avoided'], 'Max Drawdown': f"{res_dual['max_dd']:.2f}%"}
    ]
    pd.DataFrame(records).to_csv(os.path.join(current_dir, "reporte_meta_decision.csv"), index=False)
    print("[OK] Hojas de reporte guardadas exitosamente.")

if __name__ == '__main__':
    main()
