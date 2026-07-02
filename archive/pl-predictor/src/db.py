import os
import sqlite3
import json

# DB path is relative to this file: archive/pl-predictor/src/db.py
# Resolves to: pl-web/pl_web.db
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../pl-web/pl_web.db"))

def get_connection():
    # Ensure directory exists
    db_dir = os.path.dirname(DB_PATH)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS upcoming_matches (
            id TEXT PRIMARY KEY,
            date TEXT,
            home_team TEXT,
            away_team TEXT,
            home_elo REAL,
            away_elo REAL,
            top_market TEXT,
            top_probability REAL,
            top_confidence TEXT,
            top_pick INTEGER,
            top_fair_odds REAL,
            top_ev REAL,
            top_stake_pct REAL,
            all_predictions TEXT
        )
    """)
    conn.commit()
    
    # Schema Migration: Add new odds columns if they do not exist
    cursor.execute("PRAGMA table_info(upcoming_matches)")
    columns = [row['name'] for row in cursor.fetchall()]
    
    new_columns = {
        'odds_home': 'REAL',
        'odds_draw': 'REAL',
        'odds_away': 'REAL',
        'odds_over25': 'REAL',
        'odds_under25': 'REAL',
        'odds_btts_yes': 'REAL',
        'odds_btts_no': 'REAL',
        'odds_provider': 'TEXT',
        'odds_fetched_at': 'TEXT',
        'odds_max_home': 'REAL',
        'odds_max_draw': 'REAL',
        'odds_max_away': 'REAL',
        'odds_max_over25': 'REAL',
        'odds_max_under25': 'REAL',
        'odds_max_btts_yes': 'REAL',
        'odds_max_btts_no': 'REAL',
        'all_providers_odds': 'TEXT',
        'odds_is_simulated': 'INTEGER',
    }
    
    mutated = False
    for col_name, col_type in new_columns.items():
        if col_name not in columns:
            cursor.execute(f"ALTER TABLE upcoming_matches ADD COLUMN {col_name} {col_type}")
            mutated = True
            
    if mutated:
        conn.commit()
    conn.close()

def save_upcoming_matches(matches_list):
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    
    # Clear the table first
    cursor.execute("DELETE FROM upcoming_matches")
    
    for m in matches_list:
        top_pred = m.get('topPrediction') or {}
        odds = m.get('odds') or {}
        max_odds = m.get('max_odds') or {}
        
        is_simulated = 1 if (odds.get('is_simulated') or m.get('odds_is_simulated')) else 0
        cursor.execute("""
            INSERT INTO upcoming_matches (
                id, date, home_team, away_team, home_elo, away_elo,
                top_market, top_probability, top_confidence, top_pick,
                top_fair_odds, top_ev, top_stake_pct, all_predictions,
                odds_home, odds_draw, odds_away,
                odds_over25, odds_under25,
                odds_btts_yes, odds_btts_no,
                odds_provider, odds_fetched_at, odds_is_simulated,
                odds_max_home, odds_max_draw, odds_max_away,
                odds_max_over25, odds_max_under25,
                odds_max_btts_yes, odds_max_btts_no,
                all_providers_odds
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            m['id'],
            m['date'],
            m['homeTeam'],
            m['awayTeam'],
            m['homeElo'],
            m['awayElo'],
            top_pred.get('Market'),
            top_pred.get('Probability'),
            top_pred.get('Confidence'),
            top_pred.get('Pick'),
            top_pred.get('FairOdds'),
            top_pred.get('ExpectedValue'),
            top_pred.get('RecommendedStakePct'),
            json.dumps(m.get('allPredictions', [])),
            m.get('odds_home') or odds.get('home'),
            m.get('odds_draw') or odds.get('draw'),
            m.get('odds_away') or odds.get('away'),
            m.get('odds_over25') or odds.get('over25'),
            m.get('odds_under25') or odds.get('under25'),
            m.get('odds_btts_yes') or odds.get('btts_yes'),
            m.get('odds_btts_no') or odds.get('btts_no'),
            m.get('odds_provider') or odds.get('provider'),
            m.get('odds_fetched_at') or odds.get('fetched_at'),
            is_simulated,
            odds.get('max_home') or max_odds.get('home') or m.get('odds_max_home'),
            odds.get('max_draw') or max_odds.get('draw') or m.get('odds_max_draw'),
            odds.get('max_away') or max_odds.get('away') or m.get('odds_max_away'),
            odds.get('max_over25') or max_odds.get('over25') or m.get('odds_max_over25'),
            odds.get('max_under25') or max_odds.get('under25') or m.get('odds_max_under25'),
            odds.get('max_btts_yes') or max_odds.get('btts_yes') or m.get('odds_max_btts_yes'),
            odds.get('max_btts_no') or max_odds.get('btts_no') or m.get('odds_max_btts_no'),
            json.dumps(odds.get('all_providers') or m.get('all_providers_odds') or m.get('all_providers') or {})
        ))
        
    conn.commit()
    conn.close()

def get_upcoming_matches():
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM upcoming_matches ORDER BY date ASC")
    rows = cursor.fetchall()
    conn.close()
    
    result = []
    for r in rows:
        top_pred = None
        if r['top_market']:
            top_pred = {
                'Market': r['top_market'],
                'Probability': r['top_probability'],
                'Confidence': r['top_confidence'],
                'Pick': r['top_pick'],
                'FairOdds': r['top_fair_odds'],
                'ExpectedValue': r['top_ev'],
                'RecommendedStakePct': r['top_stake_pct']
            }
        
        odds = None
        if r['odds_home'] is not None or r['odds_provider'] is not None:
            odds = {
                'home': r['odds_home'],
                'draw': r['odds_draw'],
                'away': r['odds_away'],
                'over25': r['odds_over25'],
                'under25': r['odds_under25'],
                'btts_yes': r['odds_btts_yes'],
                'btts_no': r['odds_btts_no'],
                'provider': r['odds_provider'],
                'fetched_at': r['odds_fetched_at'],
                'is_simulated': bool(r['odds_is_simulated']) if 'odds_is_simulated' in cols else None,
            }
            
        max_odds = None
        # Validar si las columnas maximas existen en el row
        cols = r.keys()
        if 'odds_max_home' in cols and r['odds_max_home'] is not None:
            max_odds = {
                'home': r['odds_max_home'],
                'draw': r['odds_max_draw'],
                'away': r['odds_max_away'],
                'over25': r['odds_max_over25'],
                'under25': r['odds_max_under25'],
                'btts_yes': r['odds_max_btts_yes'],
                'btts_no': r['odds_max_btts_no']
            }
            
        all_providers = None
        if 'all_providers_odds' in cols and r['all_providers_odds']:
            try:
                all_providers = json.loads(r['all_providers_odds'])
            except:
                pass
            
        result.append({
            'id': r['id'],
            'date': r['date'],
            'homeTeam': r['home_team'],
            'awayTeam': r['away_team'],
            'homeElo': r['home_elo'],
            'awayElo': r['away_elo'],
            'topPrediction': top_pred,
            'allPredictions': json.loads(r['all_predictions'] or '[]'),
            'odds': odds,
            'max_odds': max_odds,
            'all_providers_odds': all_providers
        })
    return result
