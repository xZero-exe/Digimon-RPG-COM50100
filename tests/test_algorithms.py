import unittest

from digimon_rl.agents import MonteCarloAgent, ValueIterationAgent
from digimon_rl.environment import DigitalWorld
from digimon_rl.experiments import evaluate


class TestAlgorithms(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.world = DigitalWorld()

    def test_value_iteration_policy_is_valid(self):
        result = ValueIterationAgent(self.world, max_iterations=160).train()
        self.assertTrue(result.deltas)
        self.assertTrue(result.policy)
        for s, action in result.policy.items():
            self.assertIn(action, self.world.actions(s))
        score = evaluate(self.world, result.policy, episodes=20, seed=1)
        self.assertEqual(score.episodes, 20)

    def test_monte_carlo_policy_is_valid(self):
        agent = MonteCarloAgent(self.world, seed=4)
        agent.train(episodes=60)
        policy = agent.deterministic_policy()
        self.assertEqual(len(agent.history), 60)
        self.assertTrue(policy)
        for s, action in policy.items():
            self.assertIn(action, self.world.actions(s))


if __name__ == "__main__":
    unittest.main()
