"""Audita ataques básicos y galería completa usando Pygame real."""
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
    parser.add_argument('--output',type=Path,default=ROOT/'resultados/basicos_v0141')
    parser.add_argument('--gif',action='store_true')
    args=parser.parse_args()
    if args.headless:os.environ['SDL_VIDEODRIVER']='dummy'
    os.environ.setdefault('SDL_AUDIODRIVER','dummy')
    import pygame
    from digimon_rl.gui.app import RPGApp
    from digimon_rl.combat_visuals import CombatAnimation,ALL_EFFECTS,BASIC_EFFECTS
    from digimon_rl.domain import Action,Ending,GameState,Step,Zone
    from digimon_rl.environment import DigitalWorld
    from digimon_rl.presentation import Screen
    from digimon_rl.session import AdventureController,ControlMode,TurnReport
    args.output.mkdir(parents=True,exist_ok=True)
    app=RPGApp(AdventureController(DigitalWorld(),{},{}),asset_root=ROOT/'assets')
    result={'platform':platform.platform(),'headless':args.headless,'pygame':pygame.version.ver,
            'status':'FAIL','screenshots':[],'cases':[]}
    frames=[]
    try:
        app.initialize((1280,820));app._new_adventure(ControlMode.MANUAL)
        app.notice_ticks=0
        original_frame=app.effects.frame
        requests=[]
        def tracked(name,index,size=144,mirror=False):
            image=original_frame(name,index,size,mirror)
            assert image is not None,('No se pudo cargar el PNG',name,index)
            requests.append(name)
            return image
        app.effects.frame=tracked
        original_text=app._text
        def checked(value,x,y,*,font=None,color=(232,243,250),center=False):
            rect=(font or app.body).render(str(value),True,color).get_rect()
            if center:rect.center=(x,y)
            else:rect.topleft=(x,y)
            assert pygame.Rect(0,0,1280,820).contains(rect),(value,rect)
            original_text(value,x,y,font=font,color=color,center=center)
        app._text=checked
        for name in ALL_EFFECTS:
            atlas=app.effects.frames(name)
            assert len(atlas)==4
            for frame in atlas:
                assert frame.get_at((0,0)).a==0
                assert frame.get_bounding_rect().width>0
        for action,name in BASIC_EFFECTS.items():
            for form in range(4):
                # Escenarios de revisión gráfica; no son nuevos episodios de entrenamiento.
                state=GameState(Zone.FOREST,6,6,2,form,True,True)
                outcomes=app.controller.world.transitions(state,action)
                outcome=next(t for t in outcomes if isinstance(t.next_state,GameState) and t.next_state.enemy_hp<2)
                step=Step(state,action,outcome.reward,outcome.next_state)
                seq=CombatAnimation.from_step(step)
                assert seq.beats[0].effect==name
                app.combat_animation=seq;app.presentation.screen=Screen.GAME
                app.controller.state=outcome.next_state
                app.controller.last_report=TurnReport(step,'Revisión gráfica',1,outcome.reward,False)
                app.controller.turn=1;app.controller.reward=outcome.reward
                for i,ms in enumerate((80,240,400,560)):
                    seq.elapsed_ms=ms
                    count=len(requests)
                    app.draw()
                    assert name in requests[count:],('La animación no utilizó el sprite',action,form)
                    file=f'{name}_forma{form}_{i}.png'
                    pygame.image.save(app.screen,str(args.output/file));result['screenshots'].append(file)
                result['cases'].append({'action':action.value,'form':form,'sprite':name,'frames':4})
        app._command('effects')
        for index,name in enumerate(ALL_EFFECTS):
            app._command('effect_select',index);app.effect_elapsed=650;app.draw()
            buttons=[b for b in app.buttons if b.command=='effect_select']
            assert len(buttons)==13
            for i,a in enumerate(buttons):
                assert all(not a.rect.colliderect(b.rect) for b in buttons[i+1:])
                assert a.rect.bottom<550
            file='galeria_'+name+'.png'
            pygame.image.save(app.screen,str(args.output/file));result['screenshots'].append(file)
            if args.gif and name in BASIC_EFFECTS.values():
                from PIL import Image
                for ms in range(0,1600,100):
                    app.effect_elapsed=ms;app.draw()
                    scaled=pygame.transform.smoothscale(app.screen,(768,492))
                    frames.append(Image.frombytes('RGB',scaled.get_size(),pygame.image.tostring(scaled,'RGB')))
        if frames:
            frames[0].save(args.output/'Vista_Previa_Basicos_v0141.gif',save_all=True,
                           append_images=frames[1:],duration=100,loop=0,optimize=True)
        result['status']='PASS'
    except Exception as exc:
        result['error']=repr(exc)
        raise
    finally:
        (args.output/'validacion.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
        pygame.quit()
    print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
