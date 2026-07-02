import os
import io
import time
import json
import re
from loguru import logger
import pandas as pd
from lxml import html, etree
import soccerdata.fbref
from soccerdata._common import BaseRequestsReader
import soccerdata as sd
from config import LEAGUE
from dotenv import load_dotenv
from scraper.browser_client import BrowserClient

load_dotenv()

# MONKEY PATCH: Override soccerdata's download method to use our undetected-chromedriver
def _download_and_save_with_browser(
    self,
    url: str,
    filepath=None,
    var=None,
):
    """Download file at url to filepath using a real browser to bypass Cloudflare. Overwrites if filepath exists."""
    for i in range(5):
        try:
            # Use the injected browser_client or the legacy global one
            if hasattr(self, 'browser_client') and self.browser_client:
                client = self.browser_client
            else:
                from scraper.browser_client import BrowserClient
                # Fallback to a default client if none injected (for backward compatibility)
                if not hasattr(self, '_default_client'):
                    self._default_client = BrowserClient()
                client = self._default_client
            
            logger.debug(f"Página con navegador: {url}")
            payload = client.get_html(url)
            
            if var is not None:
                if isinstance(var, str):
                    var = [var]
                var_names = "|".join(var)
                template_understat = rb"(%b)+[\s\t]*=[\s\t]*JSON\.parse\('(.*)'\)"
                pattern_understat = template_understat % bytes(var_names, encoding="utf-8")
                results = re.findall(pattern_understat, payload)
                data = {
                    key.decode("unicode_escape"): json.loads(value.decode("unicode_escape"))
                    for key, value in results
                }
                payload = json.dumps(data).encode("utf-8")
            
            if not self.no_store and filepath is not None:
                # Create parent dirs if they don't exist
                filepath.parent.mkdir(parents=True, exist_ok=True)
                with filepath.open(mode="wb") as fh:
                    fh.write(payload)
            return io.BytesIO(payload)
            
        except Exception as e:
            logger.exception(
                "Error while scraping %s con navegador. Retrying... (attempt %d of 5). Detalles: %s",
                url,
                i + 1,
                e
            )
            time.sleep(5)
            continue

    raise ConnectionError(f"Could not download {url} incluso usando el navegador undetected-chromedriver.")

# Apply the patch to the base class used by FBref
BaseRequestsReader._download_and_save = _download_and_save_with_browser

# MONKEY PATCH 2: Override _parse_table to prevent NoneType errors on Selenium HTML
def _patched_parse_table(html_table: html.HtmlElement) -> pd.DataFrame:
    from io import StringIO
    # remove icons (use .// to search inside the table only, not the whole doc)
    for elem in html_table.xpath(".//span[contains(@class, 'f-i')]"):
        parent = elem.getparent()
        if parent is not None:
            etree.strip_elements(parent, "span", with_tail=False)
    # remove sep rows
    for elem in html_table.xpath(".//tbody/tr[contains(@class, 'spacer')]"):
        parent = elem.getparent()
        if parent is not None:
            parent.remove(elem)
    # remove thead rows in the table body
    for elem in html_table.xpath(".//tbody/tr[contains(@class, 'thead')]"):
        parent = elem.getparent()
        if parent is not None:
            parent.remove(elem)
    # parse HTML to dataframe
    try:
        html_str = html.tostring(html_table, encoding="unicode")
        (df_table,) = pd.read_html(StringIO(html_str), flavor="lxml")
        return df_table.convert_dtypes()
    except Exception as e:
        logger.warning(f"Error parsing table with pandas: {e}")
        return pd.DataFrame()

soccerdata.fbref._parse_table = _patched_parse_table

# MONKEY PATCH 3: Override read_schedule to bypass broken read_leagues/read_seasons
# FBref changed their HTML structure and soccerdata's _translate_league fails with KeyError: 'league'
def _patched_read_schedule(self, force_cache=False):
    """Direct schedule parser that bypasses soccerdata's broken read_leagues pipeline."""
    if hasattr(self, "_cached_schedule") and not force_cache:
        return self._cached_schedule.copy()
        
    from io import StringIO

    # Build the FBref schedule URL
    # self.seasons[0] is the raw season identifier (e.g., "2025" or 2025)
    # FBref uses format like "2025-2026" in URLs
    season_raw = self.seasons[0]
    try:
        s_int = int(season_raw)
        season_code = f"{s_int}-{s_int + 1}"
    except (ValueError, TypeError):
        season_code = str(season_raw)
    url = f"https://fbref.com/en/comps/9/{season_code}/schedule/{season_code}-Premier-League-Scores-and-Fixtures"
    
    logger.info(f"[PATCHED] Descargando schedule desde: {url}")
    
    # Download using the browser-patched method
    raw_bytes = self._download_and_save(url)
    raw_html = raw_bytes.read()
    
    # Parse HTML
    doc = html.fromstring(raw_html)
    
    # Find schedule table
    tables = doc.xpath("//table[contains(@id, 'sched')]")
    if not tables:
        tables = doc.xpath("//table[contains(@class, 'stats_table')]")
    
    schedule_table = None
    for t in tables:
        caption = t.xpath(".//caption/text()")
        if caption and ("scores" in caption[0].lower() or "fixtures" in caption[0].lower()):
            schedule_table = t
            break
    if schedule_table is None and tables:
        schedule_table = tables[0]
    
    if schedule_table is None:
        raise ValueError("No se encontro tabla de schedule en FBref")
    
    # Parse table to DataFrame
    table_html_str = html.tostring(schedule_table, encoding="unicode")
    dfs = pd.read_html(StringIO(table_html_str))
    df = dfs[0]
    
    # Clean: remove repeated header rows and spacer rows
    if "Wk" in df.columns:
        df = df[df["Wk"].notna() & (df["Wk"] != "Wk")].copy()
    
    # Extract game_ids from match report links
    rows = schedule_table.xpath(
        ".//tbody/tr[not(contains(@class, 'spacer')) and not(contains(@class, 'thead'))]"
    )
    game_ids = []
    for row in rows:
        report_link = row.xpath(".//td[@data-stat='match_report']//a/@href")
        if report_link:
            match = re.search(r'/matches/([a-f0-9]+)/', report_link[0])
            game_ids.append(match.group(1) if match else None)
        else:
            game_ids.append(None)
    
    # Align game_ids with cleaned DataFrame
    if len(game_ids) == len(df):
        df["game_id"] = game_ids
    else:
        logger.warning(f"game_ids ({len(game_ids)}) != rows ({len(df)}), attempting alignment by position")
        # Try to align by filtering out spacer/thead rows from our count
        df["game_id"] = (game_ids[:len(df)] if len(game_ids) >= len(df) 
                         else game_ids + [None] * (len(df) - len(game_ids)))
    
    # Rename columns to match soccerdata convention
    col_map = {
        "Home": "home_team", "Away": "away_team", "Score": "score",
        "Date": "date", "Time": "time", "Wk": "week", "Day": "day",
        "Venue": "venue", "Referee": "referee", "Attendance": "attendance",
        "Match Report": "match_report", "Notes": "notes"
    }
    df = df.rename(columns={k: v for k, v in col_map.items() if k in df.columns})
    
    df["league"] = "ENG-Premier League"
    df["season"] = self.seasons[0]
    
    # Fix types and index to match soccerdata format
    df["date"] = pd.to_datetime(df["date"]).ffill()
    
    def _make_game_id(row):
        if pd.isna(row["date"]):
            return f"TBD {row['home_team']}-{row['away_team']}"
        return f"{row['date'].strftime('%Y-%m-%d')} {row['home_team']}-{row['away_team']}"
        
    df["game"] = df.apply(_make_game_id, axis=1)
    df = df.set_index(["league", "season", "game"]).sort_index()
    
    # For game_id to work like soccerdata, it needs to be available
    logger.success(f"[PATCHED] Schedule: {len(df)} partidos, {df['game_id'].notna().sum()} con game_id")
    
    self._cached_schedule = df
    return df

# Apply patch
sd.FBref.read_schedule = _patched_read_schedule

def get_fbref(season: int, browser_client: BrowserClient = None):
    # We don't necessarily need injecting these anymore since the real browser handles state,
    # but we can leave it mapping just in case sd tries to use it somewhere else.
    cookie = os.getenv("STATHEAD_COOKIE")
    ua = os.getenv("STATHEAD_USER_AGENT")
    
    if cookie:
        soccerdata.fbref.FBREF_HEADERS["Cookie"] = cookie
    if ua:
        soccerdata.fbref.FBREF_HEADERS["User-Agent"] = ua

    fbref_obj = sd.FBref(
        leagues=LEAGUE,
        seasons=[season]
    )
    # Inject the specific browser client into the object
    fbref_obj.browser_client = browser_client
    return fbref_obj
