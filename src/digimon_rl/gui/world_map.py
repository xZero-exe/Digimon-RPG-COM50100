"""Paisaje, caminos y marcadores del mapa. Solo dibuja una WorldMapView."""
from __future__ import annotations

from dataclasses import dataclass
import math
import pygame
from ..assets_catalog import ENEMY_SPRITES, HERO_SPRITES
from ..domain import Action, GameState, Zone
from ..world_map import MAP_LABELS, MAP_DESCRIPTIONS, MAP_POSITIONS, MAP_EDGES, WorldMapView

MAP_RECT = (44,194,724,337)
INK = (8,20,31)
WHITE = (232,243,250)
MUTED = (165,184,198)
CYAN = (87,226,229)
GOLD = (255,192,96)
GREEN = (107,219,162)

ROAD_POINTS = {edge:(MAP_POSITIONS[edge[0]],MAP_POSITIONS[edge[1]]) for edge in sorted(MAP_EDGES,key=lambda e:(e[0].value,e[1].value))}


@dataclass(frozen=True)
class MapHotspot:
    zone: Zone
    rect: pygame.Rect
    tooltip: str
    action: Action | None = None


class WorldMapRenderer:
    """El arte no contiene rutas: toda la topología sale de constantes verificables."""

    def __init__(self):
        self._shade = None

    @staticmethod
    def _point_on_road(points, progress):
        lengths = [math.dist(a,b) for a,b in zip(points,points[1:])]
        distance = sum(lengths)*progress
        for a,b,length in zip(points,points[1:],lengths):
            if distance <= length:
                f = distance/length
                return round(a[0]+(b[0]-a[0])*f),round(a[1]+(b[1]-a[1])*f)
            distance -= length
        return points[-1]

    def draw(self, app, state: GameState, view: WorldMapView) -> tuple[MapHotspot,...]:
        screen = app.screen
        rect = pygame.Rect(MAP_RECT)
        image = app.sprites.world_map(rect.size)
        if image is not None:
            screen.blit(image,rect.topleft)
        else:
            screen.fill((25,54,65),rect)
            for x in range(rect.left+12,rect.right,30):
                for y in range(rect.top+12,rect.bottom,30):
                    pygame.draw.circle(screen,(46,81,88),(x,y),1)
        if self._shade is None:
            self._shade = pygame.Surface(rect.size,pygame.SRCALPHA)
            self._shade.fill((6,20,32,26))
        screen.blit(self._shade,rect.topleft)
        pygame.draw.rect(screen,(75,111,125),rect,2,border_radius=10)
        frame = app.frames if app.animation_speed else 0
        for edge,points in ROAD_POINTS.items():
            destination = view.route_to(edge[1]) if edge[0] == view.current else None
            traveled = edge in view.traveled
            color = CYAN if destination else GOLD if traveled else (99,128,137)
            pygame.draw.lines(screen,INK,False,points,8)
            pygame.draw.lines(screen,color,False,points,4 if traveled or destination else 2)
            if destination and view.can_choose:
                dot = self._point_on_road(points,(frame%75)/75)
                pygame.draw.circle(screen,INK,dot,5)
                pygame.draw.circle(screen,WHITE,dot,2)
        hotspots = []
        for zone,pos in MAP_POSITIONS.items():
            x,y = pos
            current = zone == view.current
            destination = view.route_to(zone)
            visited = zone in view.visited
            accent = CYAN if current or destination else GREEN if zone in view.cleared else MUTED
            card = pygame.Rect(x-62,y+32,124,40)
            card.clamp_ip(rect.inflate(-10,-10))
            hit = card.union(pygame.Rect(x-28,y-28,56,56))
            hover = hit.collidepoint(app.last_mouse)
            if current:
                pulse = round(33+2*math.sin(frame/9))
                pygame.draw.circle(screen,INK,pos,pulse+3)
                pygame.draw.circle(screen,CYAN,pos,pulse,2)
                pygame.draw.polygon(screen,CYAN,((x-5,y-43),(x+5,y-43),(x,y-36)))
            pygame.draw.circle(screen,INK,pos,27)
            pygame.draw.circle(screen,accent if visited or destination else (101,121,132),pos,25,2)
            name = HERO_SPRITES[state.evolved] if current else (
                HERO_SPRITES[0] if zone == Zone.VILLAGE else ENEMY_SPRITES.get(zone, ""))
            icon = app.sprites.sprite(name,(41,41))
            if icon is not None:
                if not current and not visited and not destination:
                    icon = icon.copy(); icon.set_alpha(185)
                screen.blit(icon,icon.get_rect(center=pos))
            elif zone == Zone.REFUGE:
                pygame.draw.polygon(screen,CYAN,((x,y-19),(x+11,y),(x,y+19),(x-11,y)))
            else:
                app._text(MAP_LABELS[zone][0],x,y,font=app.subtitle,color=accent,center=True)
            if zone in view.cleared and not current:
                pygame.draw.circle(screen,INK,(x+21,y-21),9)
                pygame.draw.circle(screen,GREEN,(x+21,y-21),7)
                pygame.draw.lines(screen,INK,False,((x+17,y-21),(x+20,y-18),(x+25,y-24)),2)
            label_bg = pygame.Surface(card.size,pygame.SRCALPHA)
            pygame.draw.rect(label_bg,(7,19,31,227),label_bg.get_rect(),border_radius=5)
            pygame.draw.rect(label_bg,(*accent,230 if hover else 115),label_bg.get_rect(),1,border_radius=5)
            screen.blit(label_bg,card.topleft)
            app._text(MAP_LABELS[zone],card.centerx,card.y+10,
                      font=app._fit_font(MAP_LABELS[zone],app.small,110),color=WHITE,center=True)
            status = view.status(zone)
            app._text(status,card.centerx,card.y+28,
                      font=app._fit_font(status,app.tiny,110),color=accent,center=True)
            tip = MAP_DESCRIPTIONS[zone]
            action = destination.action if destination and view.can_choose else None
            if action is not None:
                tip = ('Avanzar · ' if action == Action.ADVANCE else 'Elegir ruta · ')+tip
            hotspots.append(MapHotspot(zone,hit,tip,action))
        for x,color,label in ((58,CYAN,'Actual'),(217,GOLD,'Recorrido'),
                              (393,CYAN,'Ruta posible'),(587,MUTED,'Sin visitar')):
            if label == 'Actual':
                pygame.draw.circle(screen,color,(x,551),5,2)
            else:
                pygame.draw.line(screen,color,(x-5,551),(x+7,551),3)
            app._text(label,x+14,542,font=app.tiny,color=MUTED)
        return tuple(hotspots)
