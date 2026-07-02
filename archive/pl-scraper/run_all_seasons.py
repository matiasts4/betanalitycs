"""
run_all_seasons.py — Runs all seasons sequentially in priority order.

Launches one season at a time to avoid Cloudflare bans.
Can be interrupted (Ctrl+C) and will resume from checkpoint.

Priority order:
  1. 2122 — 296 matches + 6 stats
  2. 2024 — 353 matches + 6 stats
  3. 2022 — 376 matches + 6 stats
  4. 2023 — stats only (4 missing)
  5. 2020 — stats only (5 missing)
  6. 2019 — stats only (5 missing)
  7. 2018 — stats only (5 missing)
  8. 2017 — stats only (5 missing)
"""
from loguru import logger
from pathlib import Path
from pipeline import run_season

# Ordered by priority (most work first, then stats-only)
ORDERED_SEASONS = [
    "2025",  # Current season
    "2122",  # 296 matches + all 6 stats
    "2024",  # 353 matches + all 6 stats
    "2022",  # 376 matches + all 6 stats
    "2023",  # 4 stat types only (summary+keepers done)
    "2020",  # 5 stat types only
    "2019",  # 5 stat types only
    "2018",  # 5 stat types only
    "2017",  # 5 stat types only
]

def main():
    Path("logs").mkdir(exist_ok=True)
    logger.add("logs/run_all.log", rotation="10 MB", level="INFO")
    
    logger.info(f"🚀 Starting ordered scraping for {len(ORDERED_SEASONS)} seasons")
    
    for season in ORDERED_SEASONS:
        logger.info(f"\n{'='*50}")
        logger.info(f"▶ Season: {season}")
        logger.info(f"{'='*50}")
        run_season(season)
    
    logger.success("🏁 All seasons completed!")

if __name__ == "__main__":
    main()
