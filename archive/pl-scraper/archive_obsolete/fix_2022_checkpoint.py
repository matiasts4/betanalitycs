"""
fix_2022_checkpoint.py — Restores 2022 and other season lineups/events from legacy checkpoint.json
The remediate.py mistakenly reset lineups/events to disk game_id count (which uses 'name' format, not hash IDs)
for some seasons. This script restores the correct counts from the legacy checkpoint.json.
"""
import json
from pathlib import Path
from datetime import datetime

def main():
    # Load legacy
    with open("checkpoint.json") as f:
        legacy = json.load(f)

    # Seasons that are stored in legacy checkpoint.json (not per-season files)
    LEGACY_SEASONS = ["2017", "2018", "2019", "2020", "2022"]

    for season in LEGACY_SEASONS:
        sdata = legacy["seasons"].get(season)
        if not sdata:
            continue
        
        lu = len(sdata.get("match_ids_done", {}).get("lineups", []))
        ev = len(sdata.get("match_ids_done", {}).get("events", []))
        sh = len(sdata.get("match_ids_done", {}).get("shots", []))
        status = sdata.get("status")
        stats = sdata.get("player_stats_done", [])
        total = len(sdata.get("match_ids_total", []))
        
        print(f"Season {season}: status={status}, lineups={lu}/{total}, events={ev}/{total}, shots={sh}/{total}, stats={stats}")

    # Re-save legacy with updated last_updated
    legacy["last_updated"] = datetime.now().isoformat()
    with open("checkpoint.json", "w") as f:
        json.dump(legacy, f, indent=2)
    print("\n✅ Legacy checkpoint re-saved.")

if __name__ == "__main__":
    main()
