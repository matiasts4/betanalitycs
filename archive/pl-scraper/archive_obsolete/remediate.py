"""
remediate.py — Fix data integrity issues before resuming scraping.

What it does:
1. Deduplicate matches.csv for all seasons (keep last occurrence)
2. For each season:
   - Count actual game_ids present in shot_events.csv on disk
   - Reset match_ids_done.shots in checkpoint to match what's actually on disk
   - Same for lineups and match_events if there's a mismatch
3. Validate 2122 lineup/event data for corruption (very short rows = Cloudflare block)
4. Print a final before/after summary
"""
import json
import glob
import shutil
import pandas as pd
from pathlib import Path
from datetime import datetime

PROCESSED_DIR = Path("data/processed")
STAT_TYPES = ["summary", "keepers", "passing", "defense", "possession", "misc"]

# ────────────────────────────────────────────────────────
# Load all checkpoints into one dict: season → (filepath, data)
# Per-season files take priority over legacy checkpoint.json
# ────────────────────────────────────────────────────────
def load_all_checkpoints():
    season_to_file = {}

    # Per-season files first
    for f in sorted(glob.glob("checkpoint_*.json")):
        with open(f) as fp:
            cp = json.load(fp)
        for season in cp.get("seasons", {}):
            season_to_file[season] = f

    # Legacy checkpoint.json — only for seasons not already found
    legacy_path = Path("checkpoint.json")
    if legacy_path.exists():
        with open(legacy_path) as fp:
            legacy = json.load(fp)
        for season in legacy.get("seasons", {}):
            if season not in season_to_file:
                season_to_file[season] = str(legacy_path)

    # Now load data
    result = {}
    loaded_files = {}
    for season, fpath in season_to_file.items():
        if fpath not in loaded_files:
            with open(fpath) as fp:
                loaded_files[fpath] = json.load(fp)
        result[season] = (fpath, loaded_files[fpath])

    return result, loaded_files


def get_game_ids_on_disk(season_key, filename, id_col="game_id"):
    """Return set of game_ids present in a CSV file."""
    fpath = PROCESSED_DIR / season_key / filename
    if not fpath.exists():
        return set()
    try:
        df = pd.read_csv(fpath, low_memory=False, usecols=lambda c: c == id_col)
        if id_col in df.columns:
            return set(df[id_col].dropna().astype(str).unique())
    except Exception as e:
        print(f"  ⚠ Error reading {fpath}: {e}")
    return set()


def dedup_csv(season_key, filename, key_cols, backup=True):
    """Deduplicate a CSV, keeping last occurrence of each key."""
    fpath = PROCESSED_DIR / season_key / filename
    if not fpath.exists():
        return 0, 0

    df = pd.read_csv(fpath, low_memory=False)
    before = len(df)

    valid_keys = [c for c in key_cols if c in df.columns]
    if valid_keys:
        df = df.drop_duplicates(subset=valid_keys, keep="last")
    else:
        df = df.drop_duplicates(keep="last")

    after = len(df)

    if before != after:
        if backup:
            backup_path = fpath.with_suffix(f".bak_{datetime.now().strftime('%H%M%S')}.csv")
            shutil.copy(fpath, backup_path)
            print(f"    Backup saved: {backup_path.name}")
        df.to_csv(fpath, index=False)
        print(f"    Deduped: {before} → {after} rows")
    else:
        print(f"    OK (no duplicates): {before} rows")

    return before, after


def detect_cloudflare_corrupted_rows(season_key, filename):
    """
    Check lineups/events for rows that might have been written from a Cloudflare
    error page (very few columns or NaN-heavy rows).
    Returns a set of game_ids that appear likely corrupted.
    """
    fpath = PROCESSED_DIR / season_key / filename
    if not fpath.exists():
        return set()

    df = pd.read_csv(fpath, low_memory=False)
    if df.empty:
        return set()

    suspicious_ids = set()
    if "game_id" in df.columns:
        for game_id, group in df.groupby("game_id"):
            null_pct = group.isnull().mean().mean()
            if null_pct > 0.8:  # >80% nulls → likely corrupted
                suspicious_ids.add(str(game_id))
            elif len(group) <= 1:  # Only 1 row for a full lineup? Suspicious
                suspicious_ids.add(str(game_id))

    return suspicious_ids


def remediate_season(season_key, cp_data):
    print(f"\n{'─'*55}")
    print(f"  Remediating Season {season_key}")
    print(f"{'─'*55}")

    season_dir = PROCESSED_DIR / season_key
    if not season_dir.exists():
        print(f"  ⚠ No data directory found for season {season_key}")
        return cp_data, False

    changed = False

    # ─ 1. Dedup matches.csv ─────────────────────────────────
    print(f"  [1] Checking matches.csv for duplicates:")
    before, after = dedup_csv(season_key, "matches.csv", ["game_id"])
    if before != after:
        changed = True

    # ─ 2. Resync shot_events vs checkpoint ────────────────────
    print(f"  [2] Resyncing shot_events.csv vs checkpoint:")
    shots_on_disk = get_game_ids_on_disk(season_key, "shot_events.csv", "game_id")
    cp_shots_done = set(cp_data.get("match_ids_done", {}).get("shots", []))

    if shots_on_disk != cp_shots_done:
        extra_in_cp = cp_shots_done - shots_on_disk
        missing_in_cp = shots_on_disk - cp_shots_done
        if extra_in_cp:
            print(f"    ⚠ Checkpoint claims {len(extra_in_cp)} shots done, but NOT on disk. Removing from checkpoint.")
            cp_data["match_ids_done"]["shots"] = sorted(list(shots_on_disk))
            changed = True
        if missing_in_cp:
            print(f"    ⚠ {len(missing_in_cp)} shots found on disk but not in checkpoint. Adding.")
            cp_data["match_ids_done"]["shots"] = sorted(list(shots_on_disk))
            changed = True
        print(f"    → Shots checkpoint updated: {len(shots_on_disk)} entries")
    else:
        print(f"    OK: {len(shots_on_disk)} shots match checkpoint")

    # ─ 3. Resync lineups vs checkpoint ───────────────────────
    print(f"  [3] Resyncing lineups.csv vs checkpoint:")
    lineups_on_disk = get_game_ids_on_disk(season_key, "lineups.csv", "game_id")
    cp_lineups_done = set(cp_data.get("match_ids_done", {}).get("lineups", []))

    if lineups_on_disk and lineups_on_disk != cp_lineups_done:
        extra = cp_lineups_done - lineups_on_disk
        if extra:
            print(f"    ⚠ {len(extra)} lineups in checkpoint but NOT on disk. Removing.")
            cp_data["match_ids_done"]["lineups"] = sorted(list(lineups_on_disk))
            changed = True
        print(f"    → Lineups checkpoint: {len(lineups_on_disk)}")
    else:
        print(f"    OK: {len(cp_lineups_done)} lineups match")

    # ─ 4. Check for corrupted 2122 match data ─────────────────
    if season_key == "2122":
        print(f"  [4] Checking 2122 for Cloudflare-corrupted rows:")
        corrupt_lu = detect_cloudflare_corrupted_rows(season_key, "lineups.csv")
        corrupt_ev = detect_cloudflare_corrupted_rows(season_key, "match_events.csv")
        all_corrupt = corrupt_lu | corrupt_ev
        if all_corrupt:
            print(f"    🚨 Found {len(all_corrupt)} potentially corrupted game_ids: {sorted(all_corrupt)[:10]}...")
            # Remove from lineups, events CSVs
            for fname in ["lineups.csv", "match_events.csv"]:
                fpath = season_dir / fname
                if fpath.exists():
                    df = pd.read_csv(fpath, low_memory=False)
                    if "game_id" in df.columns:
                        before_r = len(df)
                        df = df[~df["game_id"].astype(str).isin(all_corrupt)]
                        after_r = len(df)
                        df.to_csv(fpath, index=False)
                        print(f"    Removed {before_r - after_r} corrupted rows from {fname}")
            # Remove from checkpoint done lists
            for task in ["lineups", "events", "shots"]:
                old_done = set(cp_data["match_ids_done"].get(task, []))
                new_done = old_done - all_corrupt
                if len(new_done) != len(old_done):
                    cp_data["match_ids_done"][task] = sorted(list(new_done))
                    changed = True
                    print(f"    Removed {len(old_done) - len(new_done)} corrupted ids from checkpoint[{task}]")
        else:
            print(f"    ✅ No corrupted rows detected in 2122 data")

    # ─ 5. Mark player stats mismatch ─────────────────────────
    print(f"  [5] Checking player stats on disk:")
    done_stats = cp_data.get("player_stats_done", [])
    for stat in list(done_stats):
        fpath = season_dir / f"player_stats_{stat}.csv"
        if not fpath.exists():
            print(f"    ⚠ stats_{stat} in checkpoint but file MISSING — removing from done list")
            done_stats.remove(stat)
            changed = True
    cp_data["player_stats_done"] = done_stats
    if not changed:
        print(f"    OK: {done_stats}")

    return cp_data, changed


def save_checkpoint(filepath, full_data):
    full_data["last_updated"] = datetime.now().isoformat()
    with open(filepath, "w") as fp:
        json.dump(full_data, fp, indent=2)
    print(f"\n  💾 Saved: {filepath}")


def main():
    print("=" * 60)
    print("REMEDIATION SCRIPT — PL Scraper Data Fix")
    print("=" * 60)

    season_cp_map, loaded_files = load_all_checkpoints()

    files_to_save = {}  # filepath → full json data

    for season in sorted(season_cp_map.keys()):
        fpath, full_data = season_cp_map[season]
        cp_data = full_data["seasons"][season]

        cp_data, changed = remediate_season(season, cp_data)

        if changed:
            full_data["seasons"][season] = cp_data
            files_to_save[fpath] = full_data

    # Save all modified checkpoint files
    if files_to_save:
        print(f"\n{'='*60}")
        print("Saving modified checkpoints...")
        for fpath, data in files_to_save.items():
            save_checkpoint(fpath, data)
    else:
        print(f"\n{'='*60}")
        print("No checkpoint changes needed.")

    print("\n✅ Remediation complete.")
    print("\n📋 Final state after remediation:")
    print(f"{'Season':<10} {'CP Status':<15} {'Lineups':<12} {'Events':<12} {'Shots':<12} {'Stats done'}")
    print("─" * 80)
    for season in sorted(season_cp_map.keys()):
        _, full_data = season_cp_map[season]
        cp = full_data["seasons"][season]
        total = len(cp.get("match_ids_total", []))
        lu = len(cp.get("match_ids_done", {}).get("lineups", []))
        ev = len(cp.get("match_ids_done", {}).get("events", []))
        sh = len(cp.get("match_ids_done", {}).get("shots", []))
        stats = len(cp.get("player_stats_done", []))
        status = cp.get("status", "?")
        print(f"{season:<10} {status:<15} {lu}/{total:<9} {ev}/{total:<9} {sh}/{total:<9} {stats}/6")


if __name__ == "__main__":
    main()
