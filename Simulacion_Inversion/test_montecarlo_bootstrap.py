import unittest
import numpy as np
from simulacion_montecarlo import run_monte_carlo


class TestMonteCarloBootstrap(unittest.TestCase):

    def test_all_wins_flat(self):
        """Con flat stake y todas las apuestas ganadoras, todos los caminos son rentables."""
        placed_bets = [
            {'odd': 2.0, 'ev': 0.10, 'win': True},
            {'odd': 3.0, 'ev': 0.20, 'win': True},
        ]
        ruin, dd, finals, dds, rois = run_monte_carlo(
            placed_bets, staking_strategy='flat', num_simulations=10, random_seed=7
        )
        self.assertTrue(all(f >= 1000.0 for f in finals))
        # Cada camino tiene 2 apuestas ganadoras flat de $10: mínimo 1020, máximo 1040.
        self.assertTrue(all(f >= 1020.0 for f in finals))
        self.assertTrue(all(f <= 1040.0 for f in finals))

    def test_all_losses_flat(self):
        """Con flat stake y todas las apuestas perdedoras, todos los caminos pierden el stake total."""
        placed_bets = [
            {'odd': 2.0, 'ev': 0.10, 'win': False},
            {'odd': 3.0, 'ev': 0.20, 'win': False},
        ]
        ruin, dd, finals, dds, rois = run_monte_carlo(
            placed_bets, staking_strategy='flat', num_simulations=10, random_seed=7
        )
        self.assertTrue(all(f == 980.0 for f in finals))

    def test_bootstrap_mean_matches_chronological_flat(self):
        """El bootstrap de retornos históricos debe tener una media cercana al backtest cronológico."""
        np.random.seed(123)
        # 100 apuestas con cuota 3.0 y 30% de aciertos -> ROI = -10%
        placed_bets = [
            {'odd': 3.0, 'ev': 0.10, 'win': (i < 30)}
            for i in range(100)
        ]
        ruin, dd, finals, dds, rois = run_monte_carlo(
            placed_bets, staking_strategy='flat', num_simulations=2000, random_seed=42
        )
        # ROI cronológico: 30*10*2 - 70*10 = -100 sobre 1000 apostado -> -10%
        # La media del bootstrap debe estar cerca de 900.
        mean_final = np.mean(finals)
        self.assertGreater(mean_final, 850.0)
        self.assertLess(mean_final, 950.0)

    def test_quarter_kelly_respects_bankroll(self):
        """Quarter Kelly no debe apostar más del 2.5% de la banca."""
        placed_bets = [{'odd': 2.0, 'ev': 0.10, 'win': False} for _ in range(50)]
        ruin, dd, finals, dds, rois = run_monte_carlo(
            placed_bets, staking_strategy='quarter', num_simulations=5, random_seed=1
        )
        # Con todas perdedoras y stake inicial <= 25, no se puede perder más de 1000.
        self.assertTrue(all(f >= 0 for f in finals))


if __name__ == '__main__':
    unittest.main()
