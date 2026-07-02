import os
import requests
from datetime import datetime
from src.db import get_connection, init_db
from src.odds_client import normalize_team_name, update_sqlite_with_odds, generate_mock_odds

# Configuration for odds-api.net
BASE_URL = "https://api.odds-api.net/v1"
SPORTS_MAPPING = {
    # sport_slug, league_slug
    "Premier League": ("soccer", "EPL"),
    "La Liga": ("soccer", "LaLiga")
}

def get_api_key():
    """Gets the API key from environment variables."""
    return os.environ.get("ODDS_API_NET_KEY", "").strip()

def fetch_events(sport, league, api_key):
    """Fetches upcoming events for a given league."""
    url = f"{BASE_URL}/events"
    headers = {"X-API-Key": api_key}
    params = {
        "sport": sport,
        "league": league,
        "status": "upcoming",
        "limit": 20
    }
    
    try:
        print(f"[Odds-API.net] Fetching events for {league}...")
        response = requests.get(url, headers=headers, params=params, timeout=10)
        if response.status_code == 200:
            return response.json().get("items", [])
        else:
            print(f"[Odds-API.net Error] Status: {response.status_code}, Msg: {response.text}")
            return []
    except Exception as e:
        print(f"[Odds-API.net Error] Fetch events failed: {e}")
        return []

def fetch_event_odds_snapshot(event_id, api_key):
    """Fetches the odds snapshot for a specific event."""
    url = f"{BASE_URL}/events/{event_id}/odds/snapshot"
    headers = {"X-API-Key": api_key}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"[Odds-API.net Error] Odds status: {response.status_code}")
            return None
    except Exception as e:
        print(f"[Odds-API.net Error] Fetch odds snapshot failed: {e}")
        return None

def process_event_odds(event_data, odds_data):
    """Parses odds-api.net snapshot data and updates SQLite database."""
    if not odds_data:
        return False
        
    home = normalize_team_name(event_data['home_team'])
    away = normalize_team_name(event_data['away_team'])
    
    # We look for a preferred bookmaker like Pinnacle or Bet365 in odds_data
    # odds_data format typically contains dict of bookmakers/markets or list
    bookmakers = odds_data.get('bookmakers', {})
    if not bookmakers:
        return False
        
    # Select best bookmaker
    selected_key = None
    for key in ['pinnacle', 'bet365', 'betfair']:
        if key in bookmakers:
            selected_key = key
            break
            
    if not selected_key:
        # Fallback to the first available key
        keys = list(bookmakers.keys())
        if not keys:
            return False
        selected_key = keys[0]
        
    bm_data = bookmakers[selected_key]
    provider_title = bm_data.get('title', selected_key.capitalize())
    markets = bm_data.get('markets', {})
    
    odds_dict = {
        'home': None, 'draw': None, 'away': None,
        'over25': None, 'under25': None,
        'btts_yes': None, 'btts_no': None,
        'provider': provider_title,
        'fetched_at': datetime.utcnow().isoformat() + "Z"
    }
    
    # Parse 1X2 (h2h)
    h2h = markets.get('h2h', {})
    outcomes = h2h.get('outcomes', [])
    for o in outcomes:
        if o['name'] == event_data['home_team']:
            odds_dict['home'] = float(o['price'])
        elif o['name'] == event_data['away_team']:
            odds_dict['away'] = float(o['price'])
        elif o['name'] == 'Draw':
            odds_dict['draw'] = float(o['price'])
            
    # Parse Totals Over/Under 2.5
    totals = markets.get('totals', {})
    for o in totals.get('outcomes', []):
        if o.get('point') == 2.5:
            if o['name'] == 'Over':
                odds_dict['over25'] = float(o['price'])
            elif o['name'] == 'Under':
                odds_dict['under25'] = float(o['price'])
                
    # Parse BTTS
    btts = markets.get('btts', {})
    for o in btts.get('outcomes', []):
        if o['name'] == 'Yes':
            odds_dict['btts_yes'] = float(o['price'])
        elif o['name'] == 'No':
            odds_dict['btts_no'] = float(o['price'])
            
    # Update SQLite database
    if odds_dict['home'] is not None:
        return update_sqlite_with_odds(home, away, odds_dict)
    return False

def run_odds_api_net_update():
    """Main execution path for odds-api.net."""
    init_db()
    api_key = get_api_key()
    
    if not api_key:
        print("[Odds-API.net] No se detecto la clave ODDS_API_NET_KEY. Corriendo en Modo SIMULADO (Mock)...")
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT home_team, away_team FROM upcoming_matches")
        matches = cursor.fetchall()
        conn.close()
        
        if not matches:
            print("[Odds-API.net] No hay partidos en SQLite para simular.")
            return False
            
        updated = 0
        for m in matches:
            mock_odds = generate_mock_odds()
            success = update_sqlite_with_odds(m['home_team'], m['away_team'], mock_odds)
            if success:
                updated += 1
        print(f"[Odds-API.net Mock] Cuotas simuladas cargadas para {updated} partidos.")
        return True
        
    print("[Odds-API.net] Iniciando descarga real de cuotas...")
    total_updated = 0
    for league_name, (sport, league) in SPORTS_MAPPING.items():
        events = fetch_events(sport, league, api_key)
        print(f"[Odds-API.net] {league_name}: {len(events)} eventos encontrados.")
        
        for ev in events:
            event_id = ev.get('id')
            if not event_id:
                continue
                
            odds_data = fetch_event_odds_snapshot(event_id, api_key)
            if odds_data:
                success = process_event_odds(ev, odds_data)
                if success:
                    total_updated += 1
                    
    print(f"[Odds-API.net] Actualizacion completada. {total_updated} partidos actualizados.")
    return True

if __name__ == '__main__':
    run_odds_api_net_update()
