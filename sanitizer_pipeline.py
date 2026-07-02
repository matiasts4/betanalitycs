import pandas as pd
import numpy as np
import warnings
from sklearn.impute import KNNImputer
from sklearn.preprocessing import StandardScaler, PowerTransformer

warnings.filterwarnings('ignore')

def run_sanitization():
    """
    Script oficial de procesado y curación de datos (OSSEMN).
    Toma la data maestra cruda (all_match_features_v4_xg.csv) y exprime
    todos sus vicios de acuerdo al checklist formal 'sanitizacion.md'.
    Además, inyecta filtros cuantitativos avanzados (Rachas xG).
    """
    print("🚀 Iniciando Pipeline de Sanitización OSSEMN...")
    
    # 1. Cargar Datos
    raw_path = "archive/pl-predictor/data/historical/all_match_features_v4_xg.csv"
    print(f"[1/6] Cargando datos crudos desde {raw_path}")
    df = pd.read_csv(raw_path)
    
    # 💥 BUGFIX CRÍTICO: Forzar game_id a string para que "0" no se convierta en 0.0 (float)
    if 'game_id' in df.columns:
        df['game_id'] = df['game_id'].astype(str)
        # Limpiar '.0' si pandas lo leyó temporalmente como float en algún momento previo
        df['game_id'] = df['game_id'].apply(lambda x: x[:-2] if str(x).endswith('.0') else str(x))
    
    # 2. Eliminar Varianza Cero (Variables inútiles)
    print("[2/6] Eliminando variables de varianza cero y ruido algorítmico")
    drop_vars = ['league', 'notes', 'match_report'] 
    df.drop(columns=[col for col in drop_vars if col in df.columns], inplace=True)
    
    # MCAR: attendance tenía literalmente 1 solo nulo. Matamos esa fila suelta para no ensuciar promedios.
    if 'attendance' in df.columns:
        df = df.dropna(subset=['attendance']) 
        
    # Formateo datetime y extracción temporal
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
        # Generar dimensionalidad temporal en lugar del crudo
        df['month'] = df['date'].dt.month
        df['day_of_week'] = df['date'].dt.dayofweek
    
    # Acorde a las indicaciones, conservaremos solo "referee_avg_cards_history" para evitar bugs de formato de nombre
    if 'referee' in df.columns:
        df.drop(columns=['referee'], inplace=True)
    
    # Parseo OOR / Ruido
    if 'time' in df.columns:
        df.drop(columns=['time'], inplace=True) 
        
    # 3. Eliminar Leakage (Fuga de Información) y Multicolinealidad
    print("[3/6] Erradicando fugas de información (Leakage) y Multicolinealidad extrema")
    # Todas estadisticas que suceden *post-silbato* e intoxican la predicción
    leakage_cols = ['score', 'home_match_fouls', 'away_match_fouls', 'total_cards']
    df.drop(columns=[col for col in leakage_cols if col in df.columns], inplace=True)
    
    # Reducción Dimensional por correlación brutal: nos quedamos con Bet365 y dropeamos Pinnacle (coefs > 0.85)
    multicollinear_cols = ['PSH', 'PSD', 'PSA']
    df.drop(columns=[col for col in multicollinear_cols if col in df.columns], inplace=True)
    
    # Aislar las variables TARGET (nuestro norte. Nunca se imputan o alteran en asimetría).
    target_cols = ['home_goals', 'away_goals', 'total_goals', 'btts', 'result_1x2']
    targets_df = df[target_cols].copy()
    
    # Dejamos solo los features numéricos que el modelo mirará activamente.
    ignore_for_math = target_cols + ['date', 'game_id', 'home_team', 'away_team', 'venue']
    features_df = df.drop(columns=[c for c in ignore_for_math if c in df.columns])
    
    # 4. Inyección de Filtros Cuantitativos (Rachas xG Moviles)
    # =========================================================
    print("[4/6] Diseñando Características Cuantitativas (EWMA xG)")
    meta_cols = [c for c in ['game_id', 'date', 'home_team', 'away_team', 'venue'] if c in df.columns]
    
    # Reconstruimos temporalmente para usar operaciones de grupo cronológicas
    temp_df = pd.concat([df[meta_cols], targets_df, features_df], axis=1).sort_values('date')
    
    home_perf = temp_df[['date', 'home_team', 'away_team', 'home_xg', 'away_xg']].copy()
    home_perf.columns = ['date', 'team', 'opponent', 'xg_for', 'xg_against']
    away_perf = temp_df[['date', 'away_team', 'home_team', 'away_xg', 'home_xg']].copy()
    away_perf.columns = ['date', 'team', 'opponent', 'xg_for', 'xg_against']
    
    perf = pd.concat([home_perf, away_perf], ignore_index=True)
    perf = perf.sort_values('date').reset_index(drop=True)
    groups = perf.groupby('team')
    
    perf['last5_xg_for'] = groups['xg_for'].apply(lambda x: x.shift(1).ewm(span=5, min_periods=1).mean()).reset_index(level=0, drop=True)
    perf['last5_xg_against'] = groups['xg_against'].apply(lambda x: x.shift(1).ewm(span=5, min_periods=1).mean()).reset_index(level=0, drop=True)
    
    home_feat = perf[['date', 'team', 'last5_xg_for', 'last5_xg_against']].rename(columns={'team': 'home_team', 'last5_xg_for': 'h_l5_xg', 'last5_xg_against': 'h_l5_xga'})
    away_feat = perf[['date', 'team', 'last5_xg_for', 'last5_xg_against']].rename(columns={'team': 'away_team', 'last5_xg_for': 'a_l5_xg', 'last5_xg_against': 'a_l5_xga'})
    
    # Evitar duplicados si hay partidos el mismo día (improbable pero seguro)
    home_feat = home_feat.drop_duplicates(subset=['date', 'home_team'])
    away_feat = away_feat.drop_duplicates(subset=['date', 'away_team'])
    
    temp_df = pd.merge(temp_df, home_feat, on=['date', 'home_team'], how='left')
    temp_df = pd.merge(temp_df, away_feat, on=['date', 'away_team'], how='left')
    
    new_cols = ['h_l5_xg', 'a_l5_xg', 'h_l5_xga', 'a_l5_xga']
    for col in new_cols:
        # Aquí permitimos NaN porque el Pipeline se encargará de imputarlos en train_models.py
        features_df[col] = temp_df[col]
    
    # 5. Reconstrucción Final de la Matrix
    print("[5/6] Ensamblando base final PURE (sin transformaciones numéricas) y exportando csv")
    meta_cols = [c for c in ['game_id', 'date', 'home_team', 'away_team', 'venue'] if c in df.columns]
    
    # Concatenamos de vuelta para no perder los IDs, pero solo features ya pulidos
    final_df = pd.concat([df[meta_cols], targets_df, features_df], axis=1)
    
    export_path = "archive/pl-predictor/data/historical/historical_sanitized_v8.csv"
    final_df.to_csv(export_path, index=False)
    
    print(f"✅ ¡Sanitización Pura Completada con éxito! Dataset base generado en: {export_path}")
    print(f"📉 Dimensión final obtenida: {final_df.shape}")
    print(f"🔍 Atención: Este dataset contiene valores nulos. La imputación y el escalamiento deben hacerse dentro de un scikit-learn Pipeline.")

if __name__ == "__main__":
    run_sanitization()
