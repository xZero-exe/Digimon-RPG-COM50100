"""Regresión de las mecánicas v0.6: fase visible y acción táctica."""
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from digimon_rl.domain import Action, GameState, Ending, Zone
from digimon_rl.environment import DigitalWorld
from digimon_rl.policy_io import save_policy, load_policy

class TestEnemyIntent(unittest.TestCase):
    def setUp(self):
        self.w = DigitalWorld()

    def test_initial_intent_is_not_charging(self):
        self.assertFalse(self.w.start_state().enemy_charging)
        state = GameState(Zone.CAVE, 6, 3, 0, 0, True)
        for t in self.w.transitions(state, Action.ADVANCE):
            self.assertIsInstance(t.next_state, GameState)
            self.assertFalse(t.next_state.enemy_charging)

    def test_interrupt_only_if_charging_and_energy(self):
        def state(energy, charged):
            return GameState(Zone.RUINS, 6, energy, 3, 2, True, charged)
        self.assertNotIn(Action.INTERRUPT, self.w.actions(state(3, False)))
        self.assertNotIn(Action.INTERRUPT, self.w.actions(state(0, True)))
        self.assertIn(Action.INTERRUPT, self.w.actions(state(3, True)))

    def test_interrupt_success_prevents_attack(self):
        state = GameState(Zone.FORTRESS, 4, 4, 6, 2, True, True)
        transitions = self.w.transitions(state, Action.INTERRUPT)
        self.assertAlmostEqual(sum(t.probability for t in transitions),1)
        protected = [t for t in transitions if isinstance(t.next_state, GameState)
                     and t.next_state.enemy_hp == 5]
        self.assertTrue(protected)
        self.assertTrue(all(t.next_state.hp == 4 and t.next_state.energy == 3
                            for t in protected))

    def test_charged_attack_more_dangerous(self):
        normal = GameState(Zone.RUINS, 6, 2, 4, 1, True, False)
        charged = GameState(Zone.RUINS, 6, 2, 4, 1, True, True)
        def expected_damage(state):
            return sum(t.probability * (state.hp - t.next_state.hp)
                       for t in self.w.transitions(state, Action.GUARD)
                       if isinstance(t.next_state, GameState))
        # Incluso tras defender, un golpe fuerte es al menos tan peligroso.
        self.assertGreaterEqual(expected_damage(charged), expected_damage(normal))

    def test_transition_retains_next_intent_in_state(self):
        state=GameState(Zone.RUINS, 6, 4, 4, 2, True, False)
        outcome=self.w.transitions(state, Action.GUARD)
        self.assertTrue(any(isinstance(t.next_state, GameState) and t.next_state.enemy_charging
                            for t in outcome))
        self.assertTrue(any(isinstance(t.next_state, GameState) and not t.next_state.enemy_charging
                            for t in outcome))
        self.assertAlmostEqual(sum(t.probability for t in outcome),1)

    def test_policy_round_trip_includes_intent(self):
        state=GameState(Zone.RUINS,6,4,4,2,True,True)
        with TemporaryDirectory() as temp:
            file=Path(temp)/'p.json'
            save_policy(file,{state:Action.INTERRUPT},algorithm='test')
            self.assertEqual(load_policy(file,self.w),{state:Action.INTERRUPT})

    def test_boss_defeat_terminal(self):
        state=GameState(Zone.FORTRESS,6,4,1,3,True,True)
        self.assertTrue(any(t.next_state==Ending.WIN
                            for t in self.w.transitions(state,Action.ATTACK)))

if __name__=='__main__':unittest.main()
