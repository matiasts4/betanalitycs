import json
from pathlib import Path

def migrate_legacy_checkpoints():
    print("Migrating legacy checkpoints...")
    if not Path("checkpoint.json").exists():
        print("No legacy checkpoint found.")
        return
        
    with open("checkpoint.json") as f:
        legacy = json.load(f)
        
    for season, data in legacy.get("seasons", {}).items():
        out_file = Path(f"checkpoint_{season}.json")
        if not out_file.exists():
            print(f"Migrating season {season} to {out_file}...")
            # Create a single-season checkpoint file
            new_cp = {
                "version": legacy.get("version", 1),
                "last_updated": legacy.get("last_updated"),
                "seasons": {
                    season: data
                }
            }
            with open(out_file, "w") as out_f:
                json.dump(new_cp, out_f, indent=2)
            print(f"  ✅ Created {out_file}")
        else:
            print(f"Skipping {season}, file already exists.")

if __name__ == "__main__":
    migrate_legacy_checkpoints()
