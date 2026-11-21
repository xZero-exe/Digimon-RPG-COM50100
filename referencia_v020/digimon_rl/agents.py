"""Agentes de Programación Dinámica y control Monte Carlo sin librerías de RL."""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from random import Random

import numpy as np  # solo álgebra de arreglos; NO librería de aprendizaje reforzado

from .domain import Action, Ending, GameState, State
from .environment import DigitalWorld


@dataclass(frozen=True)
class DPResult:
    policy: dict[GameState, Action]
    values: dict[GameState, float]
    deltas: tuple[float, ...]


class ValueIterationAgent:
    """Control mediante Programación Dinámica con modelo de transición conocido."""

    def __init__(self, world: DigitalWorld, gamma: float = 0.95,
                 tolerance: float = 1e-8, max_iterations: int = 500):
        if not (0 < gamma < 1):
            raise ValueError("gamma debe estar entre 0 y 1")
        self.world = world
        self.gamma = gamma
        self.tolerance = tolerance
        self.max_iterations = max_iterations

    def train(self) -> DPResult:
        """Value Iteration de Bellman en arreglos dispersos (mismo algoritmo).

        El modelo se construye UNA vez, no en cada iteración. Cada transición
        se representa por (índice de acción, probabilidad, recompensa,
        índice siguiente estado). `np.bincount` agrega retornos por acción;
        `np.maximum.reduceat` aplica el operador max de Bellman por estado.
        No hay otra técnica RL: es exactamente Value Iteration tabular.
        """
        states = self.world.reachable_states()
        index = {state: i for i, state in enumerate(states)}
        terminal = len(states)  # V(terminal) = 0 siempre
        actions: list[Action] = []
        starts = [0]
        edge_actions: list[int] = []
        edge_prob: list[float] = []
        edge_rewards: list[float] = []
        edge_next: list[int] = []

        for s in states:
            for a in self.world.actions(s):
                action_id = len(actions)
                actions.append(a)
                for outcome in self.world.transitions(s, a):
                    edge_actions.append(action_id)
                    edge_prob.append(outcome.probability)
                    edge_rewards.append(outcome.reward)
                    edge_next.append(index.get(outcome.next_state, terminal))
            starts.append(len(actions))

        action_idx = np.asarray(edge_actions, dtype=np.int32)
        probabilities = np.asarray(edge_prob, dtype=np.float64)
        probabilities_rewards = probabilities * np.asarray(edge_rewards, dtype=np.float64)
        next_idx = np.asarray(edge_next, dtype=np.int32)
        boundaries = np.asarray(starts[:-1], dtype=np.int32)
        values = np.zeros(terminal + 1, dtype=np.float64)
        deltas: list[float] = []

        def q_values(current: np.ndarray) -> np.ndarray:
            contributions = probabilities_rewards + self.gamma * probabilities * current[next_idx]
            return np.bincount(action_idx, weights=contributions, minlength=len(actions))

        for _ in range(self.max_iterations):
            q = q_values(values)
            next_values = np.maximum.reduceat(q, boundaries)
            delta = float(np.max(np.abs(next_values - values[:terminal])))
            values[:terminal] = next_values
            deltas.append(delta)
            if delta < self.tolerance:
                break

        q = q_values(values)
        policy = {
            s: actions[starts[i] + int(np.argmax(q[starts[i]:starts[i + 1]]))]
            for i, s in enumerate(states)
        }
        return DPResult(policy, dict(zip(states, (float(v) for v in values[:terminal]))), tuple(deltas))



class MonteCarloAgent:
    """Control Monte Carlo on-policy first-visit con política epsilon-greedy.

    Solo aprende de los episodios muestreados; no consulta `transitions` para
    calcular valores esperados y por lo tanto no utiliza el modelo conocido.
    """

    def __init__(self, world: DigitalWorld, gamma: float = 0.95,
                 epsilon: float = 0.15, seed: int = 7):
        if not (0 < gamma < 1):
            raise ValueError("gamma debe estar entre 0 y 1")
        if not (0 <= epsilon <= 1):
            raise ValueError("epsilon debe estar en [0, 1]")
        self.world = world
        self.gamma = gamma
        self.epsilon = epsilon
        self.rng = Random(seed)
        self.q: dict[tuple[GameState, Action], float] = defaultdict(float)
        self.counts: dict[tuple[GameState, Action], int] = defaultdict(int)
        self.history: list[tuple[int, float, bool, int]] = []
        # Diagnóstico de episodios para control Monte Carlo episódico.
        self.truncated_episodes = 0
        self.completed_episodes = 0
        self.skipped_steps = 0

    def greedy_action(self, state: GameState, legal: tuple[Action, ...]) -> Action:
        # Desempate aleatorio durante entrenamiento para no favorecer la primera acción.
        maximum = max(self.q[(state, action)] for action in legal)
        best = [a for a in legal if abs(self.q[(state, a)] - maximum) < 1e-12]
        return self.rng.choice(best)

    def behave(self, state: GameState, legal: tuple[Action, ...], _: Random) -> Action:
        if self.rng.random() < self.epsilon:
            return self.rng.choice(legal)
        return self.greedy_action(state, legal)

    def train(self, episodes: int = 10_000, max_steps: int = 80) -> None:
        if episodes < 1:
            raise ValueError("Se requiere al menos un episodio")
        if max_steps < 1:
            raise ValueError("max_steps debe ser positivo")
        completed_before = len(self.history)
        for number in range(completed_before + 1, completed_before + episodes + 1):
            episode = self.world.episode(self.behave, self.rng,
                                         gamma=self.gamma, max_steps=max_steps)
            # El retorno MC episódico debe llegar a un estado terminal.
            # Si el límite artificial de simulación corta la aventura,
            # el episodio se registra, pero NO se usa para actualizar Q.
            if episode.truncated:
                self.truncated_episodes += 1
                self.skipped_steps += len(episode.steps)
                self.history.append((number, episode.total_reward, False,
                                     len(episode.steps)))
                continue
            self.completed_episodes += 1
            G = 0.0
            returns: list[float] = []
            for step in reversed(episode.steps):
                G = step.reward + self.gamma * G
                returns.append(G)
            returns.reverse()
            visited: set[tuple[GameState, Action]] = set()
            for step, return_value in zip(episode.steps, returns):
                key = (step.state, step.action)
                if key in visited:
                    continue
                visited.add(key)
                self.counts[key] += 1
                # Media incremental, equivalente a promediar los retornos first-visit.
                self.q[key] += (return_value - self.q[key]) / self.counts[key]
            self.history.append((number, episode.total_reward, episode.won,
                                 len(episode.steps)))

    @property
    def visited_states(self) -> int:
        """Estados distintos con al menos un par (s,a) actualizado."""
        return len({state for state, _action in self.counts})

    @property
    def visited_pairs(self) -> int:
        """Pares (s,a) realmente actualizados por episodios completos."""
        return len(self.counts)

    def deterministic_policy(self) -> dict[GameState, Action]:
        # La evaluación greedy jamás selecciona al azar; desempate estable.
        seen_states = {s for s, _ in self.counts}
        return {
            s: max(self.world.actions(s), key=lambda action: self.q[(s, action)])
            for s in seen_states
        }
