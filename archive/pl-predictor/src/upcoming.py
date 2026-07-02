import os
import time
import pandas as pd
import numpy as np
import io
from datetime import datetime, timedelta

FBREF_URL = "https://fbref.com/en/comps/9/schedule/Premier-League-Scores-and-Fixtures"

def _get_html_with_browser(url: str) -> str:
    """Uses SeleniumBase (undetected-chromedriver) to load a page and return its HTML.
    Opens a visible Chrome window so the user can solve any Cloudflare CAPTCHA if needed.
    """
    from seleniumbase import Driver

    driver = Driver(uc=True, headless=False)
    try:
        print(f"[Scraper] Abriendo navegador: {url}")
        driver.get(url)

        # Wait for Cloudflare to clear
        timeout = 60
        start = time.time()
        while time.time() - start < timeout:
            title = driver.title.lower()
            src   = driver.page_source.lower()
            if "just a moment" not in title and "challenge" not in title and "enable javascript" not in src:
                print("[Scraper] Pagina cargada sin Cloudflare.")
                break
            print("[Scraper] Esperando Cloudflare...")
            time.sleep(3)

        time.sleep(2)  # Extra wait for JS-rendered tables
        html = driver.page_source
        return html
    finally:
        try:
            driver.quit()
        except:
            pass

def fetch_upcoming_fixtures():
    """Scrapes FBref for the next 7-30 days of Premier League fixtures using a real browser."""
    print(f"[Scraper] Iniciando extraccion de proximos partidos desde: {FBREF_URL}")
    try:
        html_content = _get_html_with_browser(FBREF_URL)
        if not html_content or len(html_content) < 1000:
            print("  [Error] El HTML obtenido es demasiado corto o esta vacio. Posible bloqueo de Cloudflare.")
            return pd.DataFrame()
            
        all_tables = pd.read_html(io.StringIO(html_content))
    except Exception as e:
        err_msg = str(e)
        if len(err_msg) > 500:
            err_msg = err_msg[:500] + " ... [Truncated HTML Dump]"
        print(f"  [Error] Error fatal durante el scraping: {err_msg}")
        return pd.DataFrame()

    # Find the schedule table - it's the one that contains 'Home' and 'Away' columns
    fixtures = None
    for t in all_tables:
        cols = [str(c).strip() for c in t.columns]
        if any('Home' in c for c in cols) and any('Away' in c for c in cols):
            fixtures = t
            fixtures.columns = cols
            break

    if fixtures is None:
        print(f"  [Warning] Advertencia: No se encontro la tabla de fixtures con columnas 'Home'/'Away'. Tablas detectadas: {len(all_tables)}")
        if len(all_tables) > 0:
            print(f"  Columnas de la primera tabla: {list(all_tables[0].columns)}")
        return pd.DataFrame()

    score_col = next((c for c in fixtures.columns if 'Score' in c), None)
    home_col  = next((c for c in fixtures.columns if 'Home' in c), None)
    away_col  = next((c for c in fixtures.columns if 'Away' in c), None)
    date_col  = next((c for c in fixtures.columns if c == 'Date'), None)

    if not all([home_col, away_col, date_col]):
        print(f"  [Error] Error: No se pudieron mapear las columnas necesarias (Home, Away, Date). Encontradas: {list(fixtures.columns)}")
        return pd.DataFrame()

    fixtures['date_parsed'] = pd.to_datetime(fixtures[date_col], errors='coerce')
    today = pd.Timestamp(datetime.now().date())

    # Matches that haven't been played yet (Score is empty/NaN)
    if score_col:
        mask = fixtures[score_col].isna() | (fixtures[score_col].astype(str).str.strip() == '')
        upcoming = fixtures[(fixtures['date_parsed'] >= today) & mask]
    else:
        upcoming = fixtures[fixtures['date_parsed'] >= today]

    # Limit to next 30 days
    upcoming = upcoming[upcoming['date_parsed'] <= today + timedelta(days=30)]
    result = upcoming[['date_parsed', home_col, away_col]].rename(
        columns={'date_parsed': 'date', home_col: 'home_team', away_col: 'away_team'}
    ).reset_index(drop=True)

    print(f"[Scraper] Fixtures encontrados: {len(result)}")
    return result


def get_upcoming_predictions(df, selector, build_team_last5):
    """
    Scrapes upcoming fixtures and runs the MasterBetSelector on them,
    reusing the logic from the api to build temporally safe features.
    """
    fixtures = fetch_upcoming_fixtures()
    if fixtures.empty:
        return []

    from src.api import compute_elo_map
    
    ref_avg = float(df['referee_avg_cards_history'].mean()) if 'referee_avg_cards_history' in df.columns else 3.5

    upcoming_list = []
    
    def _convert_np(v):
        if isinstance(v, np.integer): return int(v)
        if isinstance(v, np.floating): return float(v)
        if isinstance(v, dict): return {k: _convert_np(val) for k, val in v.items()}
        if isinstance(v, list): return [_convert_np(val) for val in v]
        return v
        
    # We will assume no injuries (0) natively, since it's fully automated
    for i, row in fixtures.iterrows():
        home = str(row['home_team'])
        away = str(row['away_team'])
        match_date = row['date']

        # For future fixtures the historical df is already past, but we keep the
        # cutoff consistent with the backtesting logic.
        elo_map = compute_elo_map(df, cutoff_date=match_date)
        h_form = build_team_last5(home, df, cutoff=match_date)
        a_form = build_team_last5(away, df, cutoff=match_date)

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
            'a_l5_pts':              a_form.get('pts', 0),
            'a_l5_sh':               a_form.get('sh', 0),
            'a_l5_sot':              a_form.get('sot', 0),
            'a_l5_sot_c':            0.0,
            'a_l5_gf':               a_form.get('gf', 0),
            'a_l5_ga':               a_form.get('ga', 0),
            'a_l5_fls':              a_form.get('fls', 0),
            'a_l5_conv':             a_form.get('conv', 0),
            'referee_avg_cards_history': ref_avg,
        }

        preds = selector.get_best_bet(features)
        
        # Take the top bet
        top_bet = _convert_np(preds[0]) if preds else None
        
        upcoming_list.append({
            'id': f"upcoming-{i}",
            'date': match_date.strftime('%Y-%m-%d'),
            'homeTeam': home,
            'awayTeam': away,
            'homeElo': float(features['home_elo']),
            'awayElo': float(features['away_elo']),
            'topPrediction': top_bet
        })

    return upcoming_list
