"""Controlador del videojuego: conecta una política con el mismo MDP del entrenamiento.

Sin dependencias gráficas. Los tests verifican aquí las reglas que usa Pygame.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from random import Random
from typing import Mapping

from .domain import Action, Ending, GameState, State, Step, Zone
from .environment import DigitalWorld
from .techniques import technique_for


class ControlMode(str, Enum):
    DYNAMIC_PROGRAMMING = "dp"
    MONTE_CARLO = "mc"
    MANUAL = "manual"


ACTION_LABELS: dict[Action, str] = {
    Action.ROUTE_FOREST: "Ir al bosque",
    Action.ROUTE_CAVE: "Ir a la caverna",
    Action.ADVANCE: "Avanzar",
    Action.SCAVENGE: "Buscar recursos",
    Action.ROUTE_TOWER: "Torre de Datos",
    Action.ATTACK: "Atacar",
    Action.POWER_ATTACK: "Ataque especial",
    Action.TECHNIQUE: "Técnica Digimon",
    Action.GUARD: "Defender",
    Action.HEAL: "Usar poción",
    Action.DIGIVOLVE: "Digievolucionar",
    Action.INTERRUPT: "Interrumpir",
    Action.TRAIN: "Mejorar ataque",
}

ENEMIES = {
    Zone.FOREST: "Betamon",
    Zone.CAVE: "Goblimon",
    Zone.SWAMP: "Ogremon",
    Zone.RUINS: "Devimon",
    Zone.TOWER: "Andromon",
    Zone.FORTRESS: "Piedmon",
}

# Se anuncia una intención, no una tirada oculta. Parte visible del estado MDP.
ENEMY_SKILLS = {
    Zone.FOREST: "Burbujas acidas",
    Zone.CAVE: "Emboscada de garras",
    Zone.SWAMP: "Garrote salvaje",
    Zone.RUINS: "Tornado oscuro",
    Zone.TOWER: "Láser digital",
    Zone.FORTRESS: "Cartas del caos",
}


@dataclass(frozen=True)
class TurnReport:
    step: Step
    message: str
    turn: int
    cumulative_reward: float
    finished: bool


class AdventureController:
    """Orquesta turnos; nunca redefine transiciones ni recompensas del MDP."""

    def __init__(
        self,
        world: DigitalWorld,
        dp_policy: Mapping[GameState, Action],
        mc_policy: Mapping[GameState, Action],
        seed: int = 42,
        max_steps: int = 80,
    ) -> None:
        if max_steps < 1:
            raise ValueError("max_steps debe ser positivo")
        self.world = world
        self.policies = {
            ControlMode.DYNAMIC_PROGRAMMING: dict(dp_policy),
            ControlMode.MONTE_CARLO: dict(mc_policy),
        }
        self.seed = seed
        self.max_steps = max_steps
        self.mode = ControlMode.DYNAMIC_PROGRAMMING
        self.attempt = 0
        self.reset()

    def reset(self, mode: ControlMode | None = None) -> None:
        if mode is not None:
            self.mode = ControlMode(mode)
        self.rng = Random(self.seed + self.attempt)
        self.attempt += 1
        self.state: State = self.world.start_state()
        self.turn = 0
        self.reward = 0.0
        self.last_report: TurnReport | None = None
        self.history: list[str] = ["Nueva aventura: la Aldea Digital te espera."]
        self.visited_zones: set[Zone] = {Zone.VILLAGE}

    @property
    def finished(self) -> bool:
        return isinstance(self.state, Ending) or self.turn >= self.max_steps

    @property
    def outcome(self) -> str:
        if self.state == Ending.WIN:
            return "VICTORIA"
        if self.state == Ending.LOSS:
            return "DERROTA"
        if self.turn >= self.max_steps:
            return "LIMITE DE TURNOS"
        return "EN CURSO"

    @property
    def legal_actions(self) -> tuple[Action, ...]:
        return () if self.finished else self.world.actions(self.state)

    def selected_action(self) -> Action | None:
        """Política entrenada o None para decisiones manuales y episodios terminados."""
        if self.mode == ControlMode.MANUAL or self.finished:
            return None
        assert isinstance(self.state, GameState)
        actions = self.legal_actions
        suggested = self.policies[self.mode].get(self.state)
        return suggested if suggested in actions else actions[0]

    def advance(self, action: Action | None = None) -> TurnReport:
        if self.finished:
            raise RuntimeError("La aventura ya terminó; reinicia para seguir jugando")
        assert isinstance(self.state, GameState)
        if action is None:
            action = self.selected_action()
        if action is None:
            raise ValueError("El modo manual requiere una acción explícita")
        legal = self.legal_actions
        if action not in legal:
            raise ValueError(f"Acción ilegal {action} para {self.state}")
        previous = self.state
        transition = self.world.sample(self.world.transitions(previous, action), self.rng)
        self.state = transition.next_state
        if isinstance(self.state, GameState):
            self.visited_zones.add(self.state.zone)
        self.turn += 1
        self.reward += transition.reward
        step = Step(previous, action, transition.reward, transition.next_state)
        message = self._describe(step)
        if self.state == Ending.WIN:
            message += " ¡El Mundo Digital está a salvo!"
        elif self.state == Ending.LOSS:
            message += " Agumon fue derrotado."
        elif self.turn == self.max_steps:
            message += " Fin por límite de turnos."
        self.history.append(message)
        self.history = self.history[-12:]
        self.last_report = TurnReport(step, message, self.turn, self.reward, self.finished)
        return self.last_report

    @staticmethod
    def _describe(step: Step) -> str:
        before = step.state
        after = step.next_state
        label = (technique_for(int(before.evolved)).name if step.action == Action.TECHNIQUE
                 else ACTION_LABELS[step.action])
        if isinstance(after, Ending):
            return f"{label}: {'jefe vencido' if after == Ending.WIN else 'sin salud'} ({step.reward:+.0f})."
        if after.zone != before.zone:
            ambush = " (emboscada)" if after.hp < before.hp else ""
            core = " ¡Núcleo de datos conseguido!" if after.data_core and not before.data_core else ""
            return f"{label}: {after.zone.label}{ambush}{core} ({step.reward:+.0f})."
        if step.action == Action.DIGIVOLVE:
            return f"¡Digievolución a {after.form_name}! ({step.reward:+.0f})."
        if step.action == Action.INTERRUPT:
            stopped = after.enemy_hp < before.enemy_hp if isinstance(after, GameState) else after == Ending.WIN
            return ("¡Ataque cargado interrumpido!" if stopped else "Interrupción fallida") + f" ({step.reward:+.0f})."
        if step.action == Action.TRAIN:
            return (f"¡Entrenamiento completado! Ataques +1; XP {after.xp} "
                    f"({step.reward:+.0f}).")
        if step.action == Action.HEAL:
            return f"Poción consumida: {after.hp}/{DigitalWorld.MAX_HP} PS ({step.reward:+.0f})."
        if after.enemy_hp == 0 and before.enemy_hp > 0:
            return (f"{label}: enemigo derrotado, XP {after.xp}/{DigitalWorld.MAX_XP} "
                    f"({step.reward:+.0f}).")
        warning = (f" | {ENEMY_SKILLS.get(after.zone, 'Ataque')} en preparación!"
                   if after.enemy_charging else "")
        return f"{label}: recompensa {step.reward:+.0f}.{warning}"
