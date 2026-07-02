import pandas as pd

BASELINE_MATCHES  = "data/raw/2024/matches.csv"
BASELINE_LINEUPS  = "data/raw/2024/lineups.csv"

def validate_schema(df: pd.DataFrame, baseline_path: str, label: str):
    baseline = pd.read_csv(baseline_path)
    missing = set(baseline.columns) - set(df.columns)
    extra   = set(df.columns) - set(baseline.columns)

    if missing:
        print(f"⚠️  [{label}] Columnas faltantes vs 2024/25: {missing}")
    if extra:
        print(f"ℹ️  [{label}] Columnas nuevas no en baseline: {extra}")
    if not missing and not extra:
        print(f"✅ [{label}] Schema idéntico al baseline 2024/25")
