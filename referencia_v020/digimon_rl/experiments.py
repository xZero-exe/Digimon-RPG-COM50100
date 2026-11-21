"""Experimentación reproducible y comparación justa de políticas."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from random import Random

from .domain import Action, Ending, Episode, GameState
from .environment import DigitalWorld


@dataclass(frozen=True)
class Evaluation:
    episodes: int
    wins: int
    losses: int
    truncated: int
    win_rate: float
    mean_reward: float
    mean_discounted_return: float
    mean_steps: float
    fallback_actions: int = 0
    fallback_episodes: int = 0
    fallback_action_rate: float = 0.0
    distinct_unseen_states: int = 0


def evaluate(world: DigitalWorld, policy: dict[GameState, Action], episodes: int = 500,
             seed: int = 1234, gamma: float = 0.95, max_steps: int = 80) -> Evaluation:
    if episodes < 1:
        raise ValueError("El número de episodios de evaluación debe ser positivo")
    if max_steps < 1:
        raise ValueError("max_steps debe ser positivo")
    rng = Random(seed)
    fallback_actions = 0
    fallback_episodes = 0
    unseen_states: set[GameState] = set()
    total_actions = 0
    runs = []
    for _ in range(episodes):
        missing_this_episode = False

        def choose(s: GameState, legal: tuple[Action, ...], _: Random) -> Action:
            nonlocal fallback_actions, missing_this_episode, total_actions
            total_actions += 1
            selected = policy.get(s)
            if selected is None:
                fallback_actions += 1
                missing_this_episode = True
                unseen_states.add(s)
                return legal[0]  # comportamiento anterior, ahora medido
            if selected not in legal:
                raise ValueError(f"La política tiene una acción ilegal: {selected}")
            return selected

        runs.append(world.episode(choose, rng, gamma, max_steps))
        fallback_episodes += int(missing_this_episode)
    won = sum(run.won for run in runs)
    lost = sum(run.final_state == Ending.LOSS for run in runs)
    return Evaluation(
        episodes=episodes,
        wins=won,
        losses=lost,
        truncated=episodes - won - lost,
        win_rate=won / episodes,
        mean_reward=sum(run.total_reward for run in runs) / episodes,
        mean_discounted_return=sum(run.discounted_return for run in runs) / episodes,
        mean_steps=sum(len(run.steps) for run in runs) / episodes,
        fallback_actions=fallback_actions,
        fallback_episodes=fallback_episodes,
        fallback_action_rate=fallback_actions / total_actions if total_actions else 0.0,
        distinct_unseen_states=len(unseen_states),
    )


def sample_adventure(world: DigitalWorld, policy: dict[GameState, Action], seed: int = 7,
                     max_steps: int = 80) -> Episode:
    rng = Random(seed)
    return world.episode(lambda s, legal, _: policy.get(s, legal[0]), rng, max_steps=max_steps)
