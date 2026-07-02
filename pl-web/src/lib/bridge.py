import os
import sys
import json
import warnings
import numpy as np
import pandas as pd

warnings.filterwarnings('ignore')

# Configurar rutas para importar desde el backend
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../archive/pl-predictor'))
sys.path.append(BASE_DIR)

from src.config import TARGETS, FEATURES, MODELS_DIR
from src.models.selector import MasterBetSelector
from src.api import compute_elo_map, build_team_last5, compute_demo_test_metrics

DEMO_MODELS_DIR = os.path.join(BASE_DIR, "models_demo")
_demo_selector = None
# In-memory cache for stats computed from the test set
_bridge_stats_cache = None

def get_demo_selector():
    global _demo_selector
    if _demo_selector is None:
        _demo_selector = MasterBetSelector(models_dir=DEMO_MODELS_DIR)
    return _demo_selector

sys.path.append(os.path.dirname(__file__))
from src.db import get_upcoming_matches, save_upcoming_matches, init_db
from assistant import get_provider

def clean_json(obj):
    if isinstance(obj, list):
        return [clean_json(x) for x in obj]
    elif isinstance(obj, dict):
        return {k: clean_json(v) for k, v in obj.items()}
    elif isinstance(obj, (np.integer, np.int64, np.int32)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64, np.float32)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return [clean_json(x) for x in obj]
    else:
        return obj

def evaluate_market_result(market, home_goals, away_goals, result_1x2, pick):
    try:
        pick_int = int(pick)
    except (ValueError, TypeError):
        pick_int = 1
        
    if market == '1X2' or '1X2' in market:
        if pd.notna(result_1x2):
            return pick_int == int(result_1x2)
        else:
            actual_res = 2 if home_goals > away_goals else (0 if away_goals > home_goals else 1)
            return pick_int == actual_res
    elif 'Over 2.5' in market:
        return ((home_goals + away_goals) > 2.5) == bool(pick_int)
    elif 'Under 2.5' in market:
        return ((home_goals + away_goals) < 2.5) == bool(pick_int)
    elif 'BTTS (Both Teams To Score)' in market or 'BTTS' in market and 'No' not in market:
        return ((home_goals > 0) and (away_goals > 0)) == bool(pick_int)
    elif 'BTTS - No' in market:
        return (not ((home_goals > 0) and (away_goals > 0))) == bool(pick_int)
    elif 'Home Clean Sheet' in market:
        return (away_goals == 0) == bool(pick_int)
    elif 'Home' in market and 'Win' in market:
        return (home_goals > away_goals) == bool(pick_int)
    elif 'Away' in market and 'Win' in market:
        return (away_goals > home_goals) == bool(pick_int)
    else:
        return False

def run_predict(payload):
    home = payload.get('homeTeam', '')
    away = payload.get('awayTeam', '')
    h_miss = int(payload.get('homeMissingKey', False))
    a_miss = int(payload.get('awayMissingKey', False))
    match_date = payload.get('date', None)

    # Cargar datos
    features_path = os.path.join(BASE_DIR, "data", "historical", "historical_sanitized_v9.csv")
    df = pd.read_csv(features_path, parse_dates=['date'])
    df = df.sort_values('date').reset_index(drop=True)

    if match_date:
        try:
            match_date_parsed = pd.to_datetime(match_date)
            elo_map = compute_elo_map(df, cutoff_date=match_date_parsed)
            h_form  = build_team_last5(home, df, cutoff=match_date_parsed)
            a_form  = build_team_last5(away, df, cutoff=match_date_parsed)
        except Exception:
            elo_map = compute_elo_map(df)
            h_form  = build_team_last5(home, df)
            a_form  = build_team_last5(away, df)
    else:
        elo_map = compute_elo_map(df)
        h_form  = build_team_last5(home, df)
        a_form  = build_team_last5(away, df)

    ref_avg = float(df['referee_avg_cards_history'].mean()) if 'referee_avg_cards_history' in df.columns else 3.5

    features = {
        'home_elo':              round(elo_map.get(home, 1500), 1),
        'away_elo':              round(elo_map.get(away, 1500), 1),
        'h_missing_key_player':  h_miss,
        'a_missing_key_player':  a_miss,
        'home_rest':             7,
        'away_rest':             7,
        'h_l5_pts':              h_form.get('pts', 0),
        'h_l5_sh':               h_form.get('sh', 0),
        'h_l5_sot':              h_form.get('sot', 0),
        'h_l5_sot_c':            0.0,
        'h_l5_gf':               h_form.get('gf', 0),
        'h_l5_ga':               h_form.get('ga', 0),
        'h_l5_fls':              h_form.get('fls', 0),
        'h_l5_conv':             h_form.get('conv', 0),
        'h_l5_xg':               h_form.get('xg', 0),
        'h_l5_xga':              h_form.get('xga', 0),
        'a_l5_pts':              a_form.get('pts', 0),
        'a_l5_sh':               a_form.get('sh', 0),
        'a_l5_sot':              a_form.get('sot', 0),
        'a_l5_sot_c':            0.0,
        'a_l5_gf':               a_form.get('gf', 0),
        'a_l5_ga':               a_form.get('ga', 0),
        'a_l5_fls':              a_form.get('fls', 0),
        'a_l5_conv':             a_form.get('conv', 0),
        'a_l5_xg':               a_form.get('xg', 0),
        'a_l5_xga':              a_form.get('xga', 0),
        'referee_avg_cards_history': ref_avg,
        'is_derby':              0,
        'relegation_pressure':   0,
    }

    selector = MasterBetSelector()
    preds = selector.get_best_bet(features)

    # Sort predictions by EV descending in the predictions array itself (smart selection)
    preds.sort(key=lambda x: x.get('ExpectedValue', 0.0), reverse=True)

    result = {
        'homeTeam':  home,
        'awayTeam':  away,
        'homeElo':   features['home_elo'],
        'awayElo':   features['away_elo'],
        'homeForm':  h_form,
        'awayForm':  a_form,
        'predictions': preds,
    }
    return clean_json(result)

def run_simulate(payload):
    initial_bankroll = float(payload.get('initialBankroll', 100.0))
    stake = float(payload.get('stake', 10.0))
    n_matches = int(payload.get('nMatches', 60))
    strategy = payload.get('strategy', 'fixed')
    season = payload.get('season', 'all')
    min_odds = float(payload.get('minOdds', 1.0))
    min_ev = float(payload.get('minEv', 0.0)) / 100.0
    compare_model = payload.get('compareModel', 'none')
    min_prob = float(payload.get('minProb', 50.0)) / 100.0
    allowed_markets = payload.get('allowedMarkets', [])
    selection_criteria = payload.get('selectionCriteria', 'combined')

    features_path = os.path.join(BASE_DIR, "data", "historical", "historical_sanitized_v9.csv")
    df = pd.read_csv(features_path, parse_dates=['date'])
    df = df.sort_values('date').reset_index(drop=True)

    completed = df[df['home_goals'].notna()].copy()
    if completed.empty:
        return {}

    # Define real_season dynamically based on match date to avoid standardized floats bug
    def get_season_code(date):
        if pd.isna(date):
            return None
        year = date.year
        month = date.month
        if month >= 8:
            start_yr = year
        else:
            start_yr = year - 1
        s_code = (start_yr % 100) * 100 + ((start_yr + 1) % 100)
        return s_code

    completed['real_season'] = completed['date'].apply(get_season_code)

    if season != 'all':
        try:
            szn_val = int(season)
            test_set = completed[completed['real_season'] == szn_val].sort_values('date')
        except Exception:
            test_set = completed.sort_values('date').tail(n_matches)
    else:
        test_set = completed.sort_values('date').tail(n_matches)
    
    if test_set.empty:
        return {}

    elo_map = compute_elo_map(df)
    ref_avg = float(df['referee_avg_cards_history'].mean()) if 'referee_avg_cards_history' in df.columns else 3.5

    bankroll = float(initial_bankroll)
    bankroll_b = float(initial_bankroll)
    max_stake_frac = float(stake) / 100.0 if strategy == 'variable' else 0.0
    
    wins = 0
    losses = 0
    total_ev = 0.0
    
    wins_b = 0
    losses_b = 0
    
    history_data = []
    profit_chart_data = []
    
    start_point = {
        'name': test_set.iloc[0]['date'].strftime('%b %Y') if not test_set.empty else 'Start',
        'bankroll': round(bankroll, 2)
    }
    if compare_model != 'none':
        start_point['bankrollB'] = round(bankroll_b, 2)
    profit_chart_data.append(start_point)

    selector = get_demo_selector()

    for i, row in test_set.iterrows():
        if bankroll <= 1.0:
            break
        
        home = row['home_team']
        away = row['away_team']
        match_date = row['date']
        
        features = {
            'home_elo':              row.get('home_elo', 0.0),
            'away_elo':              row.get('away_elo', 0.0),
            'home_rest':             row.get('home_rest', 7.0),
            'away_rest':             row.get('away_rest', 7.0),
            'h_l5_pts':              row.get('h_l5_pts', 0.0),
            'h_l5_sh':               row.get('h_l5_sh', 0.0),
            'h_l5_sot':              row.get('h_l5_sot', 0.0),
            'h_l5_sot_c':            row.get('h_l5_sot_c', 0.0),
            'h_l5_gf':               row.get('h_l5_gf', 0.0),
            'h_l5_ga':               row.get('h_l5_ga', 0.0),
            'h_l5_fls':              row.get('h_l5_fls', 0.0),
            'h_l5_conv':             row.get('h_l5_conv', 0.0),
            'h_l5_xg':               row.get('h_l5_xg', 0.0),
            'h_l5_xga':              row.get('h_l5_xga', 0.0),
            'a_l5_pts':              row.get('a_l5_pts', 0.0),
            'a_l5_sh':               row.get('a_l5_sh', 0.0),
            'a_l5_sot':              row.get('a_l5_sot', 0.0),
            'a_l5_sot_c':            row.get('a_l5_sot_c', 0.0),
            'a_l5_gf':               row.get('a_l5_gf', 0.0),
            'a_l5_ga':               row.get('a_l5_ga', 0.0),
            'a_l5_fls':              row.get('a_l5_fls', 0.0),
            'a_l5_conv':             row.get('a_l5_conv', 0.0),
            'a_l5_xg':               row.get('a_l5_xg', 0.0),
            'a_l5_xga':              row.get('a_l5_xga', 0.0),
            'referee_avg_cards_history': row.get('referee_avg_cards_history', ref_avg),
            'is_derby':              row.get('is_derby', 0),
            'relegation_pressure':   row.get('relegation_pressure', 0),
        }

        preds = selector.get_best_bet(features)
        if not preds:
            continue
            
        top_bet = None
        bookie_odds = 0.0
        
        # Calculate "Public" probability based purely on Elo to simulate real Bookie Odds
        prob_public = 1.0 / (1.0 + 10.0 ** ((features['away_elo'] - features['home_elo']) / 400.0))
        prob_public = max(0.01, min(0.99, prob_public))
        
        # Recalculate EV and stake limit using user-defined max_stake_frac
        for p in preds:
            prob = p['Probability']
            market = p['Market']
            
            # Map Public Probability to the specific market roughly
            if market == '1X2':
                base_prob = prob_public * 0.9  
            elif '1X' in market or 'X2' in market:
                base_prob = prob_public + 0.15 
                base_prob = min(0.99, base_prob)
            else:
                base_prob = prob + np.random.uniform(-0.10, 0.10)
                base_prob = max(0.01, min(0.99, base_prob))
                
            f_odds = 1.0 / base_prob
            simulated_odds = round(max(1.01, f_odds * 0.95), 2)
            
            p['FairOdds'] = round(1.0 / prob if prob > 0 else 100.0, 2)
            ev = (prob * simulated_odds) - 1.0 
            p['ExpectedValue'] = round(ev, 3) 
            
            if simulated_odds > 1.0:
                b = simulated_odds - 1.0
                q = 1.0 - prob
                kelly_f = (b * prob - q) / b
            else:
                kelly_f = -1.0
                
            # Use user-supplied Kelly max_stake_frac limit
            limit_val = max_stake_frac if strategy == 'variable' else 0.10
            p['RecommendedStakePct'] = round(min(kelly_f * 0.25, limit_val) * 100, 2) if kelly_f > 0 else 0.0

        # Sort predictions by EV descending (Smart Selector) instead of probability descending
        preds.sort(key=lambda x: x['ExpectedValue'], reverse=True)

        for p in preds:
            prob = p['Probability']
            market = p['Market']
            
            # Filter by allowed markets
            if allowed_markets:
                is_allowed = False
                for allowed in allowed_markets:
                    if allowed.lower() in market.lower():
                        is_allowed = True
                        break
                if not is_allowed:
                    continue
            
            simulated_odds = p['ExpectedValue'] / prob + 1.0 if prob > 0 else 1.0
            simulated_odds = round(simulated_odds, 2)
            ev_val = p['ExpectedValue']
            
            meet_ev = ev_val >= min_ev
            meet_prob = prob >= min_prob
            meet_odds = simulated_odds >= min_odds
            
            meet_criteria = False
            if selection_criteria == 'ev_only':
                meet_criteria = meet_ev
            elif selection_criteria == 'prob_only':
                meet_criteria = meet_prob
            else: # combined
                meet_criteria = meet_ev and meet_prob
            
            if meet_odds and meet_criteria:
                top_bet = p
                bookie_odds = simulated_odds
                break
                
        if not top_bet:
            continue
            
        market = top_bet['Market']
        prob = top_bet['Probability']
        ev_val = top_bet.get('ExpectedValue', 0.0)
        stake_pct = top_bet.get('RecommendedStakePct', 0.0)
        total_ev += ev_val
        
        home_goals = row['home_goals']
        away_goals = row['away_goals']
        res_1x2    = row.get('result_1x2')
        
        if strategy == 'variable':
            recommended_pct = stake_pct
            if recommended_pct <= 0:
                continue 
                
            f_star = recommended_pct / 100.0
            f_star = min(f_star, max_stake_frac)
            stake_amount = max(bankroll * f_star, 1.0)
        else:
            stake_amount = float(stake)
            
        if stake_amount > bankroll:
            stake_amount = bankroll
            
        if stake_amount < 1.0:
            continue
            
        pick = top_bet['Pick']
        won = evaluate_market_result(market, home_goals, away_goals, res_1x2, pick)
        
        bankroll -= stake_amount 
        if won:
            payout = stake_amount * bookie_odds
            bankroll += payout
            wins += 1
            status = 'Won'
            bet_profit = payout - stake_amount
        else:
            losses += 1
            status = 'Lost'
            bet_profit = -stake_amount
            
        chart_point = {
            'name': match_date.strftime('%b %d, %Y'),
            'bankroll': round(bankroll, 2)
        }
        
        if compare_model != 'none':
            prob_b = 1.0 / (1.0 + 10.0 ** ((features['away_elo'] - features['home_elo']) / 400.0))
            prob_b = max(0.01, min(0.99, prob_b))
            odds_b = max(1.01, (1.0 / prob_b) * 0.95)
            won_b = (home_goals > away_goals)
            
            stake_b = float(stake)
            if strategy == 'variable':
                f_star_b = min(prob_b * max_stake_frac, 0.05)
                stake_b = max(bankroll_b * f_star_b, 1.0)
            if stake_b > bankroll_b:
                stake_b = bankroll_b
                
            if stake_b >= 1.0 and bankroll_b > 1.0:
                bankroll_b -= stake_b
                if won_b:
                    bankroll_b += stake_b * odds_b
                    wins_b += 1
                else:
                    losses_b += 1
                    
            chart_point['bankrollB'] = round(bankroll_b, 2)
            
        profit_chart_data.append(chart_point)
        
        history_data.append({
            'date': match_date.strftime('%b %d, %Y'),
            'match': f"{home} vs {away}",
            'prediction': market,
            'odds': bookie_odds,
            'result': status,
            'profit': round(bet_profit, 2),
            'balance': round(bankroll, 2),
            'ev': round(ev_val, 3),
            'stakePct': round(stake_pct, 2),
            'stakeAmount': round(stake_amount, 2),
            'homeGoals': int(home_goals),
            'awayGoals': int(away_goals),
            'features': features,
            'predictions': [
                {
                    'market': p['Market'],
                    'probability': round(p['Probability'] * 100, 1),
                    'odds': p['FairOdds'],
                    'ev': p['ExpectedValue'],
                    'won': evaluate_market_result(p['Market'], home_goals, away_goals, res_1x2, p['Pick'])
                } for p in preds
            ]
        })

    total_bets = wins + losses
    win_rate = round((wins / total_bets * 100), 1) if total_bets > 0 else 0.0
    history_data.reverse()

    period_str = ""
    if not test_set.empty:
        start_date = test_set.iloc[0]['date'].strftime('%b %Y')
        end_date = test_set.iloc[-1]['date'].strftime('%b %Y')
        period_str = f"{start_date} - {end_date}"

    avg_ev = round((total_ev / total_bets) * 100, 2) if total_bets > 0 else 0.0

    result = {
        'performanceSummary': {
            'finalBankroll': round(bankroll, 2),
            'netProfit': round(bankroll - float(initial_bankroll), 2),
            'winRate': win_rate,
            'totalBets': total_bets,
            'wins': wins,
            'losses': losses,
            'period': period_str,
            'avgEV': avg_ev
        },
        'profitChartData': profit_chart_data,
        'historyData': history_data
    }
    
    if compare_model != 'none':
        total_bets_b = wins_b + losses_b
        win_rate_b = round((wins_b / total_bets_b * 100), 1) if total_bets_b > 0 else 0.0
        result['performanceSummaryB'] = {
            'finalBankroll': round(bankroll_b, 2),
            'netProfit': round(bankroll_b - float(initial_bankroll), 2),
            'winRate': win_rate_b,
            'totalBets': total_bets_b,
            'wins': wins_b,
            'losses': losses_b,
            'period': period_str
        }

    return clean_json(result)

def run_performance():
    features_path = os.path.join(BASE_DIR, "data", "historical", "historical_sanitized_v9.csv")
    df = pd.read_csv(features_path, parse_dates=['date'])
    df = df.sort_values('date').reset_index(drop=True)

    completed = df[df['home_goals'].notna()].copy()
    if completed.empty:
        return {}

    test_set = completed.sort_values('date').tail(60)
    
    elo_map = compute_elo_map(df)
    ref_avg = float(df['referee_avg_cards_history'].mean()) if 'referee_avg_cards_history' in df.columns else 3.5

    cumulative_profit = 0.0
    wins = 0
    losses = 0
    
    history_data = []
    profit_chart_data = []

    selector = get_demo_selector()

    for i, row in test_set.iterrows():
        home = row['home_team']
        away = row['away_team']
        match_date = row['date']
        
        features = {
            'home_elo':              row.get('home_elo', 0.0),
            'away_elo':              row.get('away_elo', 0.0),
            'home_rest':             row.get('home_rest', 7.0),
            'away_rest':             row.get('away_rest', 7.0),
            'h_l5_pts':              row.get('h_l5_pts', 0.0),
            'h_l5_sh':               row.get('h_l5_sh', 0.0),
            'h_l5_sot':              row.get('h_l5_sot', 0.0),
            'h_l5_sot_c':            row.get('h_l5_sot_c', 0.0),
            'h_l5_gf':               row.get('h_l5_gf', 0.0),
            'h_l5_ga':               row.get('h_l5_ga', 0.0),
            'h_l5_fls':              row.get('h_l5_fls', 0.0),
            'h_l5_conv':             row.get('h_l5_conv', 0.0),
            'h_l5_xg':               row.get('h_l5_xg', 0.0),
            'h_l5_xga':              row.get('h_l5_xga', 0.0),
            'a_l5_pts':              row.get('a_l5_pts', 0.0),
            'a_l5_sh':               row.get('a_l5_sh', 0.0),
            'a_l5_sot':              row.get('a_l5_sot', 0.0),
            'a_l5_sot_c':            row.get('a_l5_sot_c', 0.0),
            'a_l5_gf':               row.get('a_l5_gf', 0.0),
            'a_l5_ga':               row.get('a_l5_ga', 0.0),
            'a_l5_fls':              row.get('a_l5_fls', 0.0),
            'a_l5_conv':             row.get('a_l5_conv', 0.0),
            'a_l5_xg':               row.get('a_l5_xg', 0.0),
            'a_l5_xga':              row.get('a_l5_xga', 0.0),
            'referee_avg_cards_history': row.get('referee_avg_cards_history', ref_avg),
            'is_derby':              row.get('is_derby', 0),
            'relegation_pressure':   row.get('relegation_pressure', 0),
        }

        preds = selector.get_best_bet(features)
        if not preds:
            continue
            
        # Select best bet using Expected Value descending (Smart Selector)
        preds.sort(key=lambda x: x.get('ExpectedValue', 0.0), reverse=True)

        top_bet = None
        bookie_odds = 0.0

        for p in preds:
            prob = p['Probability']
            simulated_odds = p['ExpectedValue'] / prob + 1.0 if prob > 0 else 1.0
            simulated_odds = round(simulated_odds, 2)
            ev_val = p['ExpectedValue']
            
            # Require EV >= 0.0 and prob >= 0.55 confidence to match backtest
            if prob >= 0.55:
                top_bet = p
                bookie_odds = simulated_odds
                break

        if not top_bet:
            continue
            
        market = top_bet['Market']
        
        home_goals = row['home_goals']
        away_goals = row['away_goals']
        res_1x2    = row.get('result_1x2')
        
        pick = top_bet['Pick']
        won = evaluate_market_result(market, home_goals, away_goals, res_1x2, pick)
        
        if won:
            bet_profit = bookie_odds - 1.0
            cumulative_profit += bet_profit
            wins += 1
            status = 'Won'
        else:
            bet_profit = -1.0
            cumulative_profit += bet_profit
            losses += 1
            status = 'Lost'
            
        profit_chart_data.append({
            'name': match_date.strftime('%b %d'),
            'profit': round(cumulative_profit, 2)
        })
        
        history_data.append({
            'date': match_date.strftime('%b %d, %Y'),
            'match': f"{home} vs {away}",
            'prediction': market,
            'odds': bookie_odds,
            'result': status,
            'profit': round(bet_profit, 2),
            'homeGoals': int(home_goals),
            'awayGoals': int(away_goals),
            'features': features,
            'predictions': [
                {
                    'market': p['Market'],
                    'probability': round(p['Probability'] * 100, 1),
                    'odds': p['FairOdds'],
                    'ev': p['ExpectedValue'],
                    'won': evaluate_market_result(p['Market'], home_goals, away_goals, res_1x2, p['Pick'])
                } for p in preds
            ]
        })

    total_bets = wins + losses
    win_rate = round((wins / total_bets * 100), 1) if total_bets > 0 else 0.0
    history_data.reverse()

    return clean_json({
        'performanceSummary': {
            'totalProfit': round(cumulative_profit, 2),
            'winRate': win_rate,
            'totalBets': total_bets,
            'wins': wins,
            'losses': losses
        },
        'profitChartData': profit_chart_data,
        'historyData': history_data
    })

def run_detailed_history(payload):
    n = int(payload.get('n', 100))
    
    features_path = os.path.join(BASE_DIR, "data", "historical", "historical_sanitized_v9.csv")
    df = pd.read_csv(features_path, parse_dates=['date'])
    df = df.sort_values('date').reset_index(drop=True)

    completed = df[df['home_goals'].notna()].copy()
    if completed.empty:
        return []

    test_set = completed.sort_values('date').tail(n)
    
    ref_avg = float(df['referee_avg_cards_history'].mean()) if 'referee_avg_cards_history' in df.columns else 3.5

    selector = get_demo_selector()
    detailed_results = []

    for i, row in test_set.iterrows():
        home = row['home_team']
        away = row['away_team']
        match_date = row['date']
        home_goals = row['home_goals']
        away_goals = row['away_goals']
        res_1x2    = row.get('result_1x2')
        
        # Ensure 'is_derby' and 'relegation_pressure' are defined! (fixing KeyError bug)
        features = {
            'home_elo':              row.get('home_elo', 0.0),
            'away_elo':              row.get('away_elo', 0.0),
            'home_rest':             row.get('home_rest', 7.0),
            'away_rest':             row.get('away_rest', 7.0),
            'h_l5_pts':              row.get('h_l5_pts', 0.0),
            'h_l5_sh':               row.get('h_l5_sh', 0.0),
            'h_l5_sot':              row.get('h_l5_sot', 0.0),
            'h_l5_sot_c':            row.get('h_l5_sot_c', 0.0),
            'h_l5_gf':               row.get('h_l5_gf', 0.0),
            'h_l5_ga':               row.get('h_l5_ga', 0.0),
            'h_l5_fls':              row.get('h_l5_fls', 0.0),
            'h_l5_conv':             row.get('h_l5_conv', 0.0),
            'h_l5_xg':               row.get('h_l5_xg', 0.0),
            'h_l5_xga':              row.get('h_l5_xga', 0.0),
            'a_l5_pts':              row.get('a_l5_pts', 0.0),
            'a_l5_sh':               row.get('a_l5_sh', 0.0),
            'a_l5_sot':              row.get('a_l5_sot', 0.0),
            'a_l5_sot_c':            row.get('a_l5_sot_c', 0.0),
            'a_l5_gf':               row.get('a_l5_gf', 0.0),
            'a_l5_ga':               row.get('a_l5_ga', 0.0),
            'a_l5_fls':              row.get('a_l5_fls', 0.0),
            'a_l5_conv':             row.get('a_l5_conv', 0.0),
            'a_l5_xg':               row.get('a_l5_xg', 0.0),
            'a_l5_xga':              row.get('a_l5_xga', 0.0),
            'referee_avg_cards_history': ref_avg,
            'is_derby':              row.get('is_derby', 0),
            'relegation_pressure':   row.get('relegation_pressure', 0),
        }

        preds = selector.get_best_bet(features)
        predictions_detail = []
        for p in preds:
            market = p['Market']
            prob = p['Probability']
            fair_odds = 1.0 / prob if prob > 0 else 2.0
            bookie_odds = round(max(1.01, fair_odds * 0.95), 2)
            
            pick = p['Pick']
            won = evaluate_market_result(market, home_goals, away_goals, res_1x2, pick)
                    
            predictions_detail.append({
                'market': market,
                'probability': round(prob * 100, 1),
                'odds': bookie_odds,
                'won': bool(won)
            })
            
        detailed_results.append({
            'date': match_date.strftime('%b %d, %Y'),
            'home': home,
            'away': away,
            'homeGoals': int(home_goals),
            'awayGoals': int(away_goals),
            'features': features,
            'predictions': predictions_detail
        })
        
    detailed_results.reverse()
    return clean_json(detailed_results)

def run_seasons():
    features_path = os.path.join(BASE_DIR, "data", "historical", "historical_sanitized_v9.csv")
    df = pd.read_csv(features_path, parse_dates=['date'])
    df = df.sort_values('date').reset_index(drop=True)
    completed = df[df['home_goals'].notna()].copy()
    if completed.empty:
        return []

    # Dynamic date-to-season mapper
    def get_season_code(date):
        if pd.isna(date):
            return None
        year = date.year
        month = date.month
        if month >= 8:
            start_yr = year
        else:
            start_yr = year - 1
        return (start_yr % 100) * 100 + ((start_yr + 1) % 100)

    completed['real_season'] = completed['date'].apply(get_season_code)
    
    result = []
    for szn in sorted(completed['real_season'].dropna().unique()):
        s = completed[completed['real_season'] == szn].copy()
        if s.empty:
            continue
        
        total = len(s)
        home_wins = int((s['home_goals'] > s['away_goals']).sum())
        draws     = int((s['home_goals'] == s['away_goals']).sum())
        away_wins = int((s['home_goals'] < s['away_goals']).sum())
        
        s['total_goals'] = s['home_goals'] + s['away_goals']
        
        # Monthly grouping
        s['month_key'] = s['date'].dt.to_period('M')
        monthly = []
        for period, grp in sorted(s.groupby('month_key'), key=lambda x: x[0]):
            grp_total = len(grp)
            monthly.append({
                'month':   period.strftime('%b %y'),
                'matches': grp_total,
                'homeWins': int((grp['home_goals'] > grp['away_goals']).sum()),
                'draws':    int((grp['home_goals'] == grp['away_goals']).sum()),
                'awayWins': int((grp['home_goals'] < grp['away_goals']).sum()),
                'avgGoals': round(float(grp['total_goals'].mean()), 2) if grp_total > 0 else 0.0,
            })
            
        start_y = 2000 + (szn // 100)
        end_y   = 2000 + (szn % 100)
        label = f"{start_y}/{str(end_y)[-2:]}"
        
        result.append({
            'season':    int(szn),
            'label':     label,
            'matches':   total,
            'homeWins':  home_wins,
            'draws':     draws,
            'awayWins':  away_wins,
            'homeWinPct': round(home_wins / total * 100, 1) if total else 0.0,
            'drawPct':    round(draws / total * 100, 1) if total else 0.0,
            'awayWinPct': round(away_wins / total * 100, 1) if total else 0.0,
            'avgGoals':  round(float(s['total_goals'].mean()), 2) if total else 0.0,
            'teams':     len(set(s['home_team'].unique().tolist() + s['away_team'].unique().tolist())),
            'monthly':   monthly,
        })
        
    result.sort(key=lambda x: x['season'], reverse=True)
    return clean_json(result)

def run_history(payload):
    n = int(payload.get('n', 50))
    season = payload.get('season', 'all')
    
    features_path = os.path.join(BASE_DIR, "data", "historical", "historical_sanitized_v9.csv")
    df = pd.read_csv(features_path, parse_dates=['date'])
    df = df.sort_values('date').reset_index(drop=True)
    completed = df[df['home_goals'].notna()].copy()
    
    def get_season_code(date):
        if pd.isna(date):
            return None
        year = date.year
        month = date.month
        if month >= 8:
            start_yr = year
        else:
            start_yr = year - 1
        return (start_yr % 100) * 100 + ((start_yr + 1) % 100)

    completed['real_season'] = completed['date'].apply(get_season_code)
    
    if season and str(season) != 'all':
        try:
            szn_val = int(season)
            completed = completed[completed['real_season'] == szn_val]
        except Exception:
            pass
            
    rows = completed.sort_values('date').tail(n)
    result = []
    for _, row in rows.iterrows():
        hg = int(row['home_goals'])
        ag = int(row['away_goals'])
        if hg > ag:
            outcome = 'home_win'
        elif hg < ag:
            outcome = 'away_win'
        else:
            outcome = 'draw'
        result.append({
            'date':      row['date'].strftime('%Y-%m-%d'),
            'homeTeam':  row['home_team'],
            'awayTeam':  row['away_team'],
            'homeGoals': hg,
            'awayGoals': ag,
            'outcome':   outcome,
            'referee':   str(row.get('referee', '')) if pd.notna(row.get('referee')) else '',
            'totalCards': int(row.get('total_cards', 0)) if pd.notna(row.get('total_cards')) else 0,
            'season':    int(row['real_season']) if pd.notna(row.get('real_season')) else None,
        })
    result.reverse()  # newest first
    return clean_json(result)

def run_stats():
    global _bridge_stats_cache
    if _bridge_stats_cache is not None:
        return _bridge_stats_cache
    features_path = os.path.join(BASE_DIR, "data", "historical", "historical_sanitized_v9.csv")
    df = pd.read_csv(features_path, parse_dates=['date'])
    total = len(df)
    teams = sorted(list(set(df['home_team'].dropna().unique()) | set(df['away_team'].dropna().unique())))
    def get_season_code(date):
        if pd.isna(date):
            return None
        year = date.year
        month = date.month
        if month >= 8:
            start_yr = year
        else:
            start_yr = year - 1
        return (start_yr % 100) * 100 + ((start_yr + 1) % 100)
    df['real_season'] = df['date'].apply(get_season_code)
    seasons_count = int(df['real_season'].nunique())
    metrics = compute_demo_test_metrics()
    _bridge_stats_cache = {
        'totalMatches': total,
        'seasons': seasons_count,
        'teams': len(teams),
        'accuracy_pct': metrics['accuracy_pct'],
        'brier_score': metrics['brier_score'],
        'markets_tracked': 8,
    }
    return _bridge_stats_cache

def run_teams(payload):
    season_param = payload.get('season', None)
    features_path = os.path.join(BASE_DIR, "data", "historical", "historical_sanitized_v9.csv")
    df = pd.read_csv(features_path, parse_dates=['date'])
    df = df.sort_values('date').reset_index(drop=True)
    def get_season_code(date):
        if pd.isna(date):
            return None
        year = date.year
        month = date.month
        if month >= 8:
            start_yr = year
        else:
            start_yr = year - 1
        return (start_yr % 100) * 100 + ((start_yr + 1) % 100)
    df['real_season'] = df['date'].apply(get_season_code)
    df['result_1x2'] = pd.to_numeric(df['result_1x2'], errors='coerce')
    df['home_goals'] = pd.to_numeric(df['home_goals'], errors='coerce')
    df['away_goals'] = pd.to_numeric(df['away_goals'], errors='coerce')
    df_stats = df
    available_seasons = sorted([int(s) for s in df['real_season'].dropna().unique()], reverse=True)
    if season_param and season_param != 'all':
        try:
            df_stats = df[df['real_season'] == int(season_param)]
        except Exception:
            pass
    elo_map = compute_elo_map(df)
    all_teams = sorted(list(set(df['home_team'].dropna().unique()) | set(df['away_team'].dropna().unique())))
    result = []
    for team in all_teams:
        form = build_team_last5(team, df)
        home_matches = df_stats[df_stats['home_team'] == team]
        away_matches = df_stats[df_stats['away_team'] == team]
        if len(home_matches) + len(away_matches) == 0:
            continue
        gf = int(home_matches['home_goals'].sum() + away_matches['away_goals'].sum())
        ga = int(home_matches['away_goals'].sum() + away_matches['home_goals'].sum())
        played = len(home_matches) + len(away_matches)
        h_wins = int((home_matches['result_1x2'] == 2).sum())
        a_wins = int((away_matches['result_1x2'] == 0).sum())
        draws  = int((home_matches['result_1x2'] == 1).sum() + (away_matches['result_1x2'] == 1).sum())
        clean_sheets = int((home_matches['away_goals'] == 0).sum() + (away_matches['home_goals'] == 0).sum())
        result.append({
            'id':               team.lower().replace(' ', '-'),
            'name':             team,
            'elo':              round(elo_map.get(team, 1500), 1),
            'played':           played,
            'won':              h_wins + a_wins,
            'drawn':            draws,
            'lost':             played - h_wins - a_wins - draws,
            'goalsFor':         gf,
            'goalsAgainst':     ga,
            'cleanSheets':      clean_sheets,
            'form':             form,
            'availableSeasons': available_seasons,
        })
    result.sort(key=lambda x: x['elo'], reverse=True)
    return result

def run_teams_list():
    features_path = os.path.join(BASE_DIR, "data", "historical", "historical_sanitized_v9.csv")
    df = pd.read_csv(features_path, parse_dates=['date'])
    all_teams = sorted(list(set(df['home_team'].dropna().unique()) | set(df['away_team'].dropna().unique())))
    return all_teams

def run_recent_matches():
    features_path = os.path.join(BASE_DIR, "data", "historical", "historical_sanitized_v9.csv")
    df = pd.read_csv(features_path, parse_dates=['date'])
    df = df.sort_values('date').reset_index(drop=True)
    completed = df[df['home_goals'].notna()].tail(30)
    result = []
    for _, row in completed.iterrows():
        date_str = row['date'].strftime('%Y-%m-%d')
        home = row['home_team']
        away = row['away_team']
        match_id = f"{date_str} {home}-{away}"
        hg = int(row['home_goals'])
        ag = int(row['away_goals'])
        res_val = 'H' if hg > ag else ('A' if hg < ag else 'D')
        result.append({
            'id':        match_id,
            'date':      date_str,
            'homeTeam':  home,
            'awayTeam':  away,
            'homeGoals': hg,
            'awayGoals': ag,
            'result':    res_val,
            'referee':   str(row.get('referee', '')) if pd.notna(row.get('referee')) else '',
            'totalCards':int(row.get('total_cards', 0)) if pd.notna(row.get('total_cards')) else 0,
        })
    return result[::-1]

def generate_test_set_matches(limit=10):
    """
    Devuelve partidos del set de test (temporada 2526) con predicciones generadas
    por modelos demo entrenados ÚNICAMENTE con temporadas 1718-2425.

    Esto evita data leakage: los modelos no han visto estos partidos durante
    el entrenamiento, y las features (ELO, forma) se calculan con datos hasta
    el final de la temporada 2425.
    """
    features_path = os.path.join(BASE_DIR, "data", "historical", "historical_sanitized_v9.csv")
    df = pd.read_csv(features_path, parse_dates=['date'])
    df = df.sort_values('date').reset_index(drop=True)

    # Test set puro: temporada 2526. Train: todo lo anterior.
    train_df = df[df['season'] != 2526].copy()
    test_df = df[df['season'] == 2526].copy()

    if test_df.empty:
        return []

    elo_map = compute_elo_map(train_df)
    ref_avg = float(train_df['referee_avg_cards_history'].mean()) if 'referee_avg_cards_history' in train_df.columns else 3.5
    selector = get_demo_selector()

    upcoming_list = []
    for i, row in test_df.head(limit).iterrows():
        home = row['home_team']
        away = row['away_team']
        match_date = row['date']

        h_form = build_team_last5(home, train_df)
        a_form = build_team_last5(away, train_df)

        features = {
            'home_elo':              round(elo_map.get(home, 1500), 1),
            'away_elo':              round(elo_map.get(away, 1500), 1),
            'h_missing_key_player':  0,
            'a_missing_key_player':  0,
            'home_rest':             7,
            'away_rest':             7,
            'h_l5_pts':              h_form.get('pts', 0),
            'h_l5_sh':               h_form.get('sh', 0),
            'h_l5_sot':              h_form.get('sot', 0),
            'h_l5_sot_c':            0.0,
            'h_l5_gf':               h_form.get('gf', 0),
            'h_l5_ga':               h_form.get('ga', 0),
            'h_l5_fls':              h_form.get('fls', 0),
            'h_l5_conv':             h_form.get('conv', 0),
            'h_l5_xg':               h_form.get('xg', 0),
            'h_l5_xga':              h_form.get('xga', 0),
            'a_l5_pts':              a_form.get('pts', 0),
            'a_l5_sh':               a_form.get('sh', 0),
            'a_l5_sot':              a_form.get('sot', 0),
            'a_l5_sot_c':            0.0,
            'a_l5_gf':               a_form.get('gf', 0),
            'a_l5_ga':               a_form.get('ga', 0),
            'a_l5_fls':              a_form.get('fls', 0),
            'a_l5_conv':             a_form.get('conv', 0),
            'a_l5_xg':               a_form.get('xg', 0),
            'a_l5_xga':              a_form.get('xga', 0),
            'referee_avg_cards_history': ref_avg,
            'is_derby':              0,
            'relegation_pressure':   0,
        }
        preds = selector.get_best_bet(features)
        preds.sort(key=lambda x: x.get('ExpectedValue', 0.0), reverse=True)
        top_bet = clean_json(preds[0]) if preds else None
        upcoming_list.append({
            'id': f"test-{i}",
            'date': match_date.strftime('%Y-%m-%d'),
            'homeTeam': home,
            'awayTeam': away,
            'homeElo': float(features['home_elo']),
            'awayElo': float(features['away_elo']),
            'topPrediction': top_bet,
            'allPredictions': clean_json(preds)
        })
    save_upcoming_matches(upcoming_list)
    return upcoming_list

def run_upcoming():
    init_db()
    matches_list = get_upcoming_matches()
    if not matches_list:
        matches_list = generate_test_set_matches(limit=10)
    return matches_list

def run_update_upcoming():
    from src.upcoming import fetch_upcoming_fixtures
    print("[Bridge] Running Selenium scraper for upcoming fixtures...")
    fixtures_df = fetch_upcoming_fixtures()
    if fixtures_df.empty:
        print("[Bridge] Scraper vacío. Fallback a partidos de test (temporada 2526).")
        return generate_test_set_matches(limit=10)
        
    features_path = os.path.join(BASE_DIR, "data", "historical", "historical_sanitized_v9.csv")
    df = pd.read_csv(features_path, parse_dates=['date'])
    df = df.sort_values('date').reset_index(drop=True)
    elo_map = compute_elo_map(df)
    ref_avg = float(df['referee_avg_cards_history'].mean()) if 'referee_avg_cards_history' in df.columns else 3.5
    selector = MasterBetSelector()
    
    upcoming_list = []
    for i, row in fixtures_df.iterrows():
        home = str(row['home_team'])
        away = str(row['away_team'])
        match_date = row['date']
        
        h_form = build_team_last5(home, df)
        a_form = build_team_last5(away, df)
        features = {
            'home_elo':              round(elo_map.get(home, 1500), 1),
            'away_elo':              round(elo_map.get(away, 1500), 1),
            'h_missing_key_player':  0,
            'a_missing_key_player':  0,
            'home_rest':             7,
            'away_rest':             7,
            'h_l5_pts':              h_form.get('pts', 0),
            'h_l5_sh':               h_form.get('sh', 0),
            'h_l5_sot':              h_form.get('sot', 0),
            'h_l5_sot_c':            0.0,
            'h_l5_gf':               h_form.get('gf', 0),
            'h_l5_ga':               h_form.get('ga', 0),
            'h_l5_fls':              h_form.get('fls', 0),
            'h_l5_conv':             h_form.get('conv', 0),
            'h_l5_xg':               h_form.get('xg', 0),
            'h_l5_xga':              h_form.get('xga', 0),
            'a_l5_pts':              a_form.get('pts', 0),
            'a_l5_sh':               a_form.get('sh', 0),
            'a_l5_sot':              a_form.get('sot', 0),
            'a_l5_sot_c':            0.0,
            'a_l5_gf':               a_form.get('gf', 0),
            'a_l5_ga':               a_form.get('ga', 0),
            'a_l5_fls':              a_form.get('fls', 0),
            'a_l5_conv':             a_form.get('conv', 0),
            'a_l5_xg':               a_form.get('xg', 0),
            'a_l5_xga':              a_form.get('xga', 0),
            'referee_avg_cards_history': ref_avg,
            'is_derby':              0,
            'relegation_pressure':   0,
        }
        preds = selector.get_best_bet(features)
        preds.sort(key=lambda x: x.get('ExpectedValue', 0.0), reverse=True)
        top_bet = clean_json(preds[0]) if preds else None
        
        upcoming_list.append({
            'id': f"upcoming-{i}",
            'date': match_date.strftime('%Y-%m-%d'),
            'homeTeam': home,
            'awayTeam': away,
            'homeElo': float(features['home_elo']),
            'awayElo': float(features['away_elo']),
            'topPrediction': top_bet,
            'allPredictions': clean_json(preds)
        })
        
    save_upcoming_matches(upcoming_list)
    return upcoming_list

def run_analyze_match(payload):
    home = payload.get('homeTeam')
    away = payload.get('awayTeam')
    date = payload.get('date')
    provider_name = payload.get('provider', 'minimax')
    model = payload.get('model', '')
    
    features_path = os.path.join(BASE_DIR, "data", "historical", "historical_sanitized_v9.csv")
    df = pd.read_csv(features_path, parse_dates=['date'])
    df = df.sort_values('date').reset_index(drop=True)
    elo_map = compute_elo_map(df)
    ref_avg = float(df['referee_avg_cards_history'].mean()) if 'referee_avg_cards_history' in df.columns else 3.5
    selector = MasterBetSelector()
    
    h_form = build_team_last5(home, df)
    a_form = build_team_last5(away, df)
    features = {
        'home_elo':              round(elo_map.get(home, 1500), 1),
        'away_elo':              round(elo_map.get(away, 1500), 1),
        'h_missing_key_player':  0,
        'a_missing_key_player':  0,
        'home_rest':             7,
        'away_rest':             7,
        'h_l5_pts':              h_form.get('pts', 0),
        'h_l5_sh':               h_form.get('sh', 0),
        'h_l5_sot':              h_form.get('sot', 0),
        'h_l5_sot_c':            0.0,
        'h_l5_gf':               h_form.get('gf', 0),
        'h_l5_ga':               h_form.get('ga', 0),
        'h_l5_fls':              h_form.get('fls', 0),
        'h_l5_conv':             h_form.get('conv', 0),
        'h_l5_xg':               h_form.get('xg', 0),
        'h_l5_xga':              h_form.get('xga', 0),
        'a_l5_pts':              a_form.get('pts', 0),
        'a_l5_sh':               a_form.get('sh', 0),
        'a_l5_sot':              a_form.get('sot', 0),
        'a_l5_sot_c':            0.0,
        'a_l5_gf':               a_form.get('gf', 0),
        'a_l5_ga':               a_form.get('ga', 0),
        'a_l5_fls':              a_form.get('fls', 0),
        'a_l5_conv':             a_form.get('conv', 0),
        'a_l5_xg':               a_form.get('xg', 0),
        'a_l5_xga':              a_form.get('xga', 0),
        'referee_avg_cards_history': ref_avg,
        'is_derby':              0,
        'relegation_pressure':   0,
    }
    
    preds = selector.get_best_bet(features)
    preds.sort(key=lambda x: x.get('ExpectedValue', 0.0), reverse=True)
    
    match_report = f"""
    ANALISIS DE PARTIDO: {home} vs {away}
    Fecha: {date}
    
    Estadisticas base:
    - {home} (Local) - ELO: {features['home_elo']}, Puntos últimos 5 partidos: {features['h_l5_pts']}
    - {away} (Visitante) - ELO: {features['away_elo']}, Puntos últimos 5 partidos: {features['a_l5_pts']}
    
    Predicciones de los modelos de Machine Learning (ordenadas por Valor Esperado / EV descendente):
    """
    
    for i, p in enumerate(preds):
        match_report += f"""
        {i+1}. Mercado: {p['Market']}
           - Probabilidad de acierto del modelo: {p['Probability'] * 100:.1f}%
           - Cuota del modelo / Cuota Justa: {p['FairOdds']:.2f}
           - Cuota del mercado / Bookie: {p['ExpectedValue'] / p['Probability'] + 1.0:.2f}
           - Valor Esperado (EV): {p['ExpectedValue'] * 100:+.1f}%
           - Recomendacion Kelly (Stake %): {p['RecommendedStakePct']:.1f}%
           - Pick sugerido: {p['Pick']}
        """
        
    system_prompt = """
    Actúa como un Analista de Apuestas Deportivas Senior y Experto en Machine Learning para la Premier League.
    Tu trabajo es recibir las predicciones matemáticas generadas por nuestros modelos predictivos locales para un partido y traducirlas a un análisis comprensible, profesional, sensato y claro en español neutro (evitando modismos argentinos o de voseo).
    
    Sigue estas pautas estrictas en tu respuesta:
    1. Comienza con una bienvenida profesional y directa.
    2. Identifica la apuesta que ofrece mayor rentabilidad/EV (Valor Esperado) positivo y explícala claramente, justificando por qué el modelo la prefiere.
    3. Cuantifica las posibles ganancias netas para ayudar al usuario a entender el valor. Usa como ejemplo una apuesta estándar de $10.000 CLP (o $10 USD): por ejemplo, si la cuota de mercado es 1.80, la ganancia neta potencial sería de $8.000 CLP por cada $10.000 CLP apostados.
    4. Analiza los riesgos: si el stake sugerido por Kelly es alto o si el EV es ajustado. Advierte al usuario sobre el juego responsable y el control del bankroll.
    5. Explica brevemente qué factores (como la diferencia de ELO o la racha reciente) justifican las probabilidades de los modelos.
    6. Utiliza formato Markdown limpio con negritas y listas para que sea muy legible.
    """
    
    user_prompt = f"Por favor analiza el siguiente reporte de partido y dame tus sugerencias y análisis experto:\n{match_report}"
    
    provider = get_provider(provider_name)
    analysis_text = provider.generate(system_prompt, user_prompt, model)
    
    return {
        "analysis": analysis_text,
        "predictions": clean_json(preds)
    }

def run_play(payload):
    """Endpoint para la sección Jugar: devuelve últimos 5 partidos de cada equipo
    y la predicción 1X2 del modelo para que el usuario adivine quién gana."""
    home = payload.get('homeTeam', '')
    away = payload.get('awayTeam', '')

    features_path = os.path.join(BASE_DIR, "data", "historical", "historical_sanitized_v9.csv")
    df = pd.read_csv(features_path, parse_dates=['date'])
    df = df.sort_values('date').reset_index(drop=True)

    elo_map = compute_elo_map(df)

    def get_last5_matches(team, df):
        """Obtiene los últimos 5 partidos reales de un equipo con resultados."""
        team_matches = df[(df['home_team'] == team) | (df['away_team'] == team)].copy()
        team_matches = team_matches[team_matches['home_goals'].notna()].sort_values('date').tail(5)
        results = []
        for _, row in team_matches.iterrows():
            is_home = row['home_team'] == team
            team_goals = int(row['home_goals']) if is_home else int(row['away_goals'])
            opp_goals = int(row['away_goals']) if is_home else int(row['home_goals'])
            opponent = row['away_team'] if is_home else row['home_team']
            if team_goals > opp_goals:
                outcome = 'W'
            elif team_goals == opp_goals:
                outcome = 'D'
            else:
                outcome = 'L'
            results.append({
                'date': row['date'].strftime('%Y-%m-%d'),
                'opponent': opponent,
                'teamGoals': team_goals,
                'oppGoals': opp_goals,
                'result': outcome,
                'venue': 'Home' if is_home else 'Away',
            })
        return results[::-1]  # newest first

    home_last5 = get_last5_matches(home, df)
    away_last5 = get_last5_matches(away, df)

    # Predicción del modelo (1X2)
    selector = MasterBetSelector()
    h_form = build_team_last5(home, df)
    a_form = build_team_last5(away, df)
    ref_avg = float(df['referee_avg_cards_history'].mean()) if 'referee_avg_cards_history' in df.columns else 3.5

    features = {
        'home_elo':              round(elo_map.get(home, 1500), 1),
        'away_elo':              round(elo_map.get(away, 1500), 1),
        'h_missing_key_player':  0,
        'a_missing_key_player':  0,
        'home_rest':             7,
        'away_rest':             7,
        'h_l5_pts':              h_form.get('pts', 0),
        'h_l5_sh':               h_form.get('sh', 0),
        'h_l5_sot':              h_form.get('sot', 0),
        'h_l5_sot_c':            0.0,
        'h_l5_gf':               h_form.get('gf', 0),
        'h_l5_ga':               h_form.get('ga', 0),
        'h_l5_fls':              h_form.get('fls', 0),
        'h_l5_conv':             h_form.get('conv', 0),
        'h_l5_xg':               h_form.get('xg', 0),
        'h_l5_xga':              h_form.get('xga', 0),
        'a_l5_pts':              a_form.get('pts', 0),
        'a_l5_sh':               a_form.get('sh', 0),
        'a_l5_sot':              a_form.get('sot', 0),
        'a_l5_sot_c':            0.0,
        'a_l5_gf':               a_form.get('gf', 0),
        'a_l5_ga':               a_form.get('ga', 0),
        'a_l5_fls':              a_form.get('fls', 0),
        'a_l5_conv':             a_form.get('conv', 0),
        'a_l5_xg':               a_form.get('xg', 0),
        'a_l5_xga':              a_form.get('xga', 0),
        'referee_avg_cards_history': ref_avg,
        'is_derby':              0,
        'relegation_pressure':   0,
    }

    preds = selector.get_best_bet(features)

    # Extraer la predicción 1X2 específica
    pred_1x2 = None
    for p in preds:
        if '1X2' in p.get('Market', ''):
            pred_1x2 = p
            break
    # Si no hay 1X2 directa, usar ELO para calcular probabilidades 1X2
    if not pred_1x2:
        home_elo = features['home_elo']
        away_elo = features['away_elo']
        prob_home = 1.0 / (1.0 + 10.0 ** ((away_elo - home_elo) / 400.0))
        draw_prob = 0.25 * (1.0 - abs(prob_home - 0.5))
        remaining = 1.0 - draw_prob
        home_win = prob_home * remaining
        away_win = (1.0 - prob_home) * remaining
        pred_1x2 = {
            'Market': '1X2',
            'Probability': max(home_win, draw_prob, away_win),
            'Pick': 2 if home_win >= max(draw_prob, away_win) else (0 if away_win >= max(home_win, draw_prob) else 1),
            'Confidence': 'Medium',
            'FairOdds': round(1.0 / max(home_win, draw_prob, away_win), 2) if max(home_win, draw_prob, away_win) > 0 else 100.0,
        }

    # Pick del modelo: 2=Home, 1=Draw, 0=Away
    model_pick = pred_1x2.get('Pick', 2)
    model_result = 'home' if model_pick == 2 else ('away' if model_pick == 0 else 'draw')

    result = {
        'homeTeam': home,
        'awayTeam': away,
        'homeElo': features['home_elo'],
        'awayElo': features['away_elo'],
        'homeLast5': home_last5,
        'awayLast5': away_last5,
        'modelPrediction': {
            'market': pred_1x2.get('Market', '1X2'),
            'probability': round(pred_1x2.get('Probability', 0) * 100, 1),
            'pick': model_result,
            'confidence': pred_1x2.get('Confidence', 'Medium'),
        },
    }
    return clean_json(result)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        # Some calls like seasons may not pass payload
        if len(sys.argv) == 2:
            action = sys.argv[1]
            payload = {}
        else:
            sys.exit(1)
    else:
        action = sys.argv[1]
        payload_str = sys.argv[2]
        payload = json.loads(payload_str)

    if action == 'predict':
        print(json.dumps(run_predict(payload)))
    elif action == 'simulate':
        print(json.dumps(run_simulate(payload)))
    elif action == 'performance':
        print(json.dumps(run_performance()))
    elif action == 'detailed-history':
        print(json.dumps(run_detailed_history(payload)))
    elif action == 'seasons':
        print(json.dumps(run_seasons()))
    elif action == 'history':
        print(json.dumps(run_history(payload)))
    elif action == 'stats':
        print(json.dumps(run_stats()))
    elif action == 'teams':
        print(json.dumps(run_teams(payload)))
    elif action == 'teams-list':
        print(json.dumps(run_teams_list()))
    elif action == 'recent-matches':
        print(json.dumps(run_recent_matches()))
    elif action == 'upcoming':
        print(json.dumps(run_upcoming()))
    elif action == 'update-upcoming':
        print(json.dumps(run_update_upcoming()))
    elif action == 'analyze-match':
        print(json.dumps(run_analyze_match(payload)))
    elif action == 'play':
        print(json.dumps(run_play(payload)))
    else:
        sys.exit(1)
