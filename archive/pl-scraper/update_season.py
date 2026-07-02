"""
update_season.py — Actualiza la temporada 2025/26 completamente.

1. Resetea el checkpoint del schedule para forzar re-descarga
2. Descarga el schedule actualizado de FBref (con scores y game_ids nuevos)
3. Descarga lineups, events y shots de los partidos nuevos
4. Descarga player stats si faltan
5. Actualiza el dataset principal v4_xg con todos los datos nuevos

Uso:
    python update_season.py [--season 2025] [--headless]
"""
import json
import sys
import os
import argparse
import time
import re
import pandas as pd
import numpy as np
from pathlib import Path
from loguru import logger

os.environ["PYTHONIOENCODING"] = "utf-8"
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Setup
Path("logs").mkdir(exist_ok=True)
logger.add("logs/update_season.log", rotation="10 MB", level="INFO")

parser = argparse.ArgumentParser()
parser.add_argument("--season", default="2025", help="Season to update (default: 2025)")
parser.add_argument("--headless", action="store_true", help="Run browser in headless mode")
parser.add_argument("--skip-details", action="store_true", help="Skip lineups/events/shots (only update schedule)")
args = parser.parse_args()

SEASON = args.season
SEASON_INT = int(SEASON)

# Season code for file naming (e.g., 2025 -> 2526)
if SEASON_INT >= 2000:
    SEASON_CODE = int(f"{SEASON_INT % 100}{(SEASON_INT + 1) % 100}")
else:
    SEASON_CODE = SEASON_INT

PREDICTOR_V4 = Path("..") / "pl-predictor" / "data" / "historical" / "all_match_features_v4_xg.csv"

print("=" * 65)
print(f"  ACTUALIZADOR COMPLETO - PL Temporada {SEASON}/{SEASON_INT + 1}")
print("=" * 65)

# ── Step 1: Reset checkpoint ──
CP_FILE = Path(f"checkpoint_{SEASON}.json")
if CP_FILE.exists():
    cp_data = json.load(open(CP_FILE))
    s = cp_data.get("seasons", {}).get(SEASON, {})
    old_ids = len(s.get("match_ids_total", []))
    old_lineups = len(s.get("match_ids_done", {}).get("lineups", []))
    print(f"\n[1/5] Checkpoint actual: {old_ids} match IDs, lineups={old_lineups}")
    
    # Reset schedule to force re-download, but keep done lists
    s["schedule_done"] = False
    s["status"] = "in_progress"
    cp_data["seasons"][SEASON] = s
    
    with open(CP_FILE, "w") as f:
        json.dump(cp_data, f, indent=2)
    print(f"  [OK] Schedule reset para forzar re-descarga")
else:
    print(f"\n[1/5] No hay checkpoint previo, se creara uno nuevo")

# ── Step 2: Run the pipeline ──
print(f"\n[2/5] Iniciando navegador y scraper...")
print("  Se abrira una ventana de Chrome.")
print("  Si aparece CAPTCHA de Cloudflare, resuelvelo manualmente.\n")

from scraper.browser_client import BrowserClient
browser = BrowserClient(headless=args.headless)

from scraper.fbref_client import get_fbref
fbref = get_fbref(SEASON, browser_client=browser)

# Phase 1: Schedule
print("[3/5] Descargando schedule actualizado...")
try:
    schedule = fbref.read_schedule()
    print(f"  [OK] Schedule: {len(schedule)} partidos")
    
    # Extract game_ids
    if 'game_id' in schedule.columns:
        all_ids = schedule['game_id'].dropna().unique().tolist()
    else:
        all_ids = []
    
    match_ids = [str(m) for m in all_ids if m and str(m) != 'nan']
    print(f"  Game IDs con resultado: {len(match_ids)}")
    
    # Save updated matches.csv
    from storage.db import upsert_matches
    upsert_matches(schedule, SEASON)
    print(f"  [OK] matches.csv actualizado")
    
    # Update checkpoint with ALL match IDs (including new ones)
    from checkpoint.manager import CheckpointManager
    cp = CheckpointManager(season=SEASON)
    cp.init_season(SEASON)
    
    # Merge new match_ids with existing ones
    existing_ids = set(cp.state["seasons"][SEASON].get("match_ids_total", []))
    new_ids = set(match_ids) - existing_ids
    if new_ids:
        print(f"  [OK] {len(new_ids)} match IDs NUEVOS encontrados")
    
    cp.mark_schedule_done(SEASON, match_ids)
    
except Exception as e:
    print(f"  [ERROR] Schedule: {e}")
    import traceback
    traceback.print_exc()
    browser.close()
    sys.exit(1)

# Phase 2: Lineups, Events, Shots for new matches
if not args.skip_details:
    print(f"\n[4/5] Descargando detalles de partidos nuevos (lineups/events/shots)...")
    
    from config import RATE_LIMIT_SECONDS
    
    pending_lineups = set(cp.get_pending_matches(SEASON, "lineups"))
    pending_events = set(cp.get_pending_matches(SEASON, "events"))
    pending_shots = set(cp.get_pending_matches(SEASON, "shots"))
    
    all_pending = pending_lineups | pending_events | pending_shots
    print(f"  Partidos pendientes: {len(all_pending)} (lineups={len(pending_lineups)}, events={len(pending_events)}, shots={len(pending_shots)})")
    
    from storage.db import upsert_lineups, upsert_events, upsert_shots
    
    completed = 0
    total_pending = len(all_pending)
    for match_id in sorted(list(all_pending)):
        completed += 1
        print(f"  [{completed}/{total_pending}] Partido {match_id}...", end="", flush=True)
        
        # Lineups
        if match_id in pending_lineups:
            try:
                df = fbref.read_lineup(match_id=[match_id])
                upsert_lineups(df, SEASON)
                cp.mark_match_done(SEASON, "lineups", match_id)
            except Exception as e:
                logger.warning(f"  Lineup {match_id}: {e}")
        
        # Events
        if match_id in pending_events:
            try:
                df = fbref.read_events(match_id=[match_id])
                upsert_events(df, SEASON)
                cp.mark_match_done(SEASON, "events", match_id)
            except Exception as e:
                logger.warning(f"  Event {match_id}: {e}")
        
        # Shots
        if match_id in pending_shots:
            try:
                df = fbref.read_shot_events(match_id=[match_id])
                upsert_shots(df, SEASON)
                cp.mark_match_done(SEASON, "shots", match_id)
            except Exception as e:
                logger.warning(f"  Shot {match_id}: {e}")
        
        print(" OK")
        time.sleep(RATE_LIMIT_SECONDS)
    
    if total_pending == 0:
        print("  [OK] Todos los detalles ya descargados")
else:
    print(f"\n[4/5] Saltando detalles (--skip-details)")

# Phase 3: Player stats (DISABLED by default — soccerdata's read_player_match_stats is broken)
print(f"\n[5/5] Player stats: SALTADO (soccerdata incompatible con FBref actual)")
print("  Para player stats, usar el pipeline original con soccerdata actualizado.")

browser.close()

# ── Step 6: Update v4_xg dataset ──
print(f"\n{'=' * 65}")
print(f"  ACTUALIZANDO DATASET PRINCIPAL v4_xg")
print(f"{'=' * 65}")

if PREDICTOR_V4.exists():
    v4 = pd.read_csv(PREDICTOR_V4)
    matches_updated = pd.read_csv(f"data/processed/{SEASON}/matches.csv")
    
    v4_updates = 0
    for _, row in matches_updated.iterrows():
        if pd.isna(row.get("score")) or str(row.get("score")).strip() in ("", "nan", "NaN"):
            continue
        
        home = str(row.get("home_team", "")).strip()
        away = str(row.get("away_team", "")).strip()
        date = str(row.get("date", "")).strip()
        score = str(row["score"]).strip()
        game_id = str(row.get("game_id", ""))
        
        # Parse score
        parts = re.split(r'[\u2013\-]', score)
        if len(parts) != 2:
            continue
        try:
            hg = int(parts[0].strip())
            ag = int(parts[1].strip())
        except ValueError:
            continue
        
        # Find matching row in v4 by home+away in season, with game_id='0' OR matching game_id
        mask = (
            (v4["season"] == SEASON_CODE) &
            (v4["home_team"].str.strip() == home) &
            (v4["away_team"].str.strip() == away)
        )
        hits = v4[mask]
        
        # Prefer the one with game_id='0' (fixture to update)
        fixture_hits = hits[hits["game_id"].astype(str) == "0"]
        if len(fixture_hits) > 0:
            idx = fixture_hits.index[0]
        elif len(hits) > 0:
            # Already has a game_id, check if score needs update
            idx = hits.index[0]
            if str(v4.loc[idx, "score"]).strip() == score:
                continue  # Already up to date
        else:
            continue
        
        # Update
        v4.loc[idx, "date"] = date
        v4.loc[idx, "score"] = score
        v4.loc[idx, "game_id"] = game_id if game_id and game_id != "nan" else v4.loc[idx, "game_id"]
        v4.loc[idx, "home_goals"] = hg
        v4.loc[idx, "away_goals"] = ag
        if "total_goals" in v4.columns:
            v4.loc[idx, "total_goals"] = hg + ag
        if "btts" in v4.columns:
            v4.loc[idx, "btts"] = 1 if (hg > 0 and ag > 0) else 0
        if "result_1x2" in v4.columns:
            v4.loc[idx, "result_1x2"] = 2 if hg > ag else (1 if hg == ag else 0)
        
        v4_updates += 1
    
    v4 = v4.sort_values("date").reset_index(drop=True)
    v4.to_csv(PREDICTOR_V4, index=False)
    print(f"  [OK] {v4_updates} partidos actualizados en v4_xg")
    
    # Final summary
    s26 = v4[v4["season"] == SEASON_CODE]
    played = s26[s26["game_id"].astype(str) != "0"]
    pend = s26[s26["game_id"].astype(str) == "0"]
    print(f"  Temporada {SEASON_CODE}: {len(played)} jugados, {len(pend)} pendientes")
    if len(played) > 0:
        print(f"  Ultimo partido: {played['date'].max()}")

print(f"\n[DONE] Actualizacion completada.")
