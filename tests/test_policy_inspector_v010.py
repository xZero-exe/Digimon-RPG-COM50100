"""Pruebas del laboratorio tabular: integridad, Bellman y visita MC."""
from pathlib import Path
import tempfile
import unittest

from digimon_rl.domain import Action, GameState
from digimon_rl.environment import DigitalWorld
from digimon_rl.inspector import PolicyInspector, export_analysis
from digimon_rl.policy_io import save_policy
from digimon_rl.presentation import GamePresentation, Screen
from digimon_rl.session import ControlMode


class InspectorTests(unittest.TestCase):
    def setUp(self):
        self.world = DigitalWorld()
        self.state = self.world.start_state()
        self.first = self.world.actions(self.state)[0]

    def test_no_mc_value_without_first_visit(self):
        ins = PolicyInspector(self.world, {self.state: self.first},
                              {self.state: self.first}, {}, {}, {}, episodes=3)
        view = ins.inspect(self.state)
        self.assertEqual(view.mc_action, self.first)
        self.assertTrue(view.learned_state)
        self.assertTrue(view.agrees)
        self.assertTrue(all(a.mc_q is None and a.mc_visits == 0 for a in view.actions))

    def test_mc_actual_visit_even_when_q_zero(self):
        ins = PolicyInspector(self.world, {self.state: self.first}, {},
                              mc_q={(self.state, self.first): 0.0},
                              mc_counts={(self.state, self.first): 3})
        item = ins.inspect(self.state).actions[0]
        self.assertEqual(item.mc_q, 0.0)
        self.assertEqual(item.mc_visits, 3)
        self.assertFalse(ins.inspect(self.state).learned_state)

    def test_bellman_uses_terminal_zero(self):
        actions = self.world.actions(self.state)
        # Proporcionamos valores para los sucesores no terminales.
        values = {self.state: 2.5}
        for a in actions:
            for t in self.world.transitions(self.state, a):
                if isinstance(t.next_state, GameState):
                    values[t.next_state] = 3.0
        ins = PolicyInspector(self.world, {self.state:self.first}, {}, dp_values=values)
        row = ins.inspect(self.state).actions[0]
        expected = sum(t.probability * (t.reward + .95*(values[t.next_state] if isinstance(t.next_state, GameState) else 0))
                       for t in self.world.transitions(self.state, self.first))
        self.assertAlmostEqual(row.dp_q, expected)

    def test_no_dp_values_means_no_q(self):
        ins = PolicyInspector(self.world, {self.state:self.first}, {})
        self.assertIsNone(ins.inspect(self.state).actions[0].dp_q)

    def test_export_verifies_policy_integrity(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            dp, mc, data = p/'dp.json', p/'mc.json', p/'analysis.gz'
            save_policy(dp, {self.state:self.first}, algorithm='value_iteration')
            save_policy(mc, {self.state:self.first}, algorithm='monte_carlo_first_visit', episodes=3)
            export_analysis(data, {self.state:3.0}, {(self.state,self.first):2.0},
                            {(self.state,self.first):4}, dp, mc, episodes=3, gamma=.95)
            loaded = PolicyInspector.from_export(self.world, {self.state:self.first},
                                                 {self.state:self.first}, data, dp, mc)
            self.assertEqual(loaded.inspect(self.state).actions[0].mc_visits, 4)
            self.assertEqual(loaded.episodes, 3)
            mc.write_text(mc.read_text()+' ', encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'políticas'):
                PolicyInspector.from_export(self.world, {}, {}, data, dp, mc)

    def test_screen_lab_returns_to_game(self):
        p = GamePresentation()
        p.start(ControlMode.MANUAL)
        p.open(Screen.ANALYSIS)
        self.assertEqual(p.screen, Screen.ANALYSIS)
        p.close()
        self.assertEqual(p.screen, Screen.GAME)


if __name__ == '__main__':
    unittest.main()
