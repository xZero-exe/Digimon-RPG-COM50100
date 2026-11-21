"""Serialización versionada y validada de políticas del MDP (solo stdlib)."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Mapping

from .domain import Action, GameState, Zone
from .environment import DigitalWorld

FORMAT_VERSION = 6


def _state_to_list(state: GameState) -> list[int]:
    return [state.zone.value, state.hp, state.energy, state.enemy_hp,
            int(state.evolved), int(state.potion), int(state.enemy_charging), int(state.data_core),
            state.xp, int(state.trained)]


def save_policy(path: Path, policy: Mapping[GameState, Action], *,
                algorithm: str, gamma: float = 0.95, episodes: int | None = None,
                seed: int | None = None) -> None:
    """Guarda una política para reproducir decisiones sin reentrenar cada inicio."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = [(_state_to_list(state), action.value)
            for state, action in sorted(policy.items(), key=lambda item: tuple(_state_to_list(item[0])))]
    content = {
        "format_version": FORMAT_VERSION,
        "rules_version": DigitalWorld.RULES_VERSION,
        "algorithm": algorithm,
        "gamma": gamma,
        "episodes": episodes,
        "seed": seed,
        "state_definition": "zone,hp,energy,enemy_hp,evolution_level,potion,enemy_charging,data_core,xp,trained",
        "actions": rows,
    }
    path.write_text(json.dumps(content, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")


def load_policy(path: Path, world: DigitalWorld) -> dict[GameState, Action]:
    """Valida dominios y acciones legales antes de usar una política persistida."""
    content = json.loads(Path(path).read_text(encoding="utf-8"))
    if content.get("format_version") != FORMAT_VERSION:
        raise ValueError("Formato de política incompatible")
    if content.get("rules_version") != DigitalWorld.RULES_VERSION:
        raise ValueError("Reglas del MDP incompatibles: vuelve a entrenar")
    if content.get("state_definition") != "zone,hp,energy,enemy_hp,evolution_level,potion,enemy_charging,data_core,xp,trained":
        raise ValueError("Representación de estado incompatible")
    if not isinstance(content.get("actions"), list):
        raise ValueError("La política no contiene acciones")
    result: dict[GameState, Action] = {}
    for raw, raw_action in content["actions"]:
        if len(raw) != 10 or any(type(x) is not int for x in raw):
            raise ValueError("Estado inválido en la política")
        zone, hp, energy, enemy_hp, evolved, potion, charging, data_core, xp, trained = raw
        if not (1 <= hp <= world.MAX_HP and 0 <= energy <= world.MAX_ENERGY
                and 0 <= enemy_hp <= world.MAX_ENEMY_HP and evolved in range(4)
                and potion in (0, 1) and charging in (0, 1) and data_core in (0, 1)
                and (enemy_hp > 0 or charging == 0)
                and 0 <= xp <= world.MAX_XP and trained in (0, 1)): 
            raise ValueError("Valores fuera del dominio del estado")
        state = GameState(Zone(zone), hp, energy, enemy_hp, evolved, bool(potion),
                          bool(charging), bool(data_core), xp, bool(trained))
        action = Action(raw_action)
        if action not in world.actions(state) or state in result:
            raise ValueError("Acción ilegal o estado duplicado en política")
        result[state] = action
    if not result:
        raise ValueError("Política vacía")
    return result
