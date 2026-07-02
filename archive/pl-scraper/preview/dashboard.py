import sys
from pathlib import Path
from checkpoint.manager import CheckpointManager
import pandas as pd

def show_progress():
    """Vista del estado actual del checkpoint"""
    cp = CheckpointManager()
    summary = cp.progress_summary()

    print("\n" + "═"*65)
    print("  🏴  PREMIER LEAGUE SCRAPER — ESTADO DEL PROGRESO")
    print("═"*65)
    print(f"  {'Season':<10} {'Status':<14} {'Matches':<10} {'Lineups':<12} {'Events':<12} {'Shots':<10}")
    print("─"*65)

    for season, data in sorted(summary.items(), reverse=True):
        icon = "✅" if data["status"] == "done" else ("⏳" if data["status"] == "in_progress" else "⬜")
        print(f"  {icon} {season+'/'+ str(int(season)+1)[-2:]:<8} "
              f"{data['status']:<14} "
              f"{data['total_matches']:<10} "
              f"{data['lineups']:<12} "
              f"{data['events']:<12} "
              f"{data['shots']:<10}")

    print("═"*65 + "\n")

def show_sample(season: int, table: str = "matches", n: int = 5):
    """Preview de N filas de una tabla CSV para una temporada"""
    file_path = Path("data/processed") / str(season) / f"{table}.csv"
    if not file_path.exists():
        print(f"❌ File {file_path} doesn't exist yet.")
        return
        
    df = pd.read_csv(file_path, nrows=n)
    print(f"\n📊 Preview: table={table} | season={season} | rows={len(df)}")
    print(df.to_string(index=False))
    print()

def show_stats(season: int = None):
    """Estadísticas generales en CSV"""
    print("\n" + "═"*45)
    print("  📦  FILAS EN ARCHIVOS CSV")
    print("═"*45)
    
    data_dir = Path("data/processed")
    if not data_dir.exists():
        print("No data directory found.")
        return
        
    seasons = [str(season)] if season else [d.name for d in data_dir.iterdir() if d.is_dir()]
    
    for s in seasons:
        season_dir = data_dir / s
        if not season_dir.exists():
            continue
        print(f"\nSeason {s}:")
        for file in season_dir.glob("*.csv"):
            try:
                count = sum(1 for line in open(file, 'r', encoding='utf-8')) - 1
                print(f"  {file.stem:<25} {count:>10,} rows")
            except Exception as e:
                print(f"  {file.stem:<25} Error reading rows ({e})")
                
    print("═"*45 + "\n")

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "progress"
    if cmd == "progress":
        show_progress()
    elif cmd == "stats":
        season = int(sys.argv[2]) if len(sys.argv) > 2 else None
        show_stats(season)
    elif cmd == "sample":
        table  = sys.argv[2] if len(sys.argv) > 2 else "matches"
        season = int(sys.argv[3]) if len(sys.argv) > 3 else 2023
        show_sample(season, table)
