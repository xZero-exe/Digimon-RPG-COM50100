"""Pruebas de técnicas: cada acción es una transición MDP explícita."""
import unittest
from dataclasses import replace

from digimon_rl.domain import Action, Ending, GameState, Zone
from digimon_rl.environment import DigitalWorld
from digimon_rl.techniques import TECHNIQUES, technique_for


class TechniqueTests(unittest.TestCase):
    def setUp(self):
        self.w = DigitalWorld()

    def state(self, form, energy=6, *, charged=False, zone=Zone.FORTRESS, enemy_hp=6):
        return GameState(zone, 6, energy, enemy_hp, form, True, charged)

    def test_four_distinct_techniques(self):
        self.assertEqual(len(TECHNIQUES), 4)
        self.assertEqual(len({t.name for t in TECHNIQUES}), 4)
        self.assertEqual([t.energy_cost for t in TECHNIQUES], [1, 2, 2, 3])

    def test_technique_only_when_energy_available(self):
        for evolved in range(4):
            t = technique_for(evolved)
            self.assertNotIn(Action.TECHNIQUE, self.w.actions(self.state(evolved, t.energy_cost-1)))
            self.assertIn(Action.TECHNIQUE, self.w.actions(self.state(evolved, t.energy_cost)))
            with self.assertRaises(ValueError):
                self.w.transitions(self.state(evolved, t.energy_cost-1), Action.TECHNIQUE)

    def test_probability_mass_all_forms(self):
        for level in range(4):
            for charged in (False, True):
                outcomes = self.w.transitions(self.state(level, charged=charged), Action.TECHNIQUE)
                self.assertAlmostEqual(sum(t.probability for t in outcomes), 1.0)
                for outcome in outcomes:
                    self.assertTrue(0 <= outcome.probability <= 1)
                    if isinstance(outcome.next_state, GameState):
                        self.assertEqual(outcome.next_state.evolved, level)
                        self.assertEqual(outcome.next_state.energy, 6 - technique_for(level).energy_cost)

    def test_greymon_cancels_announced_attack_on_hit(self):
        s = self.state(1, charged=True, enemy_hp=6)
        outcomes = self.w.transitions(s, Action.TECHNIQUE)
        # En caso de acierto, Mega Flame cancela el contraataque anunciado.
        for t in outcomes:
            if isinstance(t.next_state, GameState) and t.next_state.enemy_hp < s.enemy_hp:
                self.assertEqual(t.next_state.hp, s.hp)

    def test_metalgreymon_bypasses_armor(self):
        # La armadura viral del jefe penaliza las formas bajas, pero no los misiles Giga.
        s = self.state(2, enemy_hp=6)
        normal = max(s.enemy_hp - t.next_state.enemy_hp for t in self.w.transitions(s, Action.POWER_ATTACK)
                     if isinstance(t.next_state, GameState))
        giga = max(s.enemy_hp - t.next_state.enemy_hp for t in self.w.transitions(s, Action.TECHNIQUE)
                   if isinstance(t.next_state, GameState))
        self.assertGreater(giga, normal)

    def test_wargreymon_can_finish_six_remaining_hp(self):
        s = self.state(3, energy=3, enemy_hp=6)
        results = self.w.transitions(s, Action.TECHNIQUE)
        self.assertAlmostEqual(sum(t.probability for t in results if t.next_state == Ending.WIN), 0.85)

    def test_terminal_and_exploration_have_no_technique(self):
        self.assertNotIn(Action.TECHNIQUE, self.w.actions(self.w.start_state()))
        self.assertNotIn(Action.TECHNIQUE, self.w.actions(Ending.WIN))
        self.assertNotIn(Action.TECHNIQUE, self.w.actions(replace(self.state(3), enemy_hp=0)))

    def test_state_space_dimensions_unchanged(self):
        self.assertEqual(self.w.total_nominal_states(), 725762)


if __name__ == "__main__":
    unittest.main()
