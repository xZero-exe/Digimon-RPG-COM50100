"""Narrativa y estados de interfaz del RPG, sin dependencia de Pygame.

Separa las pantallas y descripciones visuales del MDP. No altera recompensas
ni probabilidades. Puede probarse con unittest, incluso sin Pygame instalado.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .domain import Action, Ending, GameState, State, Zone
from .session import ControlMode, ENEMIES


class Screen(str, Enum):
    TITLE = "inicio"
    GAME = "juego"
    HELP = "ayuda"
    CREDITS = "creditos"
    PAUSE = "pausa"
    ANALYSIS = "analisis"
    RESULTS = "resultados"
    EFFECTS = "efectos"
    DEMO = "demostracion"
    DIGIDEX = "digidex"
    SUMMARY = "resumen_aventura"


@dataclass(frozen=True, slots=True)
class StoryBeat:
    title: str
    description: str
    accent: str = "cyan"


STORY: dict[Zone, StoryBeat] = {
    Zone.REFUGE: StoryBeat("REFUGIO DE CRISTAL", "El desvío restaura 2 PS, 1 EN y tu poción. Continúa al Pantano.", "green"),
    Zone.ABYSS: StoryBeat("ABISMO CORRUPTO", "Armadura 2, vulnerable al cargar. Vencer al guardián da núcleo y 2 EN.", "purple"),
    Zone.VILLAGE: StoryBeat(
        "LA LLAMADA DEL MUNDO DIGITAL",
        "Una corrupcion amenaza el mundo. Agumon debe encontrar la fortaleza virus.",
    ),
    Zone.FOREST: StoryBeat(
        "BOSQUE BINARIO",
        "Los datos se alteran entre los arboles. Betamon bloquea el sendero.", "green",
    ),
    Zone.CAVE: StoryBeat(
        "CAVERNA DIGITAL",
        "Una ruta arriesgada de mayor poder. Goblimon protege la entrada.", "gold",
    ),
    Zone.SWAMP: StoryBeat(
        "PANTANO DE DATOS",
        "Ogremon emerge de un terreno inestable. Administra bien tus recursos.", "green",
    ),
    Zone.RUINS: StoryBeat(
        "RUINAS ANTIGUAS",
        "Devimon custodia el camino a la fuente de la corrupcion.", "purple",
    ),
    Zone.TOWER: StoryBeat(
        "TORRE DE DATOS",
        "Andromon vigila los servidores. Más riesgo a cambio de un núcleo de energía.", "gold",
    ),
    Zone.FORTRESS: StoryBeat(
        "FORTALEZA VIRUS",
        "Piedmon tiene 9 PS. WarGreymon cuesta 2 EN y resiste mejor sus golpes.", "red",
    ),
}


MODE_DESCRIPTIONS: dict[ControlMode, str] = {
    ControlMode.DYNAMIC_PROGRAMMING: "La politica calcula la mejor accion usando un modelo del MDP.",
    ControlMode.MONTE_CARLO: "La politica aprende a partir de aventuras simuladas.",
    ControlMode.MANUAL: "Tu eliges las acciones legales y vives la aventura.",
}


class GamePresentation:
    """Máquina de pantallas y avisos narrativos, independiente del videojuego."""

    def __init__(self) -> None:
        self.screen = Screen.TITLE
        self.return_screen = Screen.TITLE
        self.notice: StoryBeat | None = None

    def start(self, mode: ControlMode) -> StoryBeat:
        self.screen = Screen.GAME
        self.notice = STORY[Zone.VILLAGE]
        return self.notice

    def open(self, screen: Screen) -> None:
        if screen not in (Screen.HELP, Screen.CREDITS, Screen.PAUSE, Screen.ANALYSIS, Screen.RESULTS, Screen.DEMO, Screen.EFFECTS, Screen.DIGIDEX, Screen.SUMMARY):
            raise ValueError("Pantalla auxiliar no valida")
        if screen == Screen.PAUSE and self.screen != Screen.GAME:
            return
        if self.screen in (Screen.HELP, Screen.CREDITS, Screen.PAUSE, Screen.ANALYSIS, Screen.RESULTS, Screen.DEMO, Screen.EFFECTS, Screen.DIGIDEX, Screen.SUMMARY):
            # Un diálogo a la vez; conserva el destino para volver.
            self.screen = screen
        else:
            self.return_screen = self.screen
            self.screen = screen

    def close(self) -> None:
        if self.screen in (Screen.HELP, Screen.CREDITS, Screen.PAUSE, Screen.ANALYSIS, Screen.RESULTS, Screen.DEMO, Screen.EFFECTS, Screen.DIGIDEX, Screen.SUMMARY):
            self.screen = self.return_screen

    def title(self) -> None:
        self.screen = Screen.TITLE
        self.return_screen = Screen.TITLE
        self.notice = None

    def on_transition(self, old_state: GameState, action: Action, new_state: State) -> StoryBeat | None:
        if isinstance(new_state, Ending):
            self.notice = StoryBeat(
                "MUNDO DIGITAL RESTAURADO" if new_state == Ending.WIN else "FIN DE LA AVENTURA",
                "La corrupcion ha sido derrotada." if new_state == Ending.WIN else
                "Agumon no pudo completar su mision.",
                "green" if new_state == Ending.WIN else "red",
            )
        elif old_state.zone != new_state.zone:
            self.notice = STORY[new_state.zone]
        elif old_state.evolved < new_state.evolved:
            self.notice = StoryBeat("DIGIEVOLUCION", f"¡{new_state.form_name} entra en combate!", "gold")
        elif not old_state.trained and new_state.trained:
            self.notice = StoryBeat(
                "HABILIDAD MEJORADA",
                "Entrenamiento completado: +1 de daño en ataques básicos y especiales.", "gold",
            )
        elif old_state.enemy_hp > 0 and new_state.enemy_hp == 0:
            enemy = ENEMIES.get(old_state.zone, "Enemigo")
            self.notice = StoryBeat("COMBATE SUPERADO", f"{enemy} fue derrotado. +1 XP; considera entrenar antes del jefe.", "green")
        else:
            self.notice = None
        return self.notice
