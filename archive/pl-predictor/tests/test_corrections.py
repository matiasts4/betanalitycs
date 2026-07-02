"""
Unit tests for the critical corrections applied to BetAnalytics.

Run from archive/pl-predictor:
    python -m unittest tests.test_corrections -v
"""

import sys
import os
import unittest
import pandas as pd

# Make src/ importable when running tests directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.parlay_engine import build_same_game_parlays, calculate_sgp
from src.backtester import evaluate_market_result
from src.api import compute_elo_map, build_team_last5


class TestSGPCorrelation(unittest.TestCase):
    """Same-Game Parlay correlation ratio must affect probability and derived odds."""

    def test_calculate_sgp_uses_correlation_ratio(self):
        sels = [
            {"probability": 0.55, "odd": 2.2},
            {"probability": 0.52, "odd": 2.1},
        ]
        ratio = 1.1655
        result = calculate_sgp(sels, ratio)
        self.assertIsNotNone(result)

        expected_prob = 0.55 * 0.52 * ratio
        self.assertAlmostEqual(result["probability"], expected_prob, places=6)

        fair_odd = 1.0 / expected_prob
        expected_odd = round(max(1.05, fair_odd * 0.92), 2)
        self.assertAlmostEqual(result["odds"], expected_odd, places=2)
        self.assertAlmostEqual(result["ev"], expected_prob * expected_odd - 1.0, places=6)

    def test_different_ratio_changes_sgp(self):
        sels = [
            {"probability": 0.55, "odd": 2.2},
            {"probability": 0.52, "odd": 2.1},
        ]
        r1 = calculate_sgp(sels, 1.1655)
        r2 = calculate_sgp(sels, 1.5)
        self.assertNotEqual(r1["probability"], r2["probability"])
        self.assertNotEqual(r1["odds"], r2["odds"])

    def test_calculate_sgp_with_real_price_positive_ev(self):
        """If the bookmaker offers a generous real SGP price, EV is positive."""
        sels = [
            {"probability": 0.60, "odd": 2.0},
            {"probability": 0.55, "odd": 1.9},
        ]
        ratio = 1.2
        # The model thinks the fair correlated odd is 1/(0.60*0.55*1.2) ≈ 2.525
        # A real SGP price of 2.80 implies value.
        result = calculate_sgp(sels, ratio, odd_sgp_real=2.80)
        self.assertIsNotNone(result)
        self.assertGreater(result["ev"], 0.0)


class TestTemporalFeatures(unittest.TestCase):
    """Elo and form features must not use future information."""

    def _make_df(self):
        return pd.DataFrame({
            "home_team": ["A", "B", "A", "B"],
            "away_team": ["B", "A", "B", "A"],
            "date": pd.to_datetime(["2020-01-01", "2020-02-01", "2020-03-01", "2020-04-01"]),
            "home_elo": [1500, 1520, 1540, 1560],
            "away_elo": [1500, 1510, 1530, 1550],
            "h_l5_pts": [10, 8, 12, 9],
            "h_l5_gf": [5, 4, 6, 3],
            "h_l5_ga": [2, 3, 1, 2],
            "h_l5_sh": [20, 18, 22, 19],
            "h_l5_sot": [8, 7, 9, 6],
            "h_l5_fls": [10, 11, 9, 12],
            "h_l5_conv": [0.2, 0.18, 0.22, 0.19],
            "h_l5_xg": [1.2, 1.0, 1.4, 1.1],
            "h_l5_xga": [0.8, 1.0, 0.7, 0.9],
            "a_l5_pts": [9, 11, 8, 13],
            "a_l5_gf": [4, 6, 3, 7],
            "a_l5_ga": [3, 1, 2, 0],
            "a_l5_sh": [18, 22, 19, 23],
            "a_l5_sot": [7, 9, 6, 10],
            "a_l5_fls": [11, 9, 12, 8],
            "a_l5_conv": [0.18, 0.22, 0.19, 0.23],
            "a_l5_xg": [1.0, 1.4, 1.1, 1.5],
            "a_l5_xga": [1.0, 0.7, 0.9, 0.6],
        })

    def test_compute_elo_map_cutoff(self):
        df = self._make_df()
        # Before 2020-02-01 only the first match is visible
        elo_map = compute_elo_map(df, cutoff_date=pd.Timestamp("2020-02-01"))
        self.assertEqual(elo_map["A"], 1500.0)  # home in first match
        self.assertEqual(elo_map["B"], 1500.0)  # away in first match

        # Before 2020-04-01 the third match is the last visible one
        elo_map = compute_elo_map(df, cutoff_date=pd.Timestamp("2020-04-01"))
        self.assertEqual(elo_map["A"], 1540.0)  # home in third match
        self.assertEqual(elo_map["B"], 1530.0)  # away in third match

    def test_build_team_last5_cutoff(self):
        df = self._make_df()
        form = build_team_last5("A", df, cutoff=pd.Timestamp("2020-02-01"))
        self.assertEqual(form["pts"], 10.0)

        form = build_team_last5("A", df, cutoff=pd.Timestamp("2020-04-01"))
        self.assertEqual(form["pts"], 12.0)


class TestMarketEvaluation(unittest.TestCase):
    """Market result resolution must be deterministic."""

    def test_unknown_market_returns_none(self):
        result = evaluate_market_result("MercadoInventado", 1, 1, 1, 1)
        self.assertIsNone(result)

    def test_known_markets(self):
        self.assertTrue(evaluate_market_result("1X2", 2, 1, 2, 2))
        self.assertFalse(evaluate_market_result("1X2", 1, 2, 0, 2))
        self.assertTrue(evaluate_market_result("Over 2.5", 2, 1, None, 1))
        self.assertFalse(evaluate_market_result("Over 2.5", 1, 1, None, 1))
        self.assertTrue(evaluate_market_result("BTTS", 1, 1, None, 1))
        self.assertTrue(evaluate_market_result("BTTS - No", 1, 0, None, 1))


if __name__ == "__main__":
    unittest.main()
