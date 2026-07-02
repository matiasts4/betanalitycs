import os
import requests
import pandas as pd
import io

# Directorios y rutas
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PREDICTOR_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
HISTORICAL_DIR = os.path.join(PREDICTOR_ROOT, "data", "historical")

PATH_V9 = os.path.join(HISTORICAL_DIR, "historical_sanitized_v9.csv")
PATH_V11 = os.path.join(HISTORICAL_DIR, "historical_sanitized_v11.csv")

SEASONS = ["1718", "1819", "1920", "2021", "2122", "2223", "2324", "2425", "2526"]

TEAM_MAPPING_FD_TO_FBREF = {
    'Cardiff': 'Cardiff City',
    'Huddersfield': 'Huddersfield Town',
    'Ipswich': 'Ipswich Town',
    'Leeds': 'Leeds United',
    'Leicester': 'Leicester City',
    'Luton': 'Luton Town',
    'Man City': 'Manchester City',
    'Man United': 'Manchester Utd',
    'Newcastle': 'Newcastle United',
    'Norwich': 'Norwich City',
    "Nott'm Forest": 'Nottingham Forest',
    'Stoke': 'Stoke City',
    'Swansea': 'Swansea City',
    'Tottenham': 'Tottenham Hotspur',
    'West Ham': 'West Ham United',
}

def normalize_fd_team(name):
    if not isinstance(name, str):
        return name
    name = name.strip()
    return TEAM_MAPPING_FD_TO_FBREF.get(name, name)

def run_merge():
    print("Iniciando descarga y fusion de cuotas promedio y maximas historicas...")
    
    if not os.path.exists(PATH_V9):
        print(f"[Error] No se encontro el dataset origen: {PATH_V9}")
        return False
        
    df_fbref = pd.read_csv(PATH_V9)
    df_fbref['season_str'] = df_fbref['season'].astype(str)
    
    all_fd_matches = []
    
    for season in SEASONS:
        url = f"https://www.football-data.co.uk/mmz4281/{season}/E0.csv"
        print(f"Descargando {season} de {url}...")
        try:
            r = requests.get(url, timeout=15)
            if r.status_code != 200:
                print(f"[Warning] No se pudo descargar la temporada {season}. Codigo: {r.status_code}")
                continue
                
            df_fd = pd.read_csv(io.StringIO(r.text))
            df_fd.columns = [c.strip() for c in df_fd.columns]
            
            # Mapeo según la temporada
            if season in ["1718", "1819"]:
                # Betbrain era
                max_h, max_d, max_a = 'BbMxH', 'BbMxD', 'BbMxA'
                over_avg, under_avg = 'BbAv>2.5', 'BbAv<2.5'
                over_max, under_max = 'BbMx>2.5', 'BbMx<2.5'
            else:
                # Market era
                max_h, max_d, max_a = 'MaxH', 'MaxD', 'MaxA'
                over_avg, under_avg = 'Avg>2.5', 'Avg<2.5'
                over_max, under_max = 'Max>2.5', 'Max<2.5'
                
            # Verificar columnas mínimas requeridas
            required_cols = ['HomeTeam', 'AwayTeam', 'B365H', 'B365D', 'B365A', max_h, max_d, max_a]
            missing_req = [c for c in required_cols if c not in df_fd.columns]
            if missing_req:
                print(f"[Warning] Columnas obligatorias {missing_req} ausentes en la temporada {season}. Saltando.")
                continue
                
            # Configurar columnas a extraer
            cols_to_extract = {
                'HomeTeam': 'home_team_raw',
                'AwayTeam': 'away_team_raw',
                'B365H': 'B365H_new',
                'B365D': 'B365D_new',
                'B365A': 'B365A_new',
                max_h: 'Max_Home',
                max_d: 'Max_Draw',
                max_a: 'Max_Away'
            }
            
            if over_avg in df_fd.columns:
                cols_to_extract[over_avg] = 'Avg_Over2.5'
            if under_avg in df_fd.columns:
                cols_to_extract[under_avg] = 'Avg_Under2.5'
                
            if over_max in df_fd.columns:
                cols_to_extract[over_max] = 'Max_Over2.5'
            if under_max in df_fd.columns:
                cols_to_extract[under_max] = 'Max_Under2.5'
                
            df_season = df_fd[list(cols_to_extract.keys())].rename(columns=cols_to_extract).copy()
            
            # Normalizar nombres de equipos
            df_season['home_team_fd'] = df_season['home_team_raw'].apply(normalize_fd_team)
            df_season['away_team_fd'] = df_season['away_team_raw'].apply(normalize_fd_team)
            df_season['season_str'] = season
            
            all_fd_matches.append(df_season)
            print(f"[OK] Temporada {season} procesada con {len(df_season)} partidos.")
            
        except Exception as e:
            print(f"[Error] Fallo al procesar la temporada {season}: {e}")
            
    if not all_fd_matches:
        print("[Error] No se pudo obtener informacion de ninguna temporada.")
        return False
        
    df_all_fd = pd.concat(all_fd_matches, ignore_index=True)
    
    # Left Merge
    print("\nFusionando datasets...")
    df_merged = pd.merge(
        df_fbref,
        df_all_fd[['season_str', 'home_team_fd', 'away_team_fd', 
                   'B365H_new', 'B365D_new', 'B365A_new', 
                   'Max_Home', 'Max_Draw', 'Max_Away', 
                   'Avg_Over2.5', 'Avg_Under2.5', 
                   'Max_Over2.5', 'Max_Under2.5']],
        left_on=['season_str', 'home_team', 'away_team'],
        right_on=['season_str', 'home_team_fd', 'away_team_fd'],
        how='left'
    )
    
    # Sobrescribir cuotas promedio
    df_merged['B365H'] = df_merged['B365H_new'].fillna(df_merged['B365H'])
    df_merged['B365D'] = df_merged['B365D_new'].fillna(df_merged['B365D'])
    df_merged['B365A'] = df_merged['B365A_new'].fillna(df_merged['B365A'])
    
    # Eliminar columnas de control/auxiliares
    cols_to_drop = ['season_str', 'home_team_fd', 'away_team_fd', 'B365H_new', 'B365D_new', 'B365A_new']
    df_merged.drop(columns=cols_to_drop, inplace=True, errors='ignore')
    
    # Coberturas
    total_rows = len(df_merged)
    print(f"\nEstadisticas de Cobertura en el Dataset Fusionado (v11):")
    print(f"  Total Partidos: {total_rows}")
    print(f"  Avg Over 2.5: {df_merged['Avg_Over2.5'].notna().sum()} ({df_merged['Avg_Over2.5'].notna().sum()/total_rows*100:.1f}%)")
    print(f"  Avg Under 2.5: {df_merged['Avg_Under2.5'].notna().sum()} ({df_merged['Avg_Under2.5'].notna().sum()/total_rows*100:.1f}%)")
    print(f"  Max Home Odds: {df_merged['Max_Home'].notna().sum()} ({df_merged['Max_Home'].notna().sum()/total_rows*100:.1f}%)")
    print(f"  Max Over 2.5: {df_merged['Max_Over2.5'].notna().sum()} ({df_merged['Max_Over2.5'].notna().sum()/total_rows*100:.1f}%)")
    
    # Guardar en historical_sanitized_v11.csv
    print(f"\nGuardando dataset actualizado en: {PATH_V11}")
    df_merged.to_csv(PATH_V11, index=False)
    print("[Exito] Dataset historical_sanitized_v11.csv creado correctamente!")
    return True

if __name__ == '__main__':
    run_merge()
