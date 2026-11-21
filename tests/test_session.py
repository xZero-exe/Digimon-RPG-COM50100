import unittest
from random import Random

from digimon_rl.domain import Action, Ending, GameState
from digimon_rl.environment import DigitalWorld
from digimon_rl.session import AdventureController, ControlMode


class TestAdventureController(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.world = DigitalWorld()
        # Controlador: no duplicar el entrenamiento DP ya verificado en test_algorithms.
        cls.dp = {cls.world.start_state(): Action.ROUTE_FOREST}
        cls.controller = AdventureController(cls.world, cls.dp, {}, seed=12)

    def setUp(self):
        self.controller.reset(ControlMode.DYNAMIC_PROGRAMMING)

    def test_automatic_uses_legal_actions(self):
        c = self.controller
        for _ in range(80):
            if c.finished:
                break
            action = c.selected_action()
            self.assertIn(action, c.legal_actions)
            report = c.advance()
            self.assertEqual(report.step.action, action)
            self.assertEqual(report.turn, c.turn)
            self.assertEqual(report.finished, c.finished)
        self.assertTrue(c.finished)
        self.assertLessEqual(len(c.history), 12)

    def test_manual_requires_explicit_action(self):
        c = self.controller
        c.reset(ControlMode.MANUAL)
        self.assertIsNone(c.selected_action())
        with self.assertRaises(ValueError):
            c.advance()
        self.assertEqual(c.turn, 0)
        report = c.advance(Action.ROUTE_FOREST)
        self.assertEqual(report.step.action, Action.ROUTE_FOREST)
        self.assertEqual(c.turn, 1)
        self.assertIsInstance(c.state, GameState)

    def test_illegal_action_does_not_change_state(self):
        c = self.controller
        previous = c.state
        with self.assertRaises(ValueError):
            c.advance(Action.HEAL)
        self.assertEqual(c.state, previous)
        self.assertEqual(c.turn, 0)

    def test_change_mode_resets_episode(self):
        c = self.controller
        c.advance()
        c.reset(ControlMode.MONTE_CARLO)
        self.assertEqual(c.mode, ControlMode.MONTE_CARLO)
        self.assertEqual(c.state, self.world.start_state())
        self.assertEqual(c.reward, 0)
        self.assertEqual(c.turn, 0)
        self.assertEqual(c.selected_action(), Action.ROUTE_FOREST)

    def test_hard_turn_limit(self):
        c = AdventureController(self.world, {}, {}, max_steps=1, seed=2)
        c.advance()
        self.assertTrue(c.finished)
        self.assertEqual(c.outcome, "LIMITE DE TURNOS")
        with self.assertRaises(RuntimeError):
            c.advance()


if __name__ == "__main__":
    unittest.main()
