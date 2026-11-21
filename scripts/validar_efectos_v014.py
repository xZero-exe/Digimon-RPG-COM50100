"""Renderiza los diez efectos reales y prueba su integración sin modificar el MDP."""
from __future__ import annotations
import argparse
from dataclasses import replace
import json
import os
from pathlib import Path
import platform
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--headless',action='store_true')
    parser.add_argument('--output',type=Path,default=ROOT/'resultados/efectos_v014')
    parser.add_argument('--gif',action='store_true',help='Exportar vista previa; requiere Pillow opcional')
    args=parser.parse_args()
    if args.headless:os.environ['SDL_VIDEODRIVER']='dummy'
    os.environ.setdefault('SDL_AUDIODRIVER','dummy')
    import pygame
    from digimon_rl.gui.app import RPGApp
    from digimon_rl.combat_visuals import CombatAnimation,SIGNATURE_EFFECTS as ALL_EFFECTS,ENEMY_EFFECTS
    from digimon_rl.domain import Action,Ending,GameState,Step,Zone
    from digimon_rl.environment import DigitalWorld
    from digimon_rl.presentation import Screen
    from digimon_rl.session import AdventureController,ControlMode,TurnReport
    args.output.mkdir(parents=True,exist_ok=True)
    report={'platform':platform.platform(),'headless':args.headless,'pygame':pygame.version.ver,
            'checks':[],'screenshots':[],'status':'FAIL'}
    world=DigitalWorld()
    app=RPGApp(AdventureController(world,{},{}),asset_root=ROOT/'assets')
    thumbs=[];gif_frames=[]
    try:
        app.initialize((1280,820));app._new_adventure(ControlMode.MANUAL);app.notice_ticks=0
        original_text=app._text
        def checked(value,x,y,*,font=None,color=(232,243,250),center=False):
            rect=(font or app.body).render(str(value),True,color).get_rect()
            if center:rect.center=(x,y)
            else:rect.topleft=(x,y)
            assert pygame.Rect(0,0,1280,820).contains(rect),(value,rect)
            original_text(value,x,y,font=font,color=color,center=center)
        app._text=checked
        for index,name in enumerate(ALL_EFFECTS):
            frames=app.effects.frames(name,128)
            assert len(frames)==4,name
            for frame in frames:
                assert frame.get_bounding_rect().width>0
                assert frame.get_at((0,0)).a==0,(name,'transparencia')
            if index<4:
                zone=Zone.FOREST if index<2 else Zone.FORTRESS
                state=GameState(zone,6,6,world.ENEMY_HP[zone],index,True,False)
                action=Action.TECHNIQUE
                outcome=next(t for t in world.transitions(state,action)
                    if t.next_state==Ending.WIN or isinstance(t.next_state,GameState) and t.next_state.enemy_hp<state.enemy_hp)
                offset=0
            else:
                zone=next(z for z,effect in ENEMY_EFFECTS.items() if effect==name)
                state=GameState(zone,6,6,world.ENEMY_HP[zone],0,True,True)
                action=Action.GUARD
                outcome=next(t for t in world.transitions(state,action)
                    if isinstance(t.next_state,GameState) and t.next_state.hp<6)
                offset=640
            step=Step(state,action,outcome.reward,outcome.next_state)
            app.controller.state=outcome.next_state
            app.controller.last_report=TurnReport(step,"Vista previa de habilidad",1,outcome.reward,isinstance(outcome.next_state,Ending))
            app.controller.turn=1
            app.controller.reward=outcome.reward
            app.controller.visited_zones={state.zone}
            sequence=CombatAnimation.from_step(step)
            app.combat_animation=sequence
            app.presentation.screen=Screen.GAME
            for i,ms in enumerate((80,240,400,560)):
                sequence.elapsed_ms=offset+ms
                app.draw()
                file=f'combate_{name}_{i}.png'
                pygame.image.save(app.screen,str(args.output/file));report['screenshots'].append(file)
            app._command('effects');app.effect_index=index;app.effect_elapsed=650
            app.draw();file='galeria_'+name+'.png'
            pygame.image.save(app.screen,str(args.output/file));report['screenshots'].append(file)
            thumbs.append((name,pygame.transform.smoothscale(app.screen,(480,308))))
            if args.gif:
                from PIL import Image
                for ms in range(0,1600,100):
                    app.effect_elapsed=ms;app.draw()
                    small=pygame.transform.smoothscale(app.screen,(768,492))
                    gif_frames.append(Image.frombytes('RGB',small.get_size(),pygame.image.tostring(small,'RGB')))
            app._command('back')
        report['checks'].append('10 atlas transparentes, 4 frames cada uno y 50 capturas de juego/galería')
        # Un turno resuelto no se repite si el usuario pulsa durante la animación.
        app._new_adventure(ControlMode.MANUAL);app.notice_ticks=0
        app.controller.state=GameState(Zone.FOREST,6,6,2,0,True)
        app._command('action',Action.TECHNIQUE)
        state,turn,rng=app.controller.state,app.controller.turn,app.controller.rng.getstate()
        assert app.animation_busy
        app._command('action',app.controller.legal_actions[0])
        assert (app.controller.state,app.controller.turn)==(state,turn)
        app._on_key(pygame.K_F6)
        assert app.presentation.screen==Screen.EFFECTS
        app._on_key(pygame.K_RIGHT)
        app._on_key(pygame.K_ESCAPE)
        assert app.presentation.screen==Screen.GAME
        app._on_key(pygame.K_SPACE)
        assert not app.animation_busy
        assert (app.controller.state,app.controller.turn)==(state,turn)
        assert app.controller.rng.getstate()==rng
        report['checks'].append('Bloqueo de turnos, F6, retorno y omisión sin consumir turno ni RNG')
        # Los frames y la galería no cambian ninguna variable del controlador.
        for frame in range(4):
            app.draw();app._present_frame()
        assert app.controller.rng.getstate()==rng
        sheet=pygame.Surface((960,5*336));sheet.fill((12,18,35))
        for i,(name,thumb) in enumerate(thumbs):
            x,y=(i%2)*480,(i//2)*336
            sheet.blit(app.small.render(name,True,(232,243,250)),(x+8,y+4));sheet.blit(thumb,(x,y+26))
        pygame.image.save(sheet,str(args.output/'contacto.png'))
        if gif_frames:
            gif_frames[0].save(args.output/'Vista_Previa_Habilidades_v014.gif',save_all=True,
                append_images=gif_frames[1:],duration=100,loop=0,optimize=True)
        report['status']='PASS'
    except Exception as exc:
        report['error']=repr(exc)
        raise
    finally:
        (args.output/'validacion.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
        pygame.quit()
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
