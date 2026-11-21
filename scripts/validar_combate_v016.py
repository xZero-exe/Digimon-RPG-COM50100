"""Diagnóstico de feedback de combate con Pygame/SDL real y resultados legales.

--headless no certifica Windows. --gif requiere el extra art (Pillow).
No entrena agentes ni modifica políticas.
"""
from __future__ import annotations
import argparse
from dataclasses import replace
import json
import os
from pathlib import Path
import platform
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--headless',action='store_true')
    parser.add_argument('--output',type=Path,default=ROOT/'resultados/combate_v016')
    parser.add_argument('--gif',action='store_true')
    args = parser.parse_args()
    if args.headless:
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
    os.environ.setdefault('SDL_AUDIODRIVER','dummy')
    import pygame
    from digimon_rl.combat_visuals import CombatAnimation
    from digimon_rl.domain import Action, Ending, GameState, Step, Zone
    from digimon_rl.environment import DigitalWorld
    from digimon_rl.gui.app import RPGApp
    from digimon_rl.presentation import Screen
    from digimon_rl.session import AdventureController, ControlMode, TurnReport

    world = DigitalWorld()
    app = RPGApp(AdventureController(world,{},{}),asset_root=ROOT/'assets')
    args.output.mkdir(parents=True,exist_ok=True)
    report = {'status':'FAIL','platform':platform.platform(),'pygame':pygame.version.ver,
              'headless':args.headless,'checks':[],'screenshots':[],'cases':[]}
    frames = []; thumbs = []
    original_text = app._text

    def checked(value,x,y,*,font=None,color=(232,243,250),center=False):
        rect = (font or app.body).render(str(value),True,color).get_rect()
        if center:
            rect.center = (x,y)
        else:
            rect.topleft = (x,y)
        assert pygame.Rect(0,0,1280,820).contains(rect),(value,rect)
        original_text(value,x,y,font=font,color=color,center=center)

    app._text = checked

    def snapshot():
        return (app.controller.state,app.controller.turn,app.controller.reward,app.controller.rng.getstate())

    def draw():
        before = snapshot()
        app.draw(); app._present_frame()
        assert snapshot() == before,'El render alteró el episodio'
        for i,a in enumerate(app.buttons):
            assert pygame.Rect(0,0,1280,820).contains(a.rect)
            assert all(not a.rect.colliderect(b.rect) for b in app.buttons[i+1:]),(a,app.buttons)

    def capture(name):
        draw()
        pygame.image.save(app.screen,str(args.output/(name+'.png')))
        report['screenshots'].append(name+'.png')

    def install(state,action,predicate):
        outcome = next(t for t in world.transitions(state,action) if predicate(t.next_state))
        step = Step(state,action,outcome.reward,outcome.next_state)
        app.combat_animation = CombatAnimation.from_step(step)
        app.controller.state = step.next_state
        app.controller.turn = 1; app.controller.reward = step.reward
        app.controller.last_report = TurnReport(step,'Revisión de combate',1,step.reward,isinstance(step.next_state,Ending))
        app.controller.history = ['Revisión de un resultado legal del MDP.']
        app.presentation.screen = Screen.GAME
        app.notice_ticks = 0; app.cue_ticks = 0; app.fx_ticks = 0
        app.animation_speed = 1
        return app.combat_animation

    try:
        app.initialize((1280,820)); app._new_adventure(ControlMode.MANUAL)
        normal = GameState(Zone.FOREST,6,3,2,0,True)
        charged = GameState(Zone.SWAMP,5,3,3,0,True,True)
        cases = [
            ('impacto',normal,Action.ATTACK,lambda s:isinstance(s,GameState) and s.enemy_hp==1 and s.hp==5),
            ('sin_dano',normal,Action.ATTACK,lambda s:isinstance(s,GameState) and s.enemy_hp==2 and s.hp==5),
            ('pocion',replace(normal,hp=2,enemy_charging=True),Action.HEAL,lambda s:isinstance(s,GameState) and s.hp==2),
            ('defensa',GameState(Zone.CAVE,5,3,3,0,True,True),Action.GUARD,lambda s:isinstance(s,GameState) and s.hp==4),
            ('interrupcion',charged,Action.INTERRUPT,lambda s:isinstance(s,GameState) and s.enemy_hp==2),
            ('interrupcion_fallida',charged,Action.INTERRUPT,lambda s:isinstance(s,GameState) and s.enemy_hp==3 and s.hp==2),
            ('evolucion',GameState(Zone.RUINS,4,6,4,1,True,True),Action.DIGIVOLVE,lambda s:isinstance(s,GameState) and s.hp==2),
            ('golpe_final',GameState(Zone.FORTRESS,6,6,2,3,True),Action.TECHNIQUE,lambda s:s==Ending.WIN),
            ('derrota',GameState(Zone.FORTRESS,1,3,6,0,True),Action.ATTACK,lambda s:s==Ending.LOSS),
            ('armadura',GameState(Zone.FORTRESS,6,3,6,0,True),Action.ATTACK,lambda s:isinstance(s,GameState) and s.hp==3),
            ('sin_contra_dano',normal,Action.GUARD,lambda s:isinstance(s,GameState) and s.hp==6),
        ]
        for name,state,action,predicate in cases:
            seq = install(state,action,predicate)
            texts = []
            for index,ms in enumerate((100,450,1100,seq.duration_ms-1)):
                seq.elapsed_ms = min(ms,seq.duration_ms-1)
                capture(f'{name}_{index}')
                texts.extend(n.text for n in seq.feedback.notices(seq.beats,seq.elapsed_ms))
                if name in ('impacto','pocion','interrupcion','defensa') and index in (1,2):
                    thumb = pygame.transform.scale(app.screen.subsurface((800,108,452,471)),(452,471))
                    thumbs.append((name+(' · acción' if index==1 else ' · respuesta'),thumb))
            report['cases'].append({'case':name,'action':action.value,'notices':texts})
            if args.gif and name in ('impacto','pocion','interrupcion'):
                from PIL import Image
                for ms in range(0,seq.duration_ms,80):
                    seq.elapsed_ms = ms; draw()
                    scaled = pygame.transform.smoothscale(app.screen,(896,574))
                    frames.append(Image.frombytes('RGB',scaled.get_size(),pygame.image.tostring(scaled,'RGB')))
        # Avisos de intención, sin confundirlos con la animación de la acción actual.
        app.combat_animation = None; app.controller.last_report = None
        for name,state in (('intencion_normal',normal),('intencion_cargada',charged)):
            app.controller.state = state; capture(name)
        seq = install(*cases[0][1:])
        elapsed = seq.elapsed_ms
        app.presentation.open(Screen.PAUSE)
        app._update_combat_visuals(1000)
        assert seq.elapsed_ms == elapsed
        capture('pausa'); app.presentation.close()
        before = snapshot()
        # Un segundo turno no se acepta mientras se representa el primero.
        app._command('action',Action.ATTACK)
        assert snapshot() == before
        app._on_key(pygame.K_v); app._update_combat_visuals(20)
        assert app.animation_speed == 2 and seq.elapsed_ms==40
        capture('velocidad_rapida')
        app._on_click(next(b.rect.center for b in app.buttons if b.command=='animation_speed'))
        assert app.animation_speed == 0 and not app.animation_busy
        assert snapshot() == before
        capture('sin_animacion')
        app._on_key(pygame.K_v); assert app.animation_speed == 1
        seq = install(*cases[0][1:]); draw(); before = snapshot()
        app._on_click(next(b.rect.center for b in app.buttons if b.command=='skip_animation'))
        assert not app.animation_busy and snapshot()==before
        report['checks'].extend(['pause_freezes_animation','double_action_blocked','speed_keyboard_and_click',
                                 'skip_preserves_turn_and_rng','all_labels_and_buttons_within_window',
                                 'buttons_do_not_overlap','render_preserves_episode'])
        # La preferencia sin animación también se aplica al crear un turno nuevo.
        app._new_adventure(ControlMode.MANUAL); app.notice_ticks = 0
        app.controller.state = normal
        other = AdventureController(world,{},{}); other.reset(ControlMode.MANUAL); other.state = normal
        other.rng.setstate(app.controller.rng.getstate())
        app.animation_speed = 0
        expected = other.advance(Action.ATTACK)
        app._advance(Action.ATTACK)
        assert app.controller.last_report.step == expected.step
        assert app.controller.rng.getstate() == other.rng.getstate()
        assert app.controller.turn == 1 and not app.animation_busy
        report['checks'].append('instant_mode_resolves_exactly_one_identical_turn')
        capture('nuevo_turno_instantaneo')
        # Contacto visual de dos fases de cuatro casos, capturado del render real.
        sheet = pygame.Surface((944,2056)); sheet.fill((12,18,35))
        for i,(label,thumb) in enumerate(thumbs):
            x,y = 12+(i%2)*470,12+(i//2)*510
            sheet.blit(app.small.render(label,True,(255,192,96)),(x,y))
            sheet.blit(thumb,(x,y+25))
        pygame.image.save(sheet,str(args.output/'Vista_Previa_Combate_v016.png'))
        if frames:
            frames[0].save(args.output/'Vista_Previa_Combate_v016.gif',save_all=True,
                           append_images=frames[1:],duration=80,loop=0,optimize=True)
        report['status'] = 'PASS'
    except Exception as exc:
        report['error'] = repr(exc)
        raise
    finally:
        (args.output/'validacion.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
        pygame.quit()
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__ == '__main__':
    main()
