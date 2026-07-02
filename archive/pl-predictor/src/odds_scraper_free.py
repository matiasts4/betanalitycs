import os
import re
import sys
import time
from datetime import datetime
from bs4 import BeautifulSoup
import numpy as np

# Configurar rutas de importación cruzada de forma dinámica
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PREDICTOR_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
SCRAPER_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "../../pl-scraper"))

if PREDICTOR_ROOT not in sys.path:
    sys.path.append(PREDICTOR_ROOT)
if SCRAPER_ROOT not in sys.path:
    sys.path.append(SCRAPER_ROOT)

from src.db import get_connection, init_db, get_upcoming_matches
from src.odds_client import update_sqlite_with_odds
from scraper.browser_client import BrowserClient

LEAGUE_URLS = {
    "Premier League": "https://www.betexplorer.com/football/england/premier-league/fixtures/",
    "La Liga": "https://www.betexplorer.com/football/spain/laliga/fixtures/"
}

# BetExplorer uses its own team-name conventions. Map common BetExplorer names
# to the canonical names used in the historical dataset / FBref.
BETEXPLORER_TEAM_MAPPING = {
    # Premier League
    "Manchester Utd": "Manchester Utd",
    "Manchester United": "Manchester Utd",
    "Man United": "Manchester Utd",
    "Man Utd": "Manchester Utd",
    "Tottenham": "Tottenham Hotspur",
    "Newcastle": "Newcastle United",
    "West Ham": "West Ham United",
    "Leicester": "Leicester City",
    "Nottm Forest": "Nottingham Forest",
    "Nottingham Forest": "Nottingham Forest",
    "Sheffield Utd": "Sheffield Utd",
    "Wolves": "Wolverhampton Wanderers",
    "Wolverhampton": "Wolverhampton Wanderers",
    "Brighton": "Brighton",
    "Bournemouth": "Bournemouth",
    "Aston Villa": "Aston Villa",
    "Chelsea": "Chelsea",
    "Arsenal": "Arsenal",
    "Liverpool": "Liverpool",
    "Everton": "Everton",
    "Crystal Palace": "Crystal Palace",
    "Fulham": "Fulham",
    "Brentford": "Brentford",
    "Luton": "Luton Town",
    "Burnley": "Burnley",
    "Ipswich": "Ipswich Town",
    "Southampton": "Southampton",
    # La Liga (BetExplorer names are usually close to canonical)
    "Real Madrid": "Real Madrid",
    "Barcelona": "Barcelona",
    "Atletico Madrid": "Atlético Madrid",
    "Athletic Bilbao": "Athletic Club",
    "Villarreal": "Villarreal",
    "Sevilla": "Sevilla",
    "Valencia": "Valencia",
    "Girona": "Girona",
    "Celta Vigo": "Celta Vigo",
    "Osasuna": "Osasuna",
    "Getafe": "Getafe",
    "Las Palmas": "Las Palmas",
    "Mallorca": "Mallorca",
    "Rayo Vallecano": "Rayo Vallecano",
    "Alaves": "Alavés",
    "Leganes": "Leganés",
    "Valladolid": "Valladolid",
    "Espanyol": "Espanyol",
}

def normalize_team_name_betexplorer(team_name):
    """Normalize a BetExplorer team name to the canonical dataset name."""
    cleaned = team_name.strip()
    return BETEXPLORER_TEAM_MAPPING.get(cleaned, cleaned)

def is_float(value):
    try:
        float(value)
        return True
    except ValueError:
        return False

def _find_header_indices(headers, labels):
    """Return column indices for the given header labels (case-insensitive)."""
    idx = {}
    for i, h in enumerate(headers):
        text = h.get_text(strip=True).lower()
        for label in labels:
            if label.lower() in text:
                idx[label] = i
    return idx


def parse_1x2_odds(soup):
    """Parses 1X2 odds table and extracts odds for all available bookmakers."""
    table = soup.find("table", id="sortable-1")
    bookies = {}
    if not table:
        return bookies

    rows = table.find_all("tr")
    if not rows:
        return bookies

    headers = rows[0].find_all(["td", "th"])
    idx = _find_header_indices(headers, ["1", "x", "2"])
    if not all(k in idx for k in ["1", "x", "2"]):
        # Fallback: assume fixed positions 1,2,3 if headers are missing
        idx = {"1": 1, "x": 2, "2": 3}

    for r in rows[1:]:
        cells = [c.get_text(strip=True) for c in r.find_all(["td", "th"])]
        if not cells or len(cells) <= max(idx.values()):
            continue
        bookmaker_name = cells[0].strip()
        if bookmaker_name.lower() in ["bookmaker", "average", "maximum", "add to"]:
            continue

        vals = [cells[idx["1"]], cells[idx["x"]], cells[idx["2"]]]
        if all(is_float(v) for v in vals):
            bookies[bookmaker_name] = {
                'home': float(vals[0]),
                'draw': float(vals[1]),
                'away': float(vals[2])
            }

    # Also try to extract the official market average from the secondary table
    avg_table = soup.find("table", id="aodds-table")
    if avg_table:
        for r in avg_table.find_all("tr"):
            cells = [c.get_text(strip=True) for c in r.find_all(["td", "th"])]
            if cells and len(cells) >= 4:
                name = cells[0].strip()
                if "average" in name.lower():
                    vals = [cells[1], cells[2], cells[3]]
                    if all(is_float(v) for v in vals):
                        bookies['Average'] = {
                            'home': float(vals[0]),
                            'draw': float(vals[1]),
                            'away': float(vals[2])
                        }
    return bookies


def parse_ou_odds(soup):
    """Parses Over/Under 2.5 odds table and extracts odds for all available bookmakers."""
    ou_table = None
    tables = soup.find_all("table")
    for t in tables:
        cls_list = t.get("class", [])
        cls_str = " ".join(cls_list).lower()
        if "best-odds-2.50" in cls_str or "table-collapse-2.50" in cls_str or "best-odds-2.5" in cls_str:
            ou_table = t
            break

    bookies = {}
    if not ou_table:
        return bookies

    rows = ou_table.find_all("tr")
    if not rows:
        return bookies

    headers = rows[0].find_all(["td", "th"])
    idx = _find_header_indices(headers, ["total", "over", "under"])
    if not all(k in idx for k in ["over", "under"]):
        # Fallback: assume total in col 1, over in col 2, under in col 3
        idx = {"total": 1, "over": 2, "under": 3}

    for r in rows[1:]:
        cells = [c.get_text(strip=True) for c in r.find_all(["td", "th"])]
        if not cells or len(cells) <= max(idx.values()):
            continue
        bookmaker_name = cells[0].strip()
        if bookmaker_name.lower() in ["bookmaker", "average", "maximum", "total", "add to"]:
            continue

        # Verify we are on the 2.5 line when a total column exists
        if "total" in idx:
            if not is_float(cells[idx["total"]]) or float(cells[idx["total"]]) != 2.5:
                continue

        over_val = cells[idx["over"]]
        under_val = cells[idx["under"]]
        if is_float(over_val) and is_float(under_val):
            bookies[bookmaker_name] = {
                'over': float(over_val),
                'under': float(under_val)
            }
    return bookies


def parse_btts_odds(soup):
    """Parses BTTS Yes/No odds table and extracts odds for all available bookmakers."""
    # BetExplorer uses a separate table for BTTS; look for Yes/No headers
    table = None
    for t in soup.find_all("table"):
        headers = [h.get_text(strip=True).lower() for h in t.find_all(["th", "td"])]
        if "yes" in headers and "no" in headers:
            table = t
            break

    bookies = {}
    if not table:
        return bookies

    rows = table.find_all("tr")
    if not rows:
        return bookies

    headers = rows[0].find_all(["td", "th"])
    idx = _find_header_indices(headers, ["yes", "no"])
    if not all(k in idx for k in ["yes", "no"]):
        idx = {"yes": 1, "no": 2}

    for r in rows[1:]:
        cells = [c.get_text(strip=True) for c in r.find_all(["td", "th"])]
        if not cells or len(cells) <= max(idx.values()):
            continue
        bookmaker_name = cells[0].strip()
        if bookmaker_name.lower() in ["bookmaker", "average", "maximum", "yes", "no", "add to"]:
            continue

        yes_val = cells[idx["yes"]]
        no_val = cells[idx["no"]]
        if is_float(yes_val) and is_float(no_val):
            bookies[bookmaker_name] = {
                'yes': float(yes_val),
                'no': float(no_val)
            }
    return bookies

def parse_betexplorer_page(html_content):
    """Parses BetExplorer league fixtures page and extracts upcoming match detail links."""
    soup = BeautifulSoup(html_content, 'html.parser')
    table = soup.find('table', {'class': 'table-main'})
    if not table:
        print("[Scraper] No se encontro la tabla 'table-main' en la pagina.")
        return []
        
    matches = []
    
    rows = table.find_all('tr')
    for row in rows:
        cells = row.find_all('td')
        if len(cells) < 6:
            continue
            
        # En la pagina de fixtures, cells[1] contiene los nombres de los equipos unidos por un guion (ej. "Arsenal-Coventry")
        match_cell = cells[1]
        match_link = match_cell.find('a')
        if not match_link:
            continue
            
        match_text = match_link.get_text(strip=True)
        if '-' not in match_text:
            continue
            
        home_raw, away_raw = match_text.split('-', 1)
        home = normalize_team_name_betexplorer(home_raw)
        away = normalize_team_name_betexplorer(away_raw)
        
        href = match_link.get('href', '')
        detail_link = "https://www.betexplorer.com" + href if href.startswith("/") else href
        
        matches.append({
            'home': home,
            'away': away,
            'detail_link': detail_link
        })
            
    return matches

def run_free_odds_scraper(headless=True):
    """Runs the BetExplorer selenium scraper to fetch and save free odds for all markets."""
    init_db()
    
    # Obtener la lista de partidos programados en SQLite para optimizar
    db_matches = get_upcoming_matches()
    # DB team names are already canonical; scraped BetExplorer names are normalized above
    db_pairs = {(dm['homeTeam'], dm['awayTeam']) for dm in db_matches}
    
    if not db_pairs:
        print("[Scraper] No hay partidos futuros guardados en SQLite. No se requiere raspado de cuotas.")
        return True
        
    print(f"[Scraper] Encontrados {len(db_pairs)} partidos pendientes en base de datos.")
    
    print("[Scraper] Iniciando BrowserClient (SeleniumBase UC)...")
    try:
        browser = BrowserClient(headless=headless)
    except Exception as e:
        print(f"[Scraper Error] No se pudo inicializar BrowserClient: {e}")
        return False
        
    total_updated = 0
    
    try:
        for league_name, url in LEAGUE_URLS.items():
            print(f"[Scraper] Navegando a la liga {league_name}: {url}")
            try:
                browser.driver.get(url)
                time.sleep(5)
                
                html_source = browser.driver.page_source
                matches = parse_betexplorer_page(html_source)
                
                print(f"[Scraper] Encontrados {len(matches)} partidos futuros en la web para {league_name}.")
                
                updated = 0
                for m in matches:
                    # OPTIMIZACIÓN: Solo raspar los detalles si el partido esta en SQLite
                    if (m['home'], m['away']) not in db_pairs:
                        continue
                        
                    detail_url = m.get('detail_link')
                    if not detail_url:
                        continue
                        
                    print(f"[Scraper] Navegando a detalles: {m['home']} vs {m['away']} en {detail_url}")
                    try:
                        # 1. Load match details page (default 1X2 odds)
                        browser.driver.get(detail_url)
                        time.sleep(4)
                        soup_1x2 = BeautifulSoup(browser.driver.page_source, 'html.parser')
                        odds_1x2 = parse_1x2_odds(soup_1x2)
                        
                        # 2. Click O/U tab for Over/Under 2.5 goals
                        odds_ou = {}
                        try:
                            from selenium.webdriver.common.by import By
                            ou_link = browser.driver.find_element(By.LINK_TEXT, "O/U")
                            ou_link.click()
                            time.sleep(4)
                            soup_ou = BeautifulSoup(browser.driver.page_source, 'html.parser')
                            parsed_ou = parse_ou_odds(soup_ou)
                            if parsed_ou:
                                odds_ou = parsed_ou
                        except Exception as e_ou:
                            print(f"[Scraper Warning] No se pudo clickear/parsear O/U: {e_ou}")
                            
                        # 3. Click BTTS tab for Yes/No
                        odds_btts = {}
                        try:
                            btts_link = browser.driver.find_element(By.LINK_TEXT, "BTTS")
                            btts_link.click()
                            time.sleep(4)
                            soup_btts = BeautifulSoup(browser.driver.page_source, 'html.parser')
                            parsed_btts = parse_btts_odds(soup_btts)
                            if parsed_btts:
                                odds_btts = parsed_btts
                        except Exception as e_btts:
                            print(f"[Scraper Warning] No se pudo clickear/parsear BTTS: {e_btts}")
                            
                        # Combine all providers odds
                        all_providers = {}
                        
                        for bk, vals in odds_1x2.items():
                            if bk not in all_providers:
                                all_providers[bk] = {}
                            all_providers[bk].update(vals)
                            
                        for bk, vals in odds_ou.items():
                            if bk not in all_providers:
                                all_providers[bk] = {}
                            all_providers[bk]['over25'] = vals.get('over')
                            all_providers[bk]['under25'] = vals.get('under')
                            
                        for bk, vals in odds_btts.items():
                            if bk not in all_providers:
                                all_providers[bk] = {}
                            all_providers[bk]['btts_yes'] = vals.get('yes')
                            all_providers[bk]['btts_no'] = vals.get('no')
                            
                        # Helpers: compute true market average and best available odds
                        def get_reference_bookmaker():
                            """Prefer Bet365 if available, otherwise the official Average row."""
                            for k in all_providers.keys():
                                if 'bet365' in k.lower():
                                    return k
                            if 'Average' in all_providers:
                                return 'Average'
                            return None

                        def get_avg(field, bk_field=None):
                            if bk_field is None:
                                bk_field = field
                            # Use the official Average row when present
                            if 'Average' in all_providers and all_providers['Average'].get(bk_field) is not None:
                                return round(float(all_providers['Average'][bk_field]), 2)
                            # Otherwise compute arithmetic mean over real bookmakers
                            vals = [all_providers[bk].get(bk_field) for bk in all_providers
                                    if all_providers[bk].get(bk_field) is not None and bk not in ['Average', 'Maximum']]
                            return round(float(np.mean(vals)), 2) if vals else None

                        def get_max(field, bk_field=None):
                            if bk_field is None:
                                bk_field = field
                            vals = [all_providers[bk].get(bk_field) for bk in all_providers
                                    if all_providers[bk].get(bk_field) is not None and bk not in ['Average', 'Maximum']]
                            return round(float(np.max(vals)), 2) if vals else None

                        home_avg = get_avg('home')
                        draw_avg = get_avg('draw')
                        away_avg = get_avg('away')
                        over_avg = get_avg('over25')
                        under_avg = get_avg('under25')
                        btts_y_avg = get_avg('btts_yes')
                        btts_n_avg = get_avg('btts_no')

                        home_max = get_max('home')
                        draw_max = get_max('draw')
                        away_max = get_max('away')
                        over_max = get_max('over25')
                        under_max = get_max('under25')
                        btts_y_max = get_max('btts_yes')
                        btts_n_max = get_max('btts_no')

                        ref_provider = get_reference_bookmaker() or 'Market Average'

                        combined_odds = {
                            'home': home_avg,
                            'draw': draw_avg,
                            'away': away_avg,
                            'over25': over_avg,
                            'under25': under_avg,
                            'btts_yes': btts_y_avg,
                            'btts_no': btts_n_avg,
                            'provider': ref_provider,
                            'fetched_at': datetime.utcnow().isoformat() + "Z",
                            'is_simulated': False,

                            # Max odds fields
                            'max_home': home_max,
                            'max_draw': draw_max,
                            'max_away': away_max,
                            'max_over25': over_max,
                            'max_under25': under_max,
                            'max_btts_yes': btts_y_max,
                            'max_btts_no': btts_n_max,

                            # Full list of providers
                            'all_providers': all_providers
                        }
                        
                        if combined_odds['home'] is not None:
                            success = update_sqlite_with_odds(m['home'], m['away'], combined_odds)
                            if success:
                                updated += 1
                                print(f"[Scraper] Cuotas multi-proveedor guardadas para {m['home']} vs {m['away']}")
                        else:
                            print(f"[Scraper Warning] Sin cuotas 1X2 validas para {m['home']} vs {m['away']}")
                            
                    except Exception as e_detail:
                        print(f"[Scraper Error] Error parseando detalles de {m['home']} vs {m['away']}: {e_detail}")
                        
                print(f"[Scraper] {league_name}: {updated} partidos actualizados.")
                total_updated += updated
            except Exception as e:
                print(f"[Scraper Error] Fallo al procesar liga {league_name}: {e}")
    finally:
        print("[Scraper] Cerrando navegador...")
        try:
            browser.driver.quit()
        except:
            pass
            
    print(f"[Scraper] Completado. Total de partidos actualizados con todos los mercados: {total_updated}")
    return True

if __name__ == '__main__':
    run_free_odds_scraper(headless=True)
