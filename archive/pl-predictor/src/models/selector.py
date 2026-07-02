import os
import joblib
import pandas as pd
import numpy as np

from src.config import MODELS_DIR, TARGETS, FEATURES
from src.models_neural import PyTorchMLPClassifier

class MasterBetSelector:
    def __init__(self, models_dir=None):
        # Cargar Modelos Entrenados (Ahora son Pipelines que incluyen Imputer y Scaler)
        self.models = {}
        base_dir = models_dir if models_dir is not None else MODELS_DIR
        for target_name in TARGETS.keys():
            target_slug = target_name.replace(' ', '_').replace('(', '').replace(')', '').replace('.', '_')
            model_path = os.path.join(base_dir, f"model_{target_slug}.pkl")
            if os.path.exists(model_path):
                self.models[target_name] = joblib.load(model_path)
            else:
                print(f"[Selector] Model not found for {target_name} at {model_path}")
    
    def get_best_bet(self, match_features_dict, bookmaker_odds=None, kelly_fraction=0.25):
        # match_features_dict should have keys matching FEATURES
        df = pd.DataFrame([match_features_dict])
        
        # Ensure correct order
        X = df[FEATURES].copy()
        
        predictions = []
        for target_name, model in self.models.items():
            try:
                if len(model.classes_) == 2 and 1 in model.classes_:
                    idx = list(model.classes_).index(1)
                    prob = model.predict_proba(X)[0][idx]
                    pick = 1
                else:
                    # For multiclass, get max prob
                    probs = model.predict_proba(X)[0]
                    max_idx = np.argmax(probs)
                    prob = probs[max_idx]
                    pick = model.classes_[max_idx]
                    
                # Simulate Bookie Odds if not provided, assuming Bookmakers anchor heavily to Elo
                if bookmaker_odds is None:
                    elo_diff = match_features_dict.get('away_elo', 1500) - match_features_dict.get('home_elo', 1500)
                    prob_public = 1.0 / (1.0 + 10.0 ** (elo_diff / 400.0))
                    prob_public = max(0.01, min(0.99, prob_public))
                    
                    if target_name == '1X2 (Match Winner)':
                        base_prob = prob_public * 0.9
                    elif '1X' in target_name or 'X2' in target_name:
                        base_prob = min(0.99, prob_public + 0.15)
                    else:
                        base_prob = max(0.01, min(0.99, prob + 0.05)) # Bookies usually slightly overestimate totals
                        
                    offered_odds = round(max(1.01, (1.0 / base_prob) * 0.95), 2)
                else:
                    offered_odds = bookmaker_odds
                    
                fair_odds = 1.0 / prob if prob > 0.01 else 100.0
                
                if offered_odds > 1.0:
                    b = offered_odds - 1.0
                    q = 1.0 - prob
                    kelly_f = (b * prob - q) / b
                else:
                    kelly_f = -1.0
                    
                ev = (prob * offered_odds) - 1.0 if prob > 0 else -1.0
                
                if kelly_f > 0:
                    safe_kelly = min(kelly_f * kelly_fraction, 0.10) # Max 10% stake
                else:
                    safe_kelly = 0.0
                    
                predictions.append({
                    "Market": target_name,
                    "Probability": float(prob),
                    "Confidence": f"{float(prob)*100:.1f}%",
                    "Pick": int(pick),
                    "FairOdds": round(float(fair_odds), 2),
                    "ExpectedValue": round(float(ev), 3),
                    "RecommendedStakePct": round(float(safe_kelly) * 100, 2)
                })
            except Exception as e:
                pass
                
        # Sort by probability
        predictions.sort(key=lambda x: x['Probability'], reverse=True)
        return predictions
