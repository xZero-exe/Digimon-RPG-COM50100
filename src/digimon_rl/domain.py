"""Entidades inmutables del juego y vocabulario del MDP."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Zone(Enum):
    VILLAGE = 0
    FOREST = 1
    CAVE = 2
    SWAMP = 3
    RUINS = 4
    TOWER = 5
    FORTRESS = 6
    REFUGE = 7
    ABYSS = 8

    @property
    def label(self) -> str:
        return {
            Zone.VILLAGE: "Aldea Digital",
            Zone.FOREST: "Bosque Binario",
            Zone.CAVE: "Caverna Digital",
            Zone.SWAMP: "Pantano de Datos",
            Zone.RUINS: "Ruinas Antiguas",
            Zone.TOWER: "Torre de Datos",
            Zone.FORTRESS: "Fortaleza Virus",
            Zone.REFUGE: "Refugio de Cristal",
            Zone.ABYSS: "Abismo Corrupto",
        }[self]


class Action(str, Enum):
    ROUTE_REFUGE = "ruta_refugio"
    ROUTE_ABYSS = "ruta_abismo"
    ROUTE_FOREST = "ruta_bosque"
    ROUTE_CAVE = "ruta_caverna"
    ADVANCE = "avanzar"
    SCAVENGE = "buscar_recursos"
    ROUTE_TOWER = "ruta_torre"
    ATTACK = "atacar"
    POWER_ATTACK = "ataque_especial"
    TECHNIQUE = "tecnica_digimon"
    GUARD = "defender"
    HEAL = "usar_pocion"
    DIGIVOLVE = "digievolucionar"
    INTERRUPT = "interrumpir"
    TRAIN = "entrenar_habilidad"


class Ending(str, Enum):
    WIN = "victoria"
    LOSS = "derrota"


@dataclass(frozen=True, slots=True)
class GameState:
    zone: Zone
    hp: int
    energy: int
    enemy_hp: int
    evolved: int  # 0 Agumon, 1 Greymon, 2 MetalGreymon, 3 WarGreymon
    potion: bool
    enemy_charging: bool = False  # Ataque anunciado: fase visible del enemigo
    data_core: bool = False  # Núcleo obtenido en una exploración de riesgo
    xp: int = 0  # Experiencia acumulada, 0..2
    trained: bool = False  # Mejora permanente del ataque básico/especial

    @property
    def form_name(self) -> str:
        return ("Agumon", "Greymon", "MetalGreymon", "WarGreymon")[int(self.evolved)]


State = GameState | Ending


@dataclass(frozen=True, slots=True)
class Transition:
    probability: float
    next_state: State
    reward: float


@dataclass(frozen=True, slots=True)
class Step:
    state: GameState
    action: Action
    reward: float
    next_state: State


@dataclass(frozen=True, slots=True)
class Episode:
    steps: tuple[Step, ...]
    final_state: State
    total_reward: float
    discounted_return: float
    truncated: bool

    @property
    def won(self) -> bool:
        return self.final_state == Ending.WIN
