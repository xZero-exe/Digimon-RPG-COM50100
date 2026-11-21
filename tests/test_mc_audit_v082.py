"""Pruebas del algoritmo visto en Cátedra 13, sin dependencias de Pygame."""
from __future__ import annotations

import unittest
from random import Random

from digimon_rl.agents import MonteCarloAgent
from digimon_rl.domain import Action, Ending, Episode, GameState, Step, Zone
from digimon_rl.environment import DigitalWorld
from digimon_rl.experiments import evaluate


S = GameState(Zone.FOREST, 6, 3, 2, 0, True)


class ToyWorld:
    """Entorno de episodios predeterminados para verificar retornos exactamente."""

    def __init__(self, scripted):
        self.scripted = scripted
        self.calls = 0

    def actions(self, _):
        return (Action.ATTACK,)

    def episode(self, behavior, rng, gamma=0.95, max_steps=80):
        behavior(S, self.actions(S), rng)
        run = self.scripted[self.calls % len(self.scripted)]
        self.calls += 1
        return run


def episode(rewards, truncated=False):
    steps = []
    for i, reward in enumerate(rewards):
        following = S if truncated or i < len(rewards) - 1 else Ending.WIN
        steps.append(Step(S, Action.ATTACK, reward, following))
    return Episode(tuple(steps), S if truncated else Ending.WIN, sum(rewards),
                   sum((0.5 ** i) * reward for i, reward in enumerate(rewards)), truncated)


class MCTestAudit(unittest.TestCase):
    def test_first_visit_uses_first_occurrence_not_second(self):
        # Dos visitas al mismo (s,a), G0=1 + 0.5*3 = 2.5.
        world = ToyWorld([episode((1.0, 3.0))])
        agent = MonteCarloAgent(world, gamma=0.5, seed=8)
        agent.train(episodes=1)
        self.assertAlmostEqual(agent.q[S, Action.ATTACK], 2.5)
        self.assertEqual(agent.counts[S, Action.ATTACK], 1)
        self.assertEqual(agent.completed_episodes, 1)

    def test_truncation_skips_mc_updates_and_counts(self):
        truncated = episode((100.0,), truncated=True)
        completed = episode((2.0,), truncated=False)
        agent = MonteCarloAgent(ToyWorld([truncated, completed]), seed=6)
        agent.train(episodes=2)
        self.assertEqual(agent.truncated_episodes, 1)
        self.assertEqual(agent.completed_episodes, 1)
        self.assertEqual(agent.skipped_steps, 1)
        self.assertEqual(agent.counts[S, Action.ATTACK], 1)
        self.assertAlmostEqual(agent.q[S, Action.ATTACK], 2.0)
        self.assertEqual(len(agent.history), 2)

    def test_rejects_zero_steps(self):
        agent = MonteCarloAgent(ToyWorld([episode((1.0,))]))
        with self.assertRaises(ValueError):
            agent.train(episodes=1, max_steps=0)

    def test_fallback_measured_when_policy_unknown(self):
        eval_ = evaluate(ToyWorld([episode((2.0,))]), {}, episodes=5, seed=7)
        self.assertEqual(eval_.wins, 5)
        self.assertEqual(eval_.fallback_actions, 5)
        self.assertEqual(eval_.fallback_episodes, 5)
        self.assertEqual(eval_.distinct_unseen_states, 1)
        self.assertEqual(eval_.fallback_action_rate, 1.0)

    def test_no_fallback_for_known_policy(self):
        eval_ = evaluate(ToyWorld([episode((2.0,))]), {S: Action.ATTACK}, episodes=5)
        self.assertEqual(eval_.fallback_actions, 0)
        self.assertEqual(eval_.fallback_episodes, 0)

    def test_reproducible_seed_on_real_mdp(self):
        a = MonteCarloAgent(DigitalWorld(), seed=91)
        b = MonteCarloAgent(DigitalWorld(), seed=91)
        a.train(episodes=80)
        b.train(episodes=80)
        self.assertEqual(a.history, b.history)
        self.assertEqual(a.counts, b.counts)
        self.assertEqual(a.deterministic_policy(), b.deterministic_policy())

    def test_epsilon_selection_is_stochastic_but_valid(self):
        agent = MonteCarloAgent(DigitalWorld(), epsilon=1.0, seed=15)
        actions = (Action.ATTACK, Action.GUARD)
        chosen = [agent.behave(S, actions, Random(4)) for _ in range(100)]
        self.assertEqual(set(chosen), set(actions))


if __name__ == "__main__":
    unittest.main()
