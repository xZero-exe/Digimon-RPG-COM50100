"""Inspector pedagógico de políticas del RPG.

No entrena agentes ni modifica estados. DP calcula Q(s,a) usando el modelo
conocido y V*(s); MC muestra SOLO estimaciones aprendidas por first-visit.
Las entradas sin visita NO son Q=0: se marcan explícitamente como ausentes.
"""
from __future__ import annotations

from dataclasses import dataclass
import gzip
import hashlib
import json
from pathlib import Path
from typing import Mapping

from .domain import Action, Ending, GameState, Zone
from .environment import DigitalWorld
from .policy_io import _state_to_list
from .session import ACTION_LABELS

DATA_VERSION = 1


def _restore_state(raw: list[int]) -> GameState:
    if not isinstance(raw, list) or len(raw) != 10 or any(type(x) is not int for x in raw):
        raise ValueError("Estado del análisis inválido")
    zone, hp, energy, enemy_hp, evolved, potion, charge, core, xp, trained = raw
    return GameState(Zone(zone), hp, energy, enemy_hp, evolved,
                     bool(potion), bool(charge), bool(core), xp, bool(trained))


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def export_analysis(path: Path, dp_values: Mapping[GameState, float],
                    mc_q: Mapping[tuple[GameState, Action], float],
                    mc_counts: Mapping[tuple[GameState, Action], int],
                    dp_file: Path, mc_file: Path, *, episodes: int, gamma: float,
                    truncated: int = 0) -> None:
    """Exporta resultados auténticos, enlazados a las políticas por hash.

    No exportar cero por pares no visitados, porque NO son estimaciones MC.
    """
    if episodes < 1 or not (0 < gamma < 1):
        raise ValueError("Metadatos de entrenamiento inválidos")
    rows = [(_state_to_list(s), a.value, float(mc_q[(s, a)]), int(n))
            for (s, a), n in mc_counts.items() if n > 0]
    if any(not (-1e100 < q < 1e100) for _, _, q, _ in rows):
        raise ValueError("Q Monte Carlo no finito")
    data = {
        "format": DATA_VERSION,
        "method_dp": "value_iteration_Bellman",
        "method_mc": "on_policy_first_visit_epsilon_greedy",
        "gamma": gamma,
        "episodes": episodes,
        "truncated": truncated,
        "dp_sha256": _digest(dp_file),
        "mc_sha256": _digest(mc_file),
        "dp_values": [[_state_to_list(s), round(float(v), 10)] for s, v in dp_values.items()],
        "mc_samples": rows,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(path, "wt", encoding="utf-8", compresslevel=6) as fp:
        json.dump(data, fp, ensure_ascii=False, separators=(",", ":"))


@dataclass(frozen=True)
class ActionInsight:
    action: Action
    label: str
    dp_q: float | None
    mc_q: float | None
    mc_visits: int
    dp_recommended: bool
    mc_recommended: bool


@dataclass(frozen=True)
class StateInsight:
    state: GameState
    actions: tuple[ActionInsight, ...]
    dp_action: Action | None
    mc_action: Action | None
    dp_value: float | None
    learned_state: bool
    agrees: bool | None


class PolicyInspector:
    """Vista de solo lectura para explicar el porqué de decisiones existentes."""

    def __init__(self, world: DigitalWorld,
                 dp_policy: Mapping[GameState, Action],
                 mc_policy: Mapping[GameState, Action],
                 dp_values: Mapping[GameState, float] | None = None,
                 mc_q: Mapping[tuple[GameState, Action], float] | None = None,
                 mc_counts: Mapping[tuple[GameState, Action], int] | None = None,
                 *, gamma: float = .95, episodes: int | None = None):
        self.world = world
        self.dp_policy = dp_policy
        self.mc_policy = mc_policy
        self.dp_values = dict(dp_values or {})
        self.mc_q = dict(mc_q or {})
        self.mc_counts = dict(mc_counts or {})
        self.gamma = gamma
        self.episodes = episodes

    @classmethod
    def from_export(cls, world: DigitalWorld,
                    dp_policy: Mapping[GameState, Action],
                    mc_policy: Mapping[GameState, Action],
                    data_file: Path, dp_file: Path, mc_file: Path) -> "PolicyInspector":
        """Rechaza valores antiguos para evitar explicar una política incorrecta."""
        with gzip.open(data_file, "rt", encoding="utf-8") as fp:
            data = json.load(fp)
        if data.get("format") != DATA_VERSION:
            raise ValueError("Versión de análisis incompatible")
        if data.get("dp_sha256") != _digest(dp_file) or data.get("mc_sha256") != _digest(mc_file):
            raise ValueError("El análisis no corresponde a las políticas cargadas")
        dp_values = {_restore_state(s): float(v) for s, v in data["dp_values"]}
        q = {}
        counts = {}
        for raw, action, value, visits in data["mc_samples"]:
            key = (_restore_state(raw), Action(action))
            if visits <= 0 or key in counts:
                raise ValueError("Visitas Monte Carlo inválidas o duplicadas")
            q[key] = float(value)
            counts[key] = int(visits)
        return cls(world, dp_policy, mc_policy, dp_values, q, counts,
                   gamma=float(data["gamma"]), episodes=int(data["episodes"]))

    @property
    def coverage(self) -> float:
        return len(self.mc_policy) / len(self.dp_policy) if self.dp_policy else 0.0

    @property
    def visited_pairs(self) -> int:
        return len(self.mc_counts)

    def inspect(self, state: GameState) -> StateInsight:
        legal = self.world.actions(state)
        dp = self.dp_policy.get(state)
        mc = self.mc_policy.get(state)
        lines = []
        for a in legal:
            # Bellman: Q*(s,a) = sum_{s'} P(s',r|s,a) [r + gamma V*(s')].
            qdp = None
            if self.dp_values:
                total = 0.0
                missing = False
                for transition in self.world.transitions(state, a):
                    nxt = transition.next_state
                    if isinstance(nxt, Ending):
                        v = 0.0
                    elif nxt in self.dp_values:
                        v = self.dp_values[nxt]
                    else:
                        missing = True
                        break
                    total += transition.probability * (transition.reward + self.gamma * v)
                if not missing:
                    qdp = total
            key = (state, a)
            n = self.mc_counts.get(key, 0)
            lines.append(ActionInsight(a, ACTION_LABELS[a], qdp,
                                       self.mc_q[key] if n else None, n,
                                       a == dp, a == mc))
        return StateInsight(state, tuple(lines), dp, mc,
                            self.dp_values.get(state), state in self.mc_policy,
                            dp == mc if mc is not None and dp is not None else None)
