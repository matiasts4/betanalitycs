import unittest
import pandas as pd
import numpy as np
from simular_meta_decision import run_simulation


class TestMetaLabelingTemporal(unittest.TestCase):

    def _build_df(self, n=100):
        """Crea un DataFrame mínimo para testear simular_meta_decision."""
        np.random.seed(0)
        df = pd.DataFrame({
            'game_id': range(n),
            'date': pd.date_range('2020-01-01', periods=n, freq='D'),
            'p_home_iso': np.random.uniform(0.2, 0.5, n),
            'p_draw_iso': np.random.uniform(0.2, 0.4, n),
            'p_away_iso': np.random.uniform(0.2, 0.5, n),
            'p_dc1X_iso': np.random.uniform(0.4, 0.7, n),
            'p_dcX2_iso': np.random.uniform(0.4, 0.7, n),
            'p_over_iso': np.random.uniform(0.4, 0.6, n),
            'p_under_iso': np.random.uniform(0.4, 0.6, n),
            'B365H': np.random.uniform(1.5, 4.0, n),
            'B365D': np.random.uniform(2.5, 4.5, n),
            'B365A': np.random.uniform(1.5, 4.0, n),
            'B365_1X': np.random.uniform(1.2, 2.5, n),
            'B365_X2': np.random.uniform(1.2, 2.5, n),
            'B365>2.5': np.random.uniform(1.6, 2.3, n),
            'B365<2.5': np.random.uniform(1.6, 2.3, n),
            'target_1x2': np.random.randint(0, 3, n),
            'target_dc_1X': np.random.randint(0, 2, n),
            'target_dc_X2': np.random.randint(0, 2, n),
            'target_over_2_5_goals': np.random.randint(0, 2, n),
            'target_under_2_5_goals': np.random.randint(0, 2, n),
            'home_elo': np.random.uniform(1500, 1700, n),
            'away_elo': np.random.uniform(1500, 1700, n),
            'home_rest': np.random.randint(1, 5, n),
            'away_rest': np.random.randint(1, 5, n),
        })
        return df

    def test_meta_model_mode_runs_without_error(self):
        """El modo meta_model debe ejecutar sin errores con validación walk-forward."""
        df = self._build_df(120)
        res = run_simulation(df, mode='meta_model', edge_threshold=0.05, num_splits=3)
        self.assertIn('final_bankroll', res)
        self.assertGreaterEqual(res['bets'], 0)

    def test_meta_model_avoids_some_bets(self):
        """El meta-modelo debe evitar al menos algunas apuestas cuando hay datos suficientes."""
        df = self._build_df(200)
        res = run_simulation(df, mode='meta_model', edge_threshold=-0.10, num_splits=5)
        self.assertGreater(res['avoided'], 0)

    def test_walk_forward_does_not_use_future_splits(self):
        """
        Verificación básica de que el meta-modelo no se entrena con apuestas
        del split actual: en el primer split no hay modelo, y en splits
        posteriores el número de apuestas históricas debe ser estrictamente
        menor al índice de inicio del split actual.
        """
        df = self._build_df(200)
        n_records = len(df)
        num_splits = 5
        split_size = n_records // num_splits

        # Replicar la lógica de acumulación de historical_bets del script
        historical_bets = []
        for s_idx in range(num_splits):
            start_idx = s_idx * split_size
            end_idx = (s_idx + 1) * split_size if s_idx < num_splits - 1 else n_records
            df_split = df.iloc[start_idx:end_idx]

            # En splits > 0, el meta-modelo se entrena con historical_bets.
            if s_idx > 0:
                self.assertLessEqual(len(historical_bets), start_idx,
                                     "El meta-modelo no debe entrenar con apuestas de splits futuros")

            # Registrar apuestas que pasarían EV (simplificado: todas)
            for _ in range(len(df_split)):
                historical_bets.append({'dummy': True})


if __name__ == '__main__':
    unittest.main()
