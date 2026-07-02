import json
import glob
from pathlib import Path

def print_status():
    files = glob.glob("checkpoint*.json")
    print("=" * 60)
    print(f"{'Temporada':<10} {'Estado':<15} {'Alineaciones':<15} {'Eventos':<12} {'Tiros':<12} {'Stats'}")
    print("─" * 60)
    
    for f in sorted(files):
        try:
            with open(f) as fp:
                data = json.load(fp)
                seasons = data.get("seasons", {})
                for season, sdata in seasons.items():
                    status = sdata.get("status", "unknown")
                    total = len(sdata.get("match_ids_total", []))
                    if total == 0:
                        print(f"{season:<10} {status:<15} {'0/'+str(total):<15} {'0/'+str(total):<12} {'0/'+str(total):<12} 0/6")
                        continue
                    
                    done_lineups = len(sdata.get("match_ids_done", {}).get("lineups", []))
                    done_events = len(sdata.get("match_ids_done", {}).get("events", []))
                    done_shots = len(sdata.get("match_ids_done", {}).get("shots", []))
                    stats = len(sdata.get("player_stats_done", []))
                    
                    print(f"{season:<10} {status:<15} {str(done_lineups)+'/'+str(total):<15} {str(done_events)+'/'+str(total):<12} {str(done_shots)+'/'+str(total):<12} {stats}/6")
        except Exception as e:
            pass
    print("=" * 60)

if __name__ == "__main__":
    print_status()
