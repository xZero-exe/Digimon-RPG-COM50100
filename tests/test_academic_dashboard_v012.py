"""Panel académico v0.12: datos reproducibles y navegación sin SDL."""
from __future__ import annotations

import csv
import json
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch

from digimon_rl.academic_dashboard import AcademicDashboard, METRICS
from digimon_rl.environment import DigitalWorld
from digimon_rl.presentation import Screen
from digimon_rl.session import AdventureController, ControlMode


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "resultados" / "convergencia_v011"


class AcademicDataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = AcademicDashboard.load(DATA)

    def test_original_results_are_read_from_files(self):
        self.assertEqual(len(self.data.rows), 5)
        self.assertEqual([x.episodes for x in self.data.rows], [500, 2000, 5000, 10000, 20000])
        self.assertAlmostEqual(self.data.rows[0].mc_win_rate, 0.149)
        self.assertAlmostEqual(self.data.rows[-1].mc_win_rate, 0.826)
        self.assertAlmostEqual(self.data.rows[-1].dp_win_rate, 0.96)
        self.assertEqual(self.data.reachable_states, 48553)

    def test_four_metrics_and_reference_conditions(self):
        for metric in METRICS:
            mc, dp, sd = self.data.values(metric.key)
            self.assertEqual(len(mc), len(self.data.rows))
            self.assertEqual(dp is not None, metric.include_dp)
        self.assertIsNone(self.data.values("fallback")[2])
        with self.assertRaises(KeyError):
            self.data.values("invented")

    def test_seeds_evaluations_and_increment(self):
        self.assertEqual(self.data.train_seeds, (41, 42, 43, 44, 45))
        self.assertEqual(self.data.eval_episodes, 200)
        self.assertEqual(self.data.gamma, 0.95)
        self.assertEqual(self.data.epsilon, 0.15)
        self.assertLess(self.data.rows[0].mc_win_rate, self.data.rows[-1].mc_win_rate)
        self.assertGreater(self.data.rows[0].fallback, self.data.rows[-1].fallback)

    def test_six_slides_retain_course_constraints(self):
        slides = self.data.slides()
        self.assertEqual(len(slides), 6)
        text = " ".join(x for slide in slides for x in slide.lines)
        self.assertIn("First-Visit", text)
        self.assertIn("sin librerías RL", text)
        self.assertIn("no prueba convergencia formal", text)
        self.assertEqual(slides[-1].metric, None)

    def test_malformed_csv_detected(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            (folder / "curvas_resumen.csv").write_text(
                (DATA / "curvas_resumen.csv").read_text(encoding="utf-8")
                .replace('0.149', 'nan'), encoding="utf-8")
            (folder / "resumen_v011.json").write_bytes((DATA / "resumen_v011.json").read_bytes())
            with self.assertRaises(ValueError):
                AcademicDashboard.load(folder)

    def test_missing_file_is_not_silent(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(FileNotFoundError):
                AcademicDashboard.load(Path(temp))


class ScreenTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        fake = types.ModuleType('pygame')
        keys = ('K_ESCAPE K_RETURN K_SPACE K_F1 K_F2 K_F3 K_F4 K_F5 '
                'K_h K_c K_p K_m K_r K_a K_PLUS K_EQUALS K_KP_PLUS '
                'K_MINUS K_KP_MINUS K_t K_LEFT K_RIGHT K_DOWN K_UP').split()
        keys += [f'K_{i}' for i in range(1, 8)]
        for i, key in enumerate(keys, 100):
            setattr(fake, key, i)
        cls.fake = fake
        with patch.dict(sys.modules, {'pygame': fake}):
            from digimon_rl.gui.app import RPGApp
            cls.app_cls = RPGApp

    def setUp(self):
        world = DigitalWorld()
        controller = AdventureController(world, {}, {}, seed=3)
        self.app = self.app_cls(controller, dashboard=AcademicDashboard.load(DATA))

    def test_f4_results_from_title_and_return(self):
        self.app._on_key(self.fake.K_F4)
        self.assertEqual(self.app.presentation.screen, Screen.RESULTS)
        self.assertEqual(self.app.results_metric_index, 0)
        self.app._on_key(self.fake.K_RIGHT)
        self.assertEqual(self.app.results_metric_index, 1)
        self.app._on_key(self.fake.K_ESCAPE)
        self.assertEqual(self.app.presentation.screen, Screen.TITLE)

    def test_demo_from_title_and_live_handoff(self):
        self.app._on_key(self.fake.K_F5)
        self.assertEqual(self.app.presentation.screen, Screen.DEMO)
        self.app._on_key(self.fake.K_RIGHT)
        self.assertEqual(self.app.demo_index, 1)
        self.app._on_key(self.fake.K_F2)
        self.assertEqual(self.app.presentation.screen, Screen.GAME)
        self.assertEqual(self.app.controller.mode, ControlMode.MONTE_CARLO)

    def test_results_pauses_simulation_and_preserves_episode(self):
        self.app._on_key(self.fake.K_F1)
        self.app._on_key(self.fake.K_a)
        self.assertTrue(self.app.auto)
        state = self.app.controller.state
        self.app._on_key(self.fake.K_F4)
        self.assertFalse(self.app.auto)
        self.app._on_key(self.fake.K_ESCAPE)
        self.assertEqual(self.app.presentation.screen, Screen.GAME)
        self.assertEqual(self.app.controller.state, state)

    def test_switch_between_results_and_demo_keeps_original_return_screen(self):
        self.app._on_key(self.fake.K_F3)
        self.app._on_key(self.fake.K_F4)
        self.app._on_key(self.fake.K_F5)
        self.assertEqual(self.app.presentation.screen, Screen.DEMO)
        self.app._on_key(self.fake.K_ESCAPE)
        self.assertEqual(self.app.presentation.screen, Screen.GAME)


if __name__ == '__main__':
    unittest.main()
