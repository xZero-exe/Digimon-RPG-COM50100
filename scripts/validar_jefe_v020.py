"""Captura un combate real de DP contra Piedmon, sin entrenar.

--headless usa SDL dummy y no certifica Windows ni un dispositivo de audio.
"""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import platform
from random import Random
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))


def main():
    raise SystemExit("Diagnóstico histórico: usa scripts/validar_jefe_v021.py con las reglas actuales.")
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--headless',action='store_true')
    p.add_argument('--output',type=Path,default=ROOT/'resultados/balance_v020/interfaz')
    args=p.parse_args()
    if args.headless:os.environ['SDL_VIDEODRIVER']='dummy'
    os.environ.setdefault('SDL_AUDIODRIVER','dummy')
    import pygame
    from digimon_rl.domain import GameState,Zone,Action
    from digimon_rl.environment import DigitalWorld
    from digimon_rl.policy_io import load_policy
    from digimon_rl.session import AdventureController
    from digimon_rl.gui.app import RPGApp
    from digimon_rl.presentation import Screen
    from digimon_rl.academic_dashboard import AcademicDashboard
    from digimon_rl.inspector import PolicyInspector
    world=DigitalWorld();dp_file=ROOT/'politicas/dp.json';mc_file=ROOT/'politicas/mc.json'
    dp=load_policy(dp_file,world);mc=load_policy(mc_file,world)
    seed=None
    for candidate in range(42,143):
        run=world.episode(lambda s,l,r:dp[s],Random(candidate))
        if run.won and any(step.state.evolved==3 for step in run.steps):seed=candidate;break
    assert seed is not None
    controller=AdventureController(world,dp,mc,seed=seed)
    inspector=PolicyInspector.from_export(world,dp,mc,ROOT/'politicas/analisis_v010.json.gz',dp_file,mc_file)
    dashboard=AcademicDashboard.load(ROOT/'resultados/convergencia_v020')
    app=RPGApp(controller,asset_root=ROOT/'assets',inspector=inspector,dashboard=dashboard)
    args.output.mkdir(parents=True,exist_ok=True)
    report={'platform':platform.platform(),'headless':args.headless,'seed':seed,'rules_version':world.RULES_VERSION,'screenshots':[],'checks':[]}
    try:
        app.initialize((1280,820));app.presentation.screen=Screen.GAME
        def capture(name):
            before=controller.rng.getstate();turn=controller.turn;state=controller.state
            app.draw();app._present_frame()
            assert controller.turn==turn and controller.state==state and controller.rng.getstate()==before
            pygame.image.save(app.screen,str(args.output/(name+'.png')))
            report['screenshots'].append(name+'.png')
        seen_metal=seen_war=False
        while not controller.finished:
            state=controller.state
            if isinstance(state,GameState) and state.zone==Zone.FORTRESS:
                if state.evolved==2 and not seen_metal:
                    assert state.enemy_hp==9
                    capture('piedmon_9ps');seen_metal=True
                if state.evolved==3 and not seen_war:
                    capture('wargreymon_vs_piedmon');seen_war=True
            controller.advance()
        assert seen_metal and seen_war and controller.outcome=='VICTORIA'
        capture('victoria')
        report['checks']=['real_dp_trajectory','boss_9hp_visible','wargreymon_seen','victory','drawing_preserves_rng_and_turns']
        report['outcome']=controller.outcome;report['turns']=controller.turn;report['status']='PASS'
    finally:pygame.quit()
    (args.output/'reporte.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
