import unittest
from random import Random

from digimon_rl.domain import Action, Ending, GameState, Zone
from digimon_rl.environment import DigitalWorld


class TestMDP(unittest.TestCase):
    def setUp(self):
        self.world = DigitalWorld()

    def test_state_count(self):
        self.assertEqual(self.world.total_nominal_states(), 725762)
        self.assertGreaterEqual(len(self.world.reachable_states()), 15)

    def test_legal_actions(self):
        s = self.world.start_state()
        self.assertEqual(self.world.actions(s), (Action.ROUTE_FOREST, Action.ROUTE_CAVE))
        self.assertEqual(self.world.actions(Ending.WIN), ())
        with self.assertRaises(ValueError):
            self.world.transitions(s, Action.DIGIVOLVE)

    def test_transition_probabilities_sum_to_one(self):
        for state in self.world.reachable_states():
            for action in self.world.actions(state):
                probabilities = self.world.transitions(state, action)
                self.assertAlmostEqual(sum(p.probability for p in probabilities), 1.0, places=10)
                self.assertTrue(all(p.probability >= 0 for p in probabilities))

    def test_all_reachable_states_in_range(self):
        for s in self.world.reachable_states():
            self.assertTrue(1 <= s.hp <= 6)
            self.assertTrue(0 <= s.energy <= 6)
            self.assertTrue(0 <= s.enemy_hp <= self.world.MAX_ENEMY_HP)
            self.assertIn(s.zone, Zone)

    def test_attack_can_finish_boss(self):
        boss = GameState(Zone.FORTRESS, hp=3, energy=1, enemy_hp=1,
                         evolved=3, potion=False)
        outcomes = self.world.transitions(boss, Action.ATTACK)
        self.assertTrue(any(p.next_state == Ending.WIN for p in outcomes))

    def test_episode_ends(self):
        def policy(s, legal, rng):
            return rng.choice(legal)
        run = self.world.episode(policy, Random(2), max_steps=80)
        self.assertTrue(run.truncated or isinstance(run.final_state, Ending))
        self.assertLessEqual(len(run.steps), 80)


if __name__ == "__main__":
    unittest.main()
