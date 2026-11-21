"""Pruebas académicas de continuidad, aprendizaje acumulativo y ausencia de librerías RL."""
from __future__ import annotations
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from verificar_sin_librerias_rl import scan_project, violations_in_source
from curvas_aprendizaje_v011 import parse_ints, summarize, group_summary
from digimon_rl.agents import MonteCarloAgent
from digimon_rl.environment import DigitalWorld


class NoExternalRLTests(unittest.TestCase):
    def test_project_has_no_rl_library_imports_or_dependencies(self):
        errors, checked = scan_project(ROOT)
        self.assertGreaterEqual(checked, 10)
        self.assertEqual(errors, [])

    def test_detects_direct_rl_import(self):
        self.assertTrue(violations_in_source('import gymnasium as gym', 'bad.py'))
        self.assertTrue(violations_in_source('from stable_baselines3 import PPO', 'bad.py'))

    def test_detects_simple_dynamic_import(self):
        self.assertTrue(violations_in_source('importlib.import_module("ray.rllib")'))
        self.assertTrue(violations_in_source('__import__("gym")'))

    def test_allows_numpy_pygame_and_python_standard(self):
        self.assertEqual(violations_in_source('import numpy as np\nimport pygame\nfrom random import Random'), [])


class ContinuousLearningTests(unittest.TestCase):
    def test_splits_match_uninterrupted_training(self):
        world = DigitalWorld()
        a = MonteCarloAgent(world, seed=61)
        b = MonteCarloAgent(world, seed=61)
        a.train(episodes=6)
        a.train(episodes=11)
        b.train(episodes=17)
        self.assertEqual(a.history, b.history)
        self.assertEqual(a.counts, b.counts)
        self.assertEqual(dict(a.q), dict(b.q))
        self.assertEqual(tuple(e[0] for e in a.history), tuple(range(1,18)))

    def test_no_bootstrap_on_truncated_episode(self):
        # La implementación existente debe registrar los truncamientos sin actualizar Q.
        a = MonteCarloAgent(DigitalWorld(), seed=14)
        a.train(episodes=1, max_steps=1)
        self.assertEqual(a.completed_episodes+a.truncated_episodes, 1)
        if a.truncated_episodes:
            self.assertEqual(a.visited_pairs, 0)

    def test_parse_and_summary_for_multiple_seeds(self):
        self.assertEqual(parse_ints('10,20,40'), (10,20,40))
        for value in ('1,1', '-1,4', '1,0', '0', ''):
            with self.subTest(value=value), self.assertRaises(ValueError):
                parse_ints(value)
        self.assertAlmostEqual(summarize([.5,.7])['mean'], .6)

    def test_grouped_statistics(self):
        rows = [{'checkpoint':cp,'mc_win_rate':mc,'dp_win_rate':.9,
                 'mc_discounted_return':1.0,'dp_discounted_return':2.0,
                 'mc_state_coverage':.2,'mc_fallback_action_rate':.01}
                for cp in (10,20) for mc in (.5,.7)]
        report = group_summary(rows, (10,20))
        self.assertEqual(len(report),2)
        self.assertEqual(report[0]['n_seeds'],2)
        self.assertAlmostEqual(report[0]['mc_win_rate']['mean'],.6)
        self.assertAlmostEqual(report[1]['win_rate_gap']['mean'],.3)


if __name__ == '__main__':
    unittest.main()
