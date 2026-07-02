import os
import pandas as pd
from pathlib import Path
from loguru import logger

def _upsert_df_csv(df, season, table_name, conflict_cols):
    if df.empty:
        return
        
    out_dir = Path("data/processed") / str(season)
    out_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = out_dir / f"{table_name}.csv"
    
    df_clean = df.reset_index() if not df.empty else df
    
    # Manejar nombres de columnas que puedan ser tuplas (MultiIndex) de fbref
    if isinstance(df_clean.columns, pd.MultiIndex):
        df_clean.columns = ['_'.join(str(c) for c in col).strip('_') for col in df_clean.columns.values]
    
    if file_path.exists():
        existing_df = pd.read_csv(file_path)
        combined = pd.concat([existing_df, df_clean], ignore_index=True)
        if conflict_cols and all(col in combined.columns for col in conflict_cols):
            combined = combined.drop_duplicates(subset=conflict_cols, keep='last')
        combined.to_csv(file_path, index=False)
    else:
        df_clean.to_csv(file_path, index=False)

def upsert_matches(df, season):
    logger.info(f"Saving matches for season {season}")
    _upsert_df_csv(df, season, "matches", ["home_team", "away_team"])
    
def upsert_lineups(df, season):
    logger.info(f"Saving lineups for season {season}")
    _upsert_df_csv(df, season, "lineups", ["game_id", "team", "player"])

def upsert_events(df, season):
    logger.info(f"Saving events for season {season}")
    _upsert_df_csv(df, season, "match_events", None)

def upsert_shots(df, season):
    logger.info(f"Saving shots for season {season}")
    _upsert_df_csv(df, season, "shot_events", None)

def upsert_player_stats(df, season, stat_type):
    logger.info(f"Saving player stats for {stat_type} in season {season}")
    _upsert_df_csv(df, season, f"player_stats_{stat_type}", ["game_id", "team", "player"])
