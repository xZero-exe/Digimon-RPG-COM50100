"""Verifica el mapa ilustrado con Pygame real, ocho rutas y clics transformados.

--headless usa SDL dummy; no certifica Windows. No entrena agentes.
"""
from __future__ import annotations
import argparse
from dataclasses import replace
import json
import os
from pathlib import Path
import platform
from random import Random
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--headless',action='store_true')
    parser.add_argument('--output',type=Path,default=ROOT/'resultados/mapa_v017')
    args = parser.parse_args()
    if args.headless:
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
    os.environ.setdefault('SDL_AUDIODRIVER','dummy')
    import pygame
    from digimon_rl.domain import Action, Ending, GameState, Zone
    from digimon_rl.environment import DigitalWorld
    from digimon_rl.gui.app import RPGApp
    from digimon_rl.gui.layout import Viewport
    from digimon_rl.gui.sprites import SpriteManager
    from digimon_rl.gui.world_map import MAP_RECT, ROAD_POINTS
    from digimon_rl.policy_io import load_policy
    from digimon_rl.presentation import Screen, STORY
    from digimon_rl.session import AdventureController, ControlMode
    from digimon_rl.world_map import MAP_EDGES, MAP_ROUTES, MAP_POSITIONS

    world = DigitalWorld(); app = RPGApp(AdventureController(world,{},{}),asset_root=ROOT/'assets')
    args.output.mkdir(parents=True,exist_ok=True)
    report = {'status':'FAIL','platform':platform.platform(),'pygame':pygame.version.ver,
              'headless':args.headless,'checks':[],'screenshots':[],'routes':[]}
    bounds = pygame.Rect(0,0,1280,820)
    original_text = app._text

    def checked(value,x,y,*,font=None,color=(232,243,250),center=False):
        rect = (font or app.body).render(str(value),True,color).get_rect()
        if center:
            rect.center = (x,y)
        else:
            rect.topleft = (x,y)
        assert bounds.contains(rect),(value,rect)
        original_text(value,x,y,font=font,color=color,center=center)

    app._text = checked

    def snapshot():
        c = app.controller
        return c.state,c.turn,c.reward,c.rng.getstate(),tuple(c.history),frozenset(c.visited_zones)

    def map_buttons():
        return [b for b in app.buttons if b.command=='action' and b.rect.top<579]

    def draw():
        before = snapshot(); app.draw(); app._present_frame()
        assert before == snapshot(),'Dibujar modificó el episodio o su RNG'
        for i,a in enumerate(app.buttons):
            assert bounds.contains(a.rect),a
            assert all(not a.rect.colliderect(b.rect) for b in app.buttons[i+1:]),a

    def capture(name):
        draw(); app._draw_tooltip(); file = name+'.png'
        pygame.image.save(app.screen,str(args.output/file)); report['screenshots'].append(file)

    prefixes = {
        Zone.REFUGE:(Zone.VILLAGE,Zone.FOREST,Zone.REFUGE),
        Zone.ABYSS:(Zone.VILLAGE,Zone.FOREST,Zone.SWAMP,Zone.RUINS,Zone.ABYSS),
        Zone.VILLAGE:(Zone.VILLAGE,), Zone.FOREST:(Zone.VILLAGE,Zone.FOREST),
        Zone.CAVE:(Zone.VILLAGE,Zone.CAVE),
        Zone.SWAMP:(Zone.VILLAGE,Zone.FOREST,Zone.SWAMP),
        Zone.RUINS:(Zone.VILLAGE,Zone.FOREST,Zone.SWAMP,Zone.RUINS),
        Zone.TOWER:(Zone.VILLAGE,Zone.CAVE,Zone.SWAMP,Zone.TOWER),
        Zone.FORTRESS:(Zone.VILLAGE,Zone.FOREST,Zone.SWAMP,Zone.RUINS,Zone.FORTRESS),
    }

    def install(zone,*,enemy_hp=0,form=0,mode=ControlMode.MANUAL):
        # Casos de composición visual, sin convertirse en episodios de entrenamiento.
        app.controller.state = GameState(zone,6,3,enemy_hp,form,True)
        app.controller.mode = mode; app.controller.turn = 0; app.controller.reward = 0
        app.controller.last_report = None
        app.controller.history = ['Revisión gráfica del mapa.']
        app.controller.visited_zones = set(prefixes[zone])
        app.inspection_history = [replace(world.start_state(),zone=z) for z in prefixes[zone][:-1]]+[app.controller.state]
        app.presentation.screen = Screen.GAME
        app.combat_animation = None; app.notice_ticks = 0; app.cue_ticks = 0; app.fx_ticks = 0

    try:
        app.initialize((1280,820)); app._new_adventure(ControlMode.MANUAL)
        assert set(ROAD_POINTS)==MAP_EDGES
        for edge,points in ROAD_POINTS.items():
            assert points[0] == MAP_POSITIONS[edge[0]] and points[-1] == MAP_POSITIONS[edge[1]]
            assert all(pygame.Rect(MAP_RECT).collidepoint(p) for p in points)
        image = app.sprites.world_map(pygame.Rect(MAP_RECT).size)
        assert image is not None and image is app.sprites.world_map(pygame.Rect(MAP_RECT).size)
        capture('00_inicio_con_narracion')
        xbutton = next(b for b in app.buttons if b.command=='dismiss_notice')
        assert not xbutton.rect.colliderect(pygame.Rect(MAP_RECT))
        app.last_mouse=MAP_POSITIONS[Zone.CAVE]
        cave_tip=next(text for rect,text in app.tooltips if rect.collidepoint(app.last_mouse))
        assert 'riesgo de emboscada' in cave_tip and 'energía adicional' in cave_tip
        capture('informacion_riesgo_caverna'); app.last_mouse=(-1,-1)
        for zone in Zone:
            install(zone,enemy_hp=0 if zone in (Zone.VILLAGE,Zone.REFUGE) else world.ENEMY_HP[zone])
            capture(f'region_{zone.name.lower()}')
            if zone not in (Zone.VILLAGE,Zone.REFUGE):
                assert map_buttons()==[]
            install(zone); capture(f'despejada_{zone.name.lower()}')
        # Cada ruta del mapa debe consumir exactamente un muestreo del mismo motor.
        for source,destination,action in MAP_ROUTES:
            install(source); draw()
            expected_rng = Random(); expected_rng.setstate(app.controller.rng.getstate())
            expected = world.sample(world.transitions(app.controller.state,action),expected_rng)
            available = {b.value for b in map_buttons()}
            assert action in available
            app._on_click(MAP_POSITIONS[destination])
            assert app.controller.state == expected.next_state
            assert app.controller.turn==1 and app.controller.rng.getstate()==expected_rng.getstate()
            before = snapshot()
            # Segundo evento antes de volver a dibujar: el botón viejo ya no es legal.
            app._on_click(MAP_POSITIONS[destination])
            assert snapshot()==before
            capture('ruta_'+source.name.lower()+'_'+destination.name.lower())
            report['routes'].append({'source':source.name,'destination':destination.name,'action':action.value})
        for mode in (ControlMode.DYNAMIC_PROGRAMMING,ControlMode.MONTE_CARLO):
            install(Zone.VILLAGE,mode=mode); draw(); before=snapshot()
            assert map_buttons()==[]
            app._on_click(MAP_POSITIONS[Zone.FOREST]); assert snapshot()==before
            capture('solo_lectura_'+mode.value)
        # La ruta se abre al acabar la presentación del golpe final, no durante ella.
        install(Zone.FOREST,enemy_hp=1)
        while app.controller.state.enemy_hp > 0:
            app._advance(Action.ATTACK)
            if app.controller.state.enemy_hp > 0:
                app.combat_animation.finish()
        draw(); before=snapshot(); assert app.animation_busy and map_buttons()==[]
        app._on_click(MAP_POSITIONS[Zone.SWAMP]); assert snapshot()==before
        capture('combate_bloquea_rutas'); app.combat_animation.finish(); draw()
        assert {b.value for b in map_buttons()}=={Action.ADVANCE,Action.ROUTE_REFUGE}
        for form in range(4):
            install(Zone.FORTRESS,enemy_hp=6,form=form); capture(f'forma_{form}')
        # Todas las narraciones permanecen fuera del mapa y de los botones de decisión.
        for zone in Zone:
            install(zone); app.presentation.notice=STORY[zone]; app.notice_ticks=130
            capture('aviso_'+zone.name.lower())
        for size in ((1366,768),(1024,768),(800,600),(1920,1080)):
            app.window = pygame.display.set_mode(size,pygame.RESIZABLE); app.viewport=Viewport(*size)
            install(Zone.VILLAGE); capture(f'ventana_{size[0]}x{size[1]}')
            x,y=MAP_POSITIONS[Zone.CAVE]; ox,oy=app.viewport.origin; w,h=app.viewport.size
            pointer=(ox+round(x*w/1280),oy+round(y*h/820))
            app._on_click(app._pointer(pointer))
            assert isinstance(app.controller.state,GameState) and app.controller.state.zone==Zone.CAVE
            assert app.controller.turn==1
        app.window=pygame.display.set_mode((1280,820),pygame.RESIZABLE);app.viewport=Viewport(1280,820)
        with tempfile.TemporaryDirectory() as temp:
            manager = SpriteManager(Path(temp)); assert manager.world_map((724,337)) is None
            original = app.sprites.world_map
            app.sprites.world_map = manager.world_map
            install(Zone.VILLAGE); capture('respaldo_sin_imagen')
            assert {b.value for b in map_buttons()}=={Action.ROUTE_FOREST,Action.ROUTE_CAVE}
            app.sprites.world_map = original
        # La vista previa procede de una trayectoria real con acciones de la política DP.
        dp = load_policy(ROOT/'politicas/dp.json',world)
        app.controller = AdventureController(world,dp,{},seed=42)
        app._new_adventure(ControlMode.MANUAL); app.notice_ticks=0
        while isinstance(app.controller.state,GameState) and app.controller.turn<80:
            if app.controller.state.zone==Zone.SWAMP and app.controller.state.enemy_hp==0:
                break
            app._advance(dp.get(app.controller.state,app.controller.legal_actions[0]))
            if app.combat_animation:
                app.combat_animation.finish()
            app.notice_ticks=0
        assert isinstance(app.controller.state,GameState) and app.controller.state.zone==Zone.SWAMP
        assert app.controller.state.enemy_hp==0
        capture('Vista_Previa_Mapa_v017')
        view = app._map_view(app.controller.state)
        assert view.traveled == frozenset({(Zone.VILLAGE,Zone.FOREST),(Zone.FOREST,Zone.SWAMP)})
        assert {b.value for b in map_buttons()}=={Action.ADVANCE,Action.ROUTE_TOWER}
        report['preview']={'seed':42,'turns':app.controller.turn,'mode':'manual with saved DP actions',
                           'purpose':'GUI demonstration, not a new learning experiment'}
        report['checks']=['eight_paths_match_engine','map_asset_cached','all_regions_and_forms',
                          'each_click_matches_one_engine_sample','stale_double_click_ignored',
                          'agents_read_only','combat_animation_blocks_routes',
                          'narrative_leaves_map_visible','four_resolutions_and_route_clicks',
                          'fallback_remains_playable','render_preserves_episode_and_rng',
                          'ordered_history_drives_traveled_routes','no_overlapping_buttons']
        report['status']='PASS'
    except Exception as exc:
        report['error']=repr(exc)
        raise
    finally:
        (args.output/'validacion.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
        pygame.quit()
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':
    main()
