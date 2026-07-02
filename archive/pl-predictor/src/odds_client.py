import os
import sqlite3
import random
import requests
from datetime import datetime
from src.db import get_connection, init_db

# Configuration
THE_ODDS_API_URL = "https://api.the-odds-api.com/v4/sports/{sport}/odds"
SPORTS_SUPPORTED = {
    "soccer_epl": "Premier League",
    "soccer_spain_la_liga": "La Liga"
}

TEAM_MAPPING = {
    # Premier League (The Odds API -> FBref)
    'Manchester United': 'Manchester Utd',
    'Manchester City': 'Manchester City',
    'Tottenham Hotspur': 'Tottenham Hotspur',
    'Newcastle United': 'Newcastle United',
    'West Ham United': 'West Ham United',
    'Leicester City': 'Leicester City',
    'Nottingham Forest': 'Nottingham Forest',
    'Sheffield United': 'Sheffield Utd',
    'Wolverhampton Wanderers': 'Wolves',
    'Brighton and Hove Albion': 'Brighton',
    'Bournemouth': 'Bournemouth',
    'Aston Villa': 'Aston Villa',
    'Chelsea': 'Chelsea',
    'Arsenal': 'Arsenal',
    'Liverpool': 'Liverpool',
    'Everton': 'Everton',
    'Crystal Palace': 'Crystal Palace',
    'Fulham': 'Fulham',
    'Brentford': 'Brentford',
    'Luton Town': 'Luton Town',
    'Burnley': 'Burnley',
    'Ipswich Town': 'Ipswich Town',
    'Southampton': 'Southampton',
    
    # La Liga (The Odds API -> FBref / standard name)
    'Real Madrid': 'Real Madrid',
    'Barcelona': 'Barcelona',
    'Atletico Madrid': 'Atlético Madrid',
    'Real Sociedad': 'Real Sociedad',
    'Real Betis': 'Real Betis',
    'Athletic Bilbao': 'Athletic Club',
    'Villarreal': 'Villarreal',
    'Sevilla': 'Sevilla',
    'Valencia': 'Valencia',
    'Girona': 'Girona',
    'Celta Vigo': 'Celta Vigo',
    'Osasuna': 'Osasuna',
    'Getafe': 'Getafe',
    'Las Palmas': 'Las Palmas',
    'Mallorca': 'Mallorca',
    'Rayo Vallecano': 'Rayo Vallecano',
    'Deportivo Alaves': 'Alavés',
    'Leganes': 'Leganés',
    'Valladolid': 'Valladolid',
    'Espanyol': 'Espanyol'
}

def normalize_team_name(team_name):
    """Translates the team name using TEAM_MAPPING or returns it stripped if no match."""
    cleaned = team_name.strip()
    return TEAM_MAPPING.get(cleaned, cleaned)

def get_api_key():
    """Gets the API key from environment variables."""
    return os.environ.get("THE_ODDS_API_KEY", "").strip()

def fetch_odds_from_api(sport, api_key):
    """Fetches odds from The Odds API for a given sport."""
    url = THE_ODDS_API_URL.format(sport=sport)
    params = {
        "apiKey": api_key,
        "regions": "eu",
        "markets": "h2h,totals,btts",
        "oddsFormat": "decimal"
    }
    
    try:
        print(f"[Odds API] Fetching odds for {sport}...")
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"[Odds API Error] Status Code: {response.status_code}, Response: {response.text}")
            return None
    except Exception as e:
        print(f"[Odds API Error] Request failed: {e}")
        return None

def generate_mock_odds():
    """Generates realistic mock odds for simulation."""
    odds = {
        "home": round(random.uniform(1.30, 4.50), 2),
        "draw": round(random.uniform(2.80, 4.00), 2),
        "away": round(random.uniform(1.80, 7.00), 2),
        "over25": round(random.uniform(1.50, 2.30), 2),
        "under25": round(random.uniform(1.60, 2.40), 2),
        "btts_yes": round(random.uniform(1.45, 2.10), 2),
        "btts_no": round(random.uniform(1.65, 2.45), 2),
        "provider": "MOCK_BOOKMAKER_SIMULATED",
        "fetched_at": datetime.utcnow().isoformat() + "Z",
        "is_simulated": True,
    }
    # In mock mode there is no real line shopping, so max_odds == average odds
    odds.update({
        "max_home": odds["home"],
        "max_draw": odds["draw"],
        "max_away": odds["away"],
        "max_over25": odds["over25"],
        "max_under25": odds["under25"],
        "max_btts_yes": odds["btts_yes"],
        "max_btts_no": odds["btts_no"],
        "all_providers": {
            "MOCK_BOOKMAKER_SIMULATED": {
                "home": odds["home"], "draw": odds["draw"], "away": odds["away"],
                "over25": odds["over25"], "under25": odds["under25"],
                "btts_yes": odds["btts_yes"], "btts_no": odds["btts_no"],
            }
        }
    })
    return odds

def update_sqlite_with_odds(home_team, away_team, odds):
    """Updates the upcoming matches table in SQLite with fetched odds (including max odds and providers JSON)."""
    conn = get_connection()
    cursor = conn.cursor()
    import json
    
    # Try to find the match in the database by normalized team names
    cursor.execute("""
        UPDATE upcoming_matches
        SET 
            odds_home = ?,
            odds_draw = ?,
            odds_away = ?,
            odds_over25 = ?,
            odds_under25 = ?,
            odds_btts_yes = ?,
            odds_btts_no = ?,
            odds_provider = ?,
            odds_fetched_at = ?,
            odds_max_home = ?,
            odds_max_draw = ?,
            odds_max_away = ?,
            odds_max_over25 = ?,
            odds_max_under25 = ?,
            odds_max_btts_yes = ?,
            odds_max_btts_no = ?,
            all_providers_odds = ?
        WHERE home_team = ? AND away_team = ?
    """, (
        odds.get('home'),
        odds.get('draw'),
        odds.get('away'),
        odds.get('over25'),
        odds.get('under25'),
        odds.get('btts_yes'),
        odds.get('btts_no'),
        odds.get('provider'),
        odds.get('fetched_at'),
        odds.get('max_home'),
        odds.get('max_draw'),
        odds.get('max_away'),
        odds.get('max_over25'),
        odds.get('max_under25'),
        odds.get('max_btts_yes'),
        odds.get('max_btts_no'),
        json.dumps(odds.get('all_providers') or {}),
        home_team,
        away_team
    ))
    
    rowcount = cursor.rowcount
    conn.commit()
    conn.close()
    return rowcount > 0

def process_api_response(data):
    """Parses API response and updates matches in the database."""
    if not data:
        return 0
        
    updates_count = 0
    for match in data:
        home_normal = normalize_team_name(match['home_team'])
        away_normal = normalize_team_name(match['away_team'])
        
        # Select best bookmaker: Pinnacle, Bet365, Betfair, or first available
        bookmakers = match.get('bookmakers', [])
        if not bookmakers:
            continue
            
        selected_bookmaker = None
        for key in ['pinnacle', 'bet365', 'betfair_ex_uk']:
            for b in bookmakers:
                if b['key'] == key:
                    selected_bookmaker = b
                    break
            if selected_bookmaker:
                break
                
        if not selected_bookmaker:
            selected_bookmaker = bookmakers[0]
            
        odds_dict = {
            'home': None, 'draw': None, 'away': None,
            'over25': None, 'under25': None,
            'btts_yes': None, 'btts_no': None,
            'provider': selected_bookmaker['title'],
            'fetched_at': datetime.utcnow().isoformat() + "Z",
            'is_simulated': False,
        }
        
        for market in selected_bookmaker.get('markets', []):
            m_key = market['key']
            outcomes = market.get('outcomes', [])
            
            if m_key == 'h2h':
                for o in outcomes:
                    if o['name'] == match['home_team']:
                        odds_dict['home'] = float(o['price'])
                    elif o['name'] == match['away_team']:
                        odds_dict['away'] = float(o['price'])
                    elif o['name'] == 'Draw':
                        odds_dict['draw'] = float(o['price'])
            elif m_key == 'totals':
                for o in outcomes:
                    # Target 2.5 totals line
                    if o.get('point') == 2.5:
                        if o['name'] == 'Over':
                            odds_dict['over25'] = float(o['price'])
                        elif o['name'] == 'Under':
                            odds_dict['under25'] = float(o['price'])
            elif m_key == 'btts':
                for o in outcomes:
                    if o['name'] == 'Yes':
                        odds_dict['btts_yes'] = float(o['price'])
                    elif o['name'] == 'No':
                        odds_dict['btts_no'] = float(o['price'])
                        
        # Build max odds and all_providers map across every bookmaker
        max_odds = {
            'max_home': None, 'max_draw': None, 'max_away': None,
            'max_over25': None, 'max_under25': None,
            'max_btts_yes': None, 'max_btts_no': None,
        }
        all_providers = {}
        for b in bookmakers:
            provider_name = b['title']
            provider_odds = {
                'home': None, 'draw': None, 'away': None,
                'over25': None, 'under25': None,
                'btts_yes': None, 'btts_no': None,
            }
            for market in b.get('markets', []):
                m_key = market['key']
                outcomes = market.get('outcomes', [])
                if m_key == 'h2h':
                    for o in outcomes:
                        if o['name'] == match['home_team']:
                            provider_odds['home'] = float(o['price'])
                        elif o['name'] == match['away_team']:
                            provider_odds['away'] = float(o['price'])
                        elif o['name'] == 'Draw':
                            provider_odds['draw'] = float(o['price'])
                elif m_key == 'totals':
                    for o in outcomes:
                        if o.get('point') == 2.5:
                            if o['name'] == 'Over':
                                provider_odds['over25'] = float(o['price'])
                            elif o['name'] == 'Under':
                                provider_odds['under25'] = float(o['price'])
                elif m_key == 'btts':
                    for o in outcomes:
                        if o['name'] == 'Yes':
                            provider_odds['btts_yes'] = float(o['price'])
                        elif o['name'] == 'No':
                            provider_odds['btts_no'] = float(o['price'])
            all_providers[provider_name] = provider_odds
            for key in provider_odds:
                if provider_odds[key] is not None:
                    max_key = 'max_' + key
                    if max_odds[max_key] is None or provider_odds[key] > max_odds[max_key]:
                        max_odds[max_key] = provider_odds[key]

        odds_dict.update(max_odds)
        odds_dict['all_providers'] = all_providers

        # Only update if we got at least 1X2 odds
        if odds_dict['home'] is not None:
            success = update_sqlite_with_odds(home_normal, away_normal, odds_dict)
            if success:
                updates_count += 1
                
    return updates_count

def run_odds_update():
    """Main execution entry point to update odds."""
    init_db()
    api_key = get_api_key()
    
    if not api_key:
        print("[Odds Update] No se detecto THE_ODDS_API_KEY. Corriendo en Modo SIMULADO (Mock)...")
        # In mock mode, we update existing SQLite upcoming matches with realistic mock odds
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT home_team, away_team FROM upcoming_matches")
        matches = cursor.fetchall()
        conn.close()
        
        if not matches:
            print("[Odds Update] No hay partidos futuros en SQLite para simular cuotas.")
            return False
            
        updated = 0
        for m in matches:
            mock_odds = generate_mock_odds()
            success = update_sqlite_with_odds(m['home_team'], m['away_team'], mock_odds)
            if success:
                updated += 1
                
        print(f"[Odds Update] Modo Simulado: Cuotas cargadas exitosamente para {updated} partidos.")
        return True
    
    # Real API execution
    print("[Odds Update] Ejecutando consulta real a The Odds API...")
    total_updated = 0
    for sport in SPORTS_SUPPORTED.keys():
        odds_data = fetch_odds_from_api(sport, api_key)
        if odds_data:
            updated = process_api_response(odds_data)
            print(f"[Odds Update] Ligas {SPORTS_SUPPORTED[sport]}: {updated} partidos actualizados.")
            total_updated += updated
            
    print(f"[Odds Update] Finalizado. Total de partidos con cuotas reales acoplados: {total_updated}")
    return True

if __name__ == '__main__':
    run_odds_update()
