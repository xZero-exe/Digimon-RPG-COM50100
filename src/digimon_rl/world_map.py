"""Proyección de la aventura para el mapa; no introduce estados ni acciones MDP."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable
from .domain import Action, GameState, Zone

MAP_POSITIONS = {
    Zone.VILLAGE:(115,345), Zone.FOREST:(245,245), Zone.CAVE:(245,445),
    Zone.REFUGE:(350,345), Zone.SWAMP:(485,345), Zone.RUINS:(535,245),
    Zone.TOWER:(535,445), Zone.ABYSS:(695,445), Zone.FORTRESS:(695,320),
}

# Los caminos visibles corresponden a las catorce conexiones del motor existente.
# Buscar recursos también avanza, pero se elige expresamente en el panel de acciones.
MAP_ROUTES = (
    (Zone.FOREST,Zone.REFUGE,Action.ROUTE_REFUGE),
    (Zone.CAVE,Zone.REFUGE,Action.ROUTE_REFUGE),
    (Zone.REFUGE,Zone.SWAMP,Action.ADVANCE),
    (Zone.RUINS,Zone.ABYSS,Action.ROUTE_ABYSS),
    (Zone.TOWER,Zone.ABYSS,Action.ROUTE_ABYSS),
    (Zone.ABYSS,Zone.FORTRESS,Action.ADVANCE),
    (Zone.VILLAGE,Zone.FOREST,Action.ROUTE_FOREST),
    (Zone.VILLAGE,Zone.CAVE,Action.ROUTE_CAVE),
    (Zone.FOREST,Zone.SWAMP,Action.ADVANCE),
    (Zone.CAVE,Zone.SWAMP,Action.ADVANCE),
    (Zone.SWAMP,Zone.RUINS,Action.ADVANCE),
    (Zone.SWAMP,Zone.TOWER,Action.ROUTE_TOWER),
    (Zone.RUINS,Zone.FORTRESS,Action.ADVANCE),
    (Zone.TOWER,Zone.FORTRESS,Action.ADVANCE),
)
MAP_EDGES = frozenset((a,b) for a,b,_ in MAP_ROUTES)

MAP_LABELS = {
    Zone.REFUGE:'REFUGIO', Zone.ABYSS:'ABISMO',
    Zone.VILLAGE:'ALDEA', Zone.FOREST:'BOSQUE', Zone.CAVE:'CAVERNA',
    Zone.SWAMP:'PANTANO', Zone.RUINS:'RUINAS', Zone.TOWER:'TORRE',
    Zone.FORTRESS:'FORTALEZA',
}

MAP_DESCRIPTIONS = {
    Zone.REFUGE:'Desvío seguro: +2 PS, +1 EN y poción. Cuesta un viaje extra; conduce al Pantano.',
    Zone.ABYSS:'Guardromon: 6 PS, armadura 2; vulnerable al cargar. Botín: núcleo y +2 EN.',
    Zone.VILLAGE:'Aldea Digital · inicio de la aventura.',
    Zone.FOREST:'Bosque Binario · ruta inicial sin emboscada; Betamon.',
    Zone.CAVE:'Caverna Digital · energía adicional y riesgo de emboscada; Goblimon.',
    Zone.SWAMP:'Pantano de Datos · Ogremon; bifurcación hacia Ruinas o Torre.',
    Zone.RUINS:'Ruinas Antiguas · Devimon custodia el acceso a la fortaleza.',
    Zone.TOWER:'Torre de Datos · Andromon: armadura 1, vulnerable al cargar; recursos y acceso al Abismo.',
    Zone.FORTRESS:'Fortaleza Virus · Piedmon, el guardián final.',
}


@dataclass(frozen=True)
class MapDestination:
    zone: Zone
    action: Action


@dataclass(frozen=True)
class WorldMapView:
    current: Zone
    visited: frozenset[Zone]
    cleared: frozenset[Zone]
    traveled: frozenset[tuple[Zone,Zone]]
    destinations: tuple[MapDestination,...]
    can_choose: bool

    @classmethod
    def build(cls, state: GameState, history: Iterable[GameState],
              visited: Iterable[Zone], legal_actions: Iterable[Action],
              *, can_choose: bool) -> WorldMapView:
        states = tuple(history)
        legal = frozenset(legal_actions)
        traveled = frozenset((a.zone,b.zone) for a,b in zip(states,states[1:])
                            if (a.zone,b.zone) in MAP_EDGES)
        cleared = frozenset(s.zone for s in (*states,state) if s.enemy_hp == 0)
        destinations = tuple(MapDestination(b,action) for a,b,action in MAP_ROUTES
                             if a == state.zone and action in legal)
        return cls(state.zone,frozenset(visited)|{state.zone},cleared,traveled,destinations,can_choose)

    def route_to(self, zone: Zone) -> MapDestination | None:
        return next((d for d in self.destinations if d.zone == zone),None)

    def status(self, zone: Zone) -> str:
        if zone == self.current:
            return 'ACTUAL'
        if self.route_to(zone):
            return 'ELEGIR RUTA' if self.can_choose else 'RUTA POSIBLE'
        if zone in self.cleared:
            return 'DESPEJADA'
        return 'VISITADA' if zone in self.visited else 'SIN VISITAR'
