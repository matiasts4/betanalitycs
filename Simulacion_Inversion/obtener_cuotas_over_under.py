import pandas as pd
import numpy as np
import os
import sys
import urllib.request
import ssl

# Configurar rutas para importar desde archive/pl-predictor
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'archive', 'pl-predictor')))
from src.config import FEATURES_PATH

# Ignorar verificación de SSL en caso de problemas con certificados
ssl_context = ssl._create_unverified_context()

TEAM_MAPPING = {
    'Man United': 'Manchester Utd',
    'Man City': 'Manchester City',
    'Tottenham': 'Tottenham Hotspur',
    'Newcastle': 'Newcastle United',
    'West Ham': 'West Ham United',
    'Leicester': 'Leicester City',
    "Nott'm Forest": 'Nottingham Forest',
    'Cardiff': 'Cardiff City',
    'Huddersfield': 'Huddersfield Town',
    'Ipswich': 'Ipswich Town',
    'Leeds': 'Leeds United',
    'Luton': 'Luton Town',
    'Norwich': 'Norwich City',
    'Stoke': 'Stoke City',
    'Swansea': 'Swansea City',
    'West Brom': 'West Brom',
}

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Descargar cuotas de cada temporada
    seasons = ['1718', '1819', '1920', '2021', '2122', '2223', '2324', '2425']
    all_odds_dfs = []
    
    print("Descargando cuotas históricas desde Football-Data.co.uk...")
    for season in seasons:
        url = f"https://www.football-data.co.uk/mmz4281/{season}/E0.csv"
        print(f"  > Descargando Temporada {season}...")
        try:
            # Descargar archivo temporalmente usando urlopen
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, context=ssl_context) as response:
                csv_data = response.read()
            
            temp_path = os.path.join(current_dir, f"temp_{season}.csv")
            with open(temp_path, 'wb') as f:
                f.write(csv_data)
                
            # Leer CSV (Football-data usa codificación latin1 a veces)
            df_season = pd.read_csv(temp_path, encoding='unicode_escape')
            
            # Borrar archivo temporal
            try:
                os.remove(temp_path)
            except Exception:
                pass
            
            # Limpiar columnas
            df_season = df_season.dropna(subset=['HomeTeam', 'AwayTeam'])
            
            # Mapear nombres de equipos
            df_season['home_team_mapped'] = df_season['HomeTeam'].map(lambda x: TEAM_MAPPING.get(x.strip(), x.strip()))
            df_season['away_team_mapped'] = df_season['AwayTeam'].map(lambda x: TEAM_MAPPING.get(x.strip(), x.strip()))
            df_season['season'] = int(season)
            
            # Verificar presencia de las columnas de cuotas Over/Under
            # Las columnas de cuotas Over/Under en Football-Data.co.uk suelen ser 'B365>2.5' y 'B365<2.5'
            ou_cols = ['B365>2.5', 'B365<2.5']
            missing_cols = [c for c in ou_cols if c not in df_season.columns]
            if len(missing_cols) > 0:
                print(f"    [Advertencia] Columnas de Over/Under ausentes en temporada {season}: {missing_cols}")
                # Buscar alternativas BetBrain o similares si es necesario
                # Para estas temporadas, Bet365 está siempre presente, pero por seguridad:
                if 'BbAv>2.5' in df_season.columns:
                    df_season['B365>2.5'] = df_season['BbAv>2.5']
                if 'BbAv<2.5' in df_season.columns:
                    df_season['B365<2.5'] = df_season['BbAv<2.5']
            
            # Seleccionar sólo columnas de interés
            cols_to_keep = ['season', 'home_team_mapped', 'away_team_mapped', 'B365>2.5', 'B365<2.5']
            all_odds_dfs.append(df_season[cols_to_keep])
            print(f"    [OK] Cargados {len(df_season)} partidos con cuotas.")
        except Exception as e:
            print(f"    [ERROR] Error al descargar temporada {season}: {e}")
            
    # Concatenar todos los DataFrames de cuotas
    odds_df = pd.concat(all_odds_dfs, ignore_index=True)
    
    # Cargar nuestro dataset sanitizado actual
    print(f"\nCargando dataset sanitizado actual desde: {FEATURES_PATH}")
    master_df = pd.read_csv(FEATURES_PATH)
    master_df['season'] = master_df['season'].astype(int)
    
    print(f"Cantidad inicial de partidos en el dataset: {len(master_df)}")
    
    # Hacer el cruce (merge) por 'season', 'home_team' y 'away_team'
    merged_df = pd.merge(
        master_df,
        odds_df,
        left_on=['season', 'home_team', 'away_team'],
        right_on=['season', 'home_team_mapped', 'away_team_mapped'],
        how='left'
    )
    
    # Limpiar columnas temporales del merge
    merged_df = merged_df.drop(columns=['home_team_mapped', 'away_team_mapped'])
    
    # Verificar cuántos partidos obtuvieron cuotas Over/Under exitosamente
    matched_count = merged_df['B365>2.5'].notna().sum()
    print(f"[OK] Fusión completada. Partidos con cuotas Over/Under acopladas: {matched_count} de {len(merged_df)} ({matched_count/len(merged_df):.2%})")
    
    # Rellenar nulos con valores promedio o dejar como nan (para filtrar en el simulador)
    # Guardar el dataset resultante en la carpeta Simulacion_Inversion
    output_path = os.path.join(current_dir, "historical_with_ou_odds.csv")
    merged_df.to_csv(output_path, index=False)
    print(f"[OK] Dataset guardado exitosamente en: {output_path}")

if __name__ == "__main__":
    main()
