"""Revisa desvíos reales y captura sus escenarios sin entrenar políticas.

La ruta del Refugio se escoge manualmente tras un prefijo DP; el Abismo sigue DP.
Las capturas son evidencia de interfaz, no experimentos adicionales de aprendizaje.
"""
import argparse
from pathlib import Path
import json
import os
import platform
from random import Random
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--headless',action='store_true')
    p.add_argument('--output',type=Path,default=ROOT/'resultados/rutas_v021/interfaz');args=p.parse_args()
    if args.headless:os.environ['SDL_VIDEODRIVER']='dummy'
    os.environ.setdefault('SDL_AUDIODRIVER','dummy')
    import pygame
    from digimon_rl.domain import Action,GameState,Zone
    from digimon_rl.environment import DigitalWorld
    from digimon_rl.session import AdventureController,ControlMode
    from digimon_rl.policy_io import load_policy
    from digimon_rl.inspector import PolicyInspector
    from digimon_rl.academic_dashboard import AcademicDashboard
    from digimon_rl.gui.app import RPGApp
    from digimon_rl.presentation import Screen
    world=DigitalWorld();dp_file=ROOT/'politicas/dp.json';mc_file=ROOT/'politicas/mc.json'
    dp=load_policy(dp_file,world);mc=load_policy(mc_file,world)
    inspector=PolicyInspector.from_export(world,dp,mc,ROOT/'politicas/analisis_v010.json.gz',dp_file,mc_file)
    dashboard=AcademicDashboard.load(ROOT/'resultados/convergencia_v021')
    assert dashboard.rules_version==world.RULES_VERSION
    app=RPGApp(AdventureController(world,dp,mc),asset_root=ROOT/'assets',inspector=inspector,dashboard=dashboard)
    args.output.mkdir(parents=True,exist_ok=True)
    report={'platform':platform.platform(),'headless':args.headless,'rules_version':world.RULES_VERSION,'checks':[],'screenshots':[]}
    def fresh(seed):
        app.controller=AdventureController(world,dp,mc,seed=seed);app.presentation.screen=Screen.GAME
        app.inspection_history=[app.controller.state];app.notice_ticks=app.cue_ticks=0
    def step(action=None):
        app.controller.advance(action)
        if isinstance(app.controller.state,GameState):app.inspection_history.append(app.controller.state)
    def capture(name):
        state=app.controller.state;rng=app.controller.rng.getstate();turn=app.controller.turn
        app.draw();app._present_frame()
        assert app.controller.state==state and app.controller.rng.getstate()==rng and app.controller.turn==turn
        pygame.image.save(app.screen,str(args.output/(name+'.png')));report['screenshots'].append(name+'.png')
    try:
        app.initialize((1280,820))
        selected=None
        for seed in range(42,143):
            fresh(seed)
            while not app.controller.finished:
                s=app.controller.state
                if s.zone in (Zone.FOREST,Zone.CAVE) and s.enemy_hp==0:break
                step()
            if not app.controller.finished and app.controller.state.hp<=4:selected=seed;break
        assert selected is not None
        capture('01_antes_del_refugio');before=app.controller.state;turn=app.controller.turn
        app.controller.mode=ControlMode.MANUAL;step(Action.ROUTE_REFUGE)
        assert app.controller.turn==turn+1 and app.controller.state.zone==Zone.REFUGE
        assert app.controller.state.hp==min(6,before.hp+2)
        assert app.controller.state.energy==min(6,before.energy+1)
        assert app.controller.state.potion
        capture('02_refugio_de_cristal')
        report['refuge']={'seed':selected,'before_hp':before.hp,'after_hp':app.controller.state.hp,
                         'mode':'manual choice after DP prefix'}
        selected=None
        for seed in range(42,143):
            run=world.episode(lambda s,l,r:dp[s],Random(seed))
            if run.won and any(x.state.zone==Zone.ABYSS for x in run.steps):selected=seed;break
        assert selected is not None
        fresh(selected);seen=False;rewarded=False
        while not app.controller.finished:
            state=app.controller.state
            if state.zone==Zone.ABYSS and state.enemy_hp>0 and not seen:
                capture('03_guardromon');seen=True
            if state.zone==Zone.ABYSS and state.enemy_hp==0 and not rewarded:
                assert state.data_core;capture('04_botin_del_abismo');rewarded=True
            step()
        assert seen and rewarded and app.controller.outcome=='VICTORIA'
        report['abyss']={'seed':selected,'mode':'saved DP policy','outcome':app.controller.outcome,'turns':app.controller.turn}
        report['checks']=['legal_manual_refuge_detour','resource_caps','one_turn_per_route','real_dp_abyss_victory','guardromon_canonical_sprite','drawing_preserves_rng_and_state']
        report['status']='PASS'
    finally:pygame.quit()
    (args.output/'reporte.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
