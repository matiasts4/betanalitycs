import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
HISTORICAL_DIR = os.path.join(BASE_DIR, "data", "historical")
FEATURES_PATH = os.path.join(HISTORICAL_DIR, "historical_sanitized_v11.csv")
MODELS_DIR = os.path.join(BASE_DIR, "models")

# ─────────────────────────────────────────────────────────────────────────────
# ACTIVE MARKETS — Cuota esperada realista ≥ 1.50 con EV potencialmente positivo
# ─────────────────────────────────────────────────────────────────────────────
TARGETS = {
    "1X2 (Match Winner)":              'target_1x2',
    "Double Chance 1X (Home or Draw)": 'target_dc_1X',
    "Double Chance X2 (Away or Draw)": 'target_dc_X2',
    "Over 2.5 Goals":                  'target_over_2_5_goals',
    "Under 2.5 Goals":                 'target_under_2_5_goals',
    "BTTS (Both Teams To Score)":      'target_btts',
    "BTTS - No":                       'target_btts_no',
    "Home Clean Sheet":                'target_home_clean_sheet',
}

FEATURES = [
    'home_elo', 'away_elo', 'home_rest', 'away_rest',
    'h_l5_pts', 'h_l5_sh', 'h_l5_sot', 'h_l5_sot_c', 'h_l5_gf', 'h_l5_ga', 'h_l5_fls', 'h_l5_conv', 'h_l5_xg', 'h_l5_xga',
    'a_l5_pts', 'a_l5_sh', 'a_l5_sot', 'a_l5_sot_c', 'a_l5_gf', 'a_l5_ga', 'a_l5_fls', 'a_l5_conv', 'a_l5_xg', 'a_l5_xga',
    'referee_avg_cards_history', 'is_derby', 'relegation_pressure'
]
