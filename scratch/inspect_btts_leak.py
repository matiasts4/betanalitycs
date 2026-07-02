import pandas as pd
import numpy as np

def main():
    csv_path = "Simulacion_Inversion/predicciones_prueba_calibradas.csv"
    if not pd.io.common.file_exists(csv_path):
        print("File not found")
        return
    df = pd.read_csv(csv_path)
    
    print("Columns in predictions:")
    print(df.columns.tolist())
    
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)
    
    print("\nFirst 10 rows for BTTS:")
    cols = ['date', 'home_team', 'away_team', 'target_btts', 'B365H', 'B365A', 'B365>2.5', 'B365<2.5', 'B365_BTTS_Yes', 'B365_BTTS_No', 'p_btts_uncal']
    print(df[cols].head(10))
    
    # Analyze bets placed on BTTS under uncal and iso
    for mode in ['uncal', 'iso', 'sig']:
        p_col = f'p_btts_{mode}'
        df['ev_yes'] = df[p_col] * df['B365_BTTS_Yes'] - 1
        df['ev_no'] = (1.0 - df[p_col]) * df['B365_BTTS_No'] - 1
        
        # Bets on YES
        bets_yes = df[df['ev_yes'] >= 0.05]
        yes_win_rate = bets_yes['target_btts'].mean() if len(bets_yes) > 0 else 0
        
        # Bets on NO
        bets_no = df[df['ev_no'] >= 0.05]
        no_win_rate = (bets_no['target_btts'] == 0).mean() if len(bets_no) > 0 else 0
        
        print(f"\nMode: {mode}")
        print(f"  Bets on BTTS Yes: {len(bets_yes)} | Win Rate: {yes_win_rate:.2%} | Avg Odd: {bets_yes['B365_BTTS_Yes'].mean():.2f}")
        print(f"  Bets on BTTS No: {len(bets_no)} | Win Rate: {no_win_rate:.2%} | Avg Odd: {bets_no['B365_BTTS_No'].mean():.2f}")

        # Let's check overall correlation
        corr = df[p_col].corr(df['target_btts'])
        print(f"  Correlation of {p_col} with target_btts: {corr:.4f}")

if __name__ == '__main__':
    main()
