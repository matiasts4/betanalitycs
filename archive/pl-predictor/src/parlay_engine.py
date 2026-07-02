import os
import json
import numpy as np
from src.db import get_upcoming_matches

# Coeficientes de correlación empíricos calculados en base al histórico
SGP_CORRELATIONS = {
    ('home_win', 'over25'): 1.1655,
    ('home_win', 'btts'): 0.8680,
    ('home_win', 'home_clean_sheet'): 1.8127,
    ('over25', 'btts'): 1.4564,
    ('under25', 'btts_no'): 1.6139,
    ('home_win', 'over25', 'btts'): 1.5952
}

def get_event_key(market, pick):
    """Mapea un mercado y pick a una clave estandarizada de evento SGP."""
    m_lower = market.lower()
    if '1x2' in m_lower and pick == 2:
        return 'home_win'
    elif 'over 2.5' in m_lower:
        return 'over25'
    elif 'under 2.5' in m_lower:
        return 'under25'
    elif 'btts' in m_lower:
        if 'no' in m_lower:
            return 'btts_no'
        return 'btts'
    elif 'clean sheet' in m_lower:
        return 'home_clean_sheet'
    return None

def get_real_odd(market, pick, odds_dict):
    """Retrieves the real odd for a given market and pick from a scraped odds dictionary."""
    if not odds_dict:
        return None
    m_lower = market.lower()
    if '1x2' in m_lower:
        if pick == 2:
            return odds_dict.get('home')
        elif pick == 0:
            return odds_dict.get('away')
        else:
            return odds_dict.get('draw')
    elif 'over 2.5' in m_lower:
        return odds_dict.get('over25')
    elif 'under 2.5' in m_lower:
        return odds_dict.get('under25')
    elif 'btts' in m_lower:
        if 'no' in m_lower:
            return odds_dict.get('btts_no')
        else:
            return odds_dict.get('btts_yes')
    return None

def build_multi_match_parlays(odds_source='average'):
    """Generates suggested doubles and trebles with positive EV from upcoming matches."""
    matches = get_upcoming_matches()
    
    # 1. Extraer todas las selecciones individuales con +EV real
    selections = []
    for m in matches:
        odds_dict = m.get('max_odds') if odds_source == 'maximum' else m.get('odds')
        if not odds_dict:
            continue
            
        all_preds = m.get('allPredictions', [])
        if not all_preds and m.get('topPrediction'):
            all_preds = [m['topPrediction']]
            
        for p in all_preds:
            market = p.get('Market')
            pick = p.get('Pick', 1)
            prob = p.get('Probability', 0.0)
            
            odd = get_real_odd(market, pick, odds_dict)
            if odd is None or odd <= 1.0:
                continue
                
            ev = (prob * odd) - 1.0
            
            if ev >= 0.0:
                selections.append({
                    'match_id': m['id'],
                    'home_team': m['homeTeam'],
                    'away_team': m['awayTeam'],
                    'date': m['date'],
                    'market': market,
                    'pick': pick,
                    'probability': prob,
                    'odd': odd,
                    'ev': ev,
                    'provider': odds_dict.get('provider', 'Desconocido') if odds_source == 'average' else 'Mercado Máximo'
                })

    # 2. Generar combinadas (Dobles)
    doubles = []
    for i in range(len(selections)):
        for j in range(i + 1, len(selections)):
            sel1 = selections[i]
            sel2 = selections[j]
            
            if sel1['match_id'] == sel2['match_id']:
                continue
                
            prob_combined = sel1['probability'] * sel2['probability']
            odd_combined = round(sel1['odd'] * sel2['odd'], 2)
            ev_combined = (prob_combined * odd_combined) - 1.0
            
            b = odd_combined - 1.0
            q = 1.0 - prob_combined
            kelly_pct = 0.0
            if b > 0:
                kelly_pct = max(0.0, (prob_combined * b - q) / b) * 0.1  # 1/10 Kelly
                
            doubles.append({
                'type': 'Doble',
                'selections': [sel1, sel2],
                'odds': odd_combined,
                'probability': prob_combined,
                'ev': ev_combined,
                'recommended_stake_pct': round(kelly_pct * 100, 2)
            })

    # 3. Generar combinadas (Triples)
    trebles = []
    for i in range(len(selections)):
        for j in range(i + 1, len(selections)):
            for k in range(j + 1, len(selections)):
                sel1 = selections[i]
                sel2 = selections[j]
                sel3 = selections[k]
                
                if (sel1['match_id'] == sel2['match_id'] or 
                    sel1['match_id'] == sel3['match_id'] or 
                    sel2['match_id'] == sel3['match_id']):
                    continue
                    
                prob_combined = sel1['probability'] * sel2['probability'] * sel3['probability']
                odd_combined = round(sel1['odd'] * sel2['odd'] * sel3['odd'], 2)
                ev_combined = (prob_combined * odd_combined) - 1.0
                
                b = odd_combined - 1.0
                q = 1.0 - prob_combined
                kelly_pct = 0.0
                if b > 0:
                    kelly_pct = max(0.0, (prob_combined * b - q) / b) * 0.05  # 1/20 Kelly
                    
                trebles.append({
                    'type': 'Triple',
                    'selections': [sel1, sel2, sel3],
                    'odds': odd_combined,
                    'probability': prob_combined,
                    'ev': ev_combined,
                    'recommended_stake_pct': round(kelly_pct * 100, 2)
                })

    doubles.sort(key=lambda x: x['ev'], reverse=True)
    trebles.sort(key=lambda x: x['ev'], reverse=True)
    
    return {
        'doubles': doubles[:5],
        'trebles': trebles[:5]
    }

def calculate_sgp(sels, ratio, odd_sgp_real=None, bookmaker_margin=0.92):
    """
    Compute the correlated Same-Game Parlay probability, fair odds and EV.

    Parameters
    ----------
    sels : list[dict]
        Each dict must have 'probability' and 'odd' keys.
    ratio : float
        Empirical correlation ratio (multiplies the independent joint probability).
    odd_sgp_real : float | None
        Actual SGP price offered by the bookmaker. If None, the fair combined
        odd is estimated and a bookmaker margin is applied.
    bookmaker_margin : float
        Margin applied to the fair combined odd when no real SGP price is given.

    Returns
    -------
    dict with 'probability', 'odds', 'ev', 'kelly_pct' or None if invalid.
    """
    p_independent = np.prod([s['probability'] for s in sels])
    prob_combined = min(0.9999, p_independent * ratio)

    if prob_combined <= 0.0:
        return None

    if odd_sgp_real is not None and odd_sgp_real > 1.0:
        odd_combined = round(odd_sgp_real, 2)
    else:
        fair_odd_combined = 1.0 / prob_combined
        odd_combined = round(max(1.05, fair_odd_combined * bookmaker_margin), 2)

    ev_combined = (prob_combined * odd_combined) - 1.0

    b = odd_combined - 1.0
    q = 1.0 - prob_combined
    kelly_pct = 0.0
    if b > 0:
        kelly_pct = max(0.0, (prob_combined * b - q) / b) * 0.05

    return {
        'probability': prob_combined,
        'odds': odd_combined,
        'ev': ev_combined,
        'kelly_pct': kelly_pct,
    }


def build_same_game_parlays(odds_source='average'):
    """Genera Same-Game Parlays recomendados con valor real corregido por correlación."""
    matches = get_upcoming_matches()
    sgps = []
    
    for m in matches:
        odds_dict = m.get('max_odds') if odds_source == 'maximum' else m.get('odds')
        if not odds_dict:
            continue
            
        all_preds = m.get('allPredictions', [])
        if not all_preds and m.get('topPrediction'):
            all_preds = [m['topPrediction']]
            
        # Indexar predicciones por clave de evento
        pred_map = {}
        for p in all_preds:
            market = p.get('Market')
            pick = p.get('Pick', 1)
            event_key = get_event_key(market, pick)
            if event_key:
                odd = get_real_odd(market, pick, odds_dict)
                if odd and odd > 1.0:
                    pred_map[event_key] = {
                        'market': market,
                        'pick': pick,
                        'probability': p.get('Probability', 0.0),
                        'odd': odd
                    }
                    
        # Evaluar cada combinación de correlación
        for combo, ratio in SGP_CORRELATIONS.items():
            if all(k in pred_map for k in combo):
                sels = [pred_map[k] for k in combo]
                result = calculate_sgp(sels, ratio)
                if result is None:
                    continue

                if result['ev'] >= 0.0:
                    selections_formatted = []
                    for s in sels:
                        selections_formatted.append({
                            'match_id': m['id'],
                            'home_team': m['homeTeam'],
                            'away_team': m['awayTeam'],
                            'date': m['date'],
                            'market': s['market'],
                            'pick': s['pick'],
                            'probability': s['probability'],
                            'odd': s['odd'],
                            'provider': odds_dict.get('provider', 'Desconocido') if odds_source == 'average' else 'Mercado Máximo'
                        })
                        
                    sgps.append({
                        'type': 'Same-Game Parlay',
                        'match_name': f"{m['homeTeam']} vs {m['awayTeam']}",
                        'selections': selections_formatted,
                        'odds': result['odds'],
                        'probability': result['probability'],
                        'ev': result['ev'],
                        'recommended_stake_pct': round(result['kelly_pct'] * 100, 2)
                    })
                    
    sgps.sort(key=lambda x: x['ev'], reverse=True)
    return sgps[:5]

def build_parlays(odds_source='average'):
    """Generates suggested doubles, trebles, and same-game parlays from upcoming matches."""
    doubles_and_trebles = build_multi_match_parlays(odds_source=odds_source)
    sgps = build_same_game_parlays(odds_source=odds_source)
    
    return {
        'doubles': doubles_and_trebles['doubles'],
        'trebles': doubles_and_trebles['trebles'],
        'same_game': sgps
    }
