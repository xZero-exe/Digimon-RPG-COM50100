"""Valida audio, controles y transiciones con SDL real; no entrena agentes.

--headless usa audio/video dummy, no certifica altavoces ni Windows.
--video exporta un montaje opcional (requiere FFmpeg, no necesario para jugar).
"""
from __future__ import annotations
from dataclasses import replace
import argparse
import json
import os
from pathlib import Path
import platform
from random import Random
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--headless',action='store_true')
    parser.add_argument('--no-audio',action='store_true',help='Simular un dispositivo no disponible')
    parser.add_argument('--video',action='store_true')
    parser.add_argument('--output',type=Path,default=ROOT/'resultados/audio_v018')
    args=parser.parse_args()
    if args.headless:
        os.environ['SDL_VIDEODRIVER']='dummy';os.environ['SDL_AUDIODRIVER']='dummy'
    if args.no_audio:
        os.environ['SDL_AUDIODRIVER']='digimon_unavailable_driver'
    import pygame
    from digimon_rl.audio_settings import AudioSettings
    from digimon_rl.combat_visuals import ALL_EFFECTS, ENEMY_EFFECTS, HERO_EFFECTS
    from digimon_rl.domain import Action, Ending, GameState, Zone
    from digimon_rl.environment import DigitalWorld
    from digimon_rl.gui.app import RPGApp
    from digimon_rl.gui.audio import AudioManager
    from digimon_rl.presentation import Screen
    from digimon_rl.session import AdventureController, ControlMode
    args.output.mkdir(parents=True,exist_ok=True)
    report={'status':'FAIL','platform':platform.platform(),'pygame':pygame.version.ver,
            'headless':args.headless,'checks':[],'screenshots':[],'cases':[],'sounds':[]}
    world=DigitalWorld();played=[];heard=set()
    temporary=tempfile.TemporaryDirectory()
    prefs=Path(temporary.name)/'audio.json'
    app=RPGApp(AdventureController(world,{},{}),asset_root=ROOT/'assets',audio_settings_path=prefs)
    app.audio.observer=lambda name,group,gain:played.append(name)
    original_text=app._text

    def checked(value,x,y,*,font=None,color=(232,243,250),center=False):
        rect=(font or app.body).render(str(value),True,color).get_rect()
        if center:rect.center=(x,y)
        else:rect.topleft=(x,y)
        assert pygame.Rect(0,0,1280,820).contains(rect),(value,rect)
        original_text(value,x,y,font=font,color=color,center=center)
    app._text=checked

    def snapshot():
        c=app.controller
        return c.state,c.turn,c.reward,c.rng.getstate(),tuple(c.history),frozenset(c.visited_zones)

    def draw():
        before=snapshot();count=len(played)
        app.draw();app._present_frame()
        assert snapshot()==before and len(played)==count,'Dibujar produjo sonido o cambió el episodio'
        for i,a in enumerate(app.buttons):
            assert pygame.Rect(0,0,1280,820).contains(a.rect)
            assert all(not a.rect.colliderect(b.rect) for b in app.buttons[i+1:]),a

    def capture(name):
        draw();pygame.image.save(app.screen,str(args.output/(name+'.png')))
        report['screenshots'].append(name+'.png')

    def install(state,action,predicate=lambda s:True):
        app.controller.state=state;app.controller.mode=ControlMode.MANUAL
        app.controller.turn=0;app.controller.reward=0.;app.controller.last_report=None
        app.controller.history=['Diagnóstico de sonido y presentación.']
        app.controller.visited_zones={Zone.VILLAGE,state.zone}
        app.inspection_history=[world.start_state(),state]
        app.presentation.screen=Screen.GAME
        app.combat_animation=None;app.region_transition=None
        app.animation_speed=1;app.notice_ticks=0;app.cue_ticks=0;app.fx_ticks=0
        outcomes=world.transitions(state,action)
        for seed in range(1000):
            outcome=world.sample(outcomes,Random(seed))
            if predicate(outcome.next_state):
                app.controller.rng=Random(seed);break
        else:raise AssertionError('Resultado de prueba no encontrado')
        expected_rng=Random(seed);expected=world.sample(outcomes,expected_rng)
        played.clear();app._advance(action);app.notice_ticks=0
        assert app.controller.state==expected.next_state
        assert app.controller.rng.getstate()==expected_rng.getstate() and app.controller.turn==1
        return snapshot()

    def finish_visuals():
        before=snapshot()
        for _ in range(100):
            if not app.presentation_busy:break
            app._update_combat_visuals(40)
        assert not app.presentation_busy and snapshot()==before
        heard.update(played)

    try:
        app.initialize((1280,820));app._new_adventure(ControlMode.MANUAL)
        report['audio_available']=app.audio.available
        report['audio_backend']=os.environ.get('SDL_AUDIODRIVER','system default')
        capture('00_controles')
        if not app.audio.available:
            before=install(world.start_state(),Action.ROUTE_FOREST)
            app._update_combat_visuals(40);capture('sin_dispositivo');finish_visuals()
            assert snapshot()==before and not app.audio.play('baby_flame')
            app._command('audio_mute');app._command('audio_up')
            assert snapshot()==before
            report['checks']=['device_failure_is_non_fatal','transition_works_without_audio',
                              'audio_controls_preserve_episode','render_preserves_episode']
        else:
            manifest=json.loads((ROOT/'assets/audio/manifest_v018.json').read_text())
            for row in manifest['files']:
                sound=app.audio.sound(Path(row['file']).stem)
                assert sound is not None and sound.get_length()>.03
            assert app.audio.sound('not_bundled') is None and not app.audio.play('not_bundled')
            before=install(world.start_state(),Action.ROUTE_CAVE,
                           lambda s:isinstance(s,GameState) and s.hp==5)
            app._update_combat_visuals(40);assert 'travel' in played
            app._update_combat_visuals(240);capture('transicion_caverna')
            assert app.region_transition.elapsed_ms==280
            assert app.region_transition.display_state.zone==Zone.CAVE
            app._command('pause');elapsed=app.region_transition.elapsed_ms
            count=len(played);app._update_combat_visuals(3000)
            assert app.region_transition.elapsed_ms==elapsed and app.audio.paused
            assert len(played)==count;capture('pausa_transicion')
            app._on_key(pygame.K_ESCAPE);assert not app.audio.paused
            app._command('action',Action.ATTACK);assert snapshot()==before
            finish_visuals();assert 'impact' in played
            app._update_combat_visuals(100);assert played.count('travel')==1
            for form,name in enumerate(HERO_EFFECTS):
                install(GameState(Zone.FORTRESS,6,6,6,form,True),Action.TECHNIQUE)
                app._update_combat_visuals(40);assert name in played
                app._update_combat_visuals(400);capture('tecnica_'+name);finish_visuals()
                report['cases'].append({'case':name,'sounds':list(played)})
            for zone,name in ENEMY_EFFECTS.items():
                install(GameState(zone,6,3,world.ENEMY_HP[zone],0,True),Action.GUARD,
                        lambda s:isinstance(s,GameState) and s.hp<6)
                for _ in range(18):app._update_combat_visuals(40)
                assert name in played;capture('enemigo_'+name);finish_visuals()
                report['cases'].append({'case':name,'sounds':list(played)})
            for action,name in ((Action.ATTACK,'basic_attack'),(Action.POWER_ATTACK,'power_attack'),
                                (Action.INTERRUPT,'interrupt_strike')):
                install(GameState(Zone.SWAMP,6,6,3,0,True,True),action,
                        lambda s:isinstance(s,GameState) and s.enemy_hp<3)
                finish_visuals();assert name in played
                if action==Action.INTERRUPT:
                    assert 'cancel' in played and 'haouken' not in played
                capture('basico_'+name)
            for action,name,state in (
                (Action.HEAL,'heal',GameState(Zone.FOREST,2,3,2,0,True,True)),
                (Action.DIGIVOLVE,'evolve',GameState(Zone.RUINS,4,6,4,1,True,True))):
                install(state,action);app._update_combat_visuals(40);assert name in played
                app._update_combat_visuals(400);capture(name);finish_visuals()
            install(GameState(Zone.FORTRESS,1,3,6,0,True),Action.ATTACK,lambda s:s==Ending.LOSS)
            finish_visuals();assert played.count('loss')==1
            app._update_combat_visuals(1000);assert played.count('loss')==1
            capture('derrota')
            # Omitir no reproduce el resto de los sonidos ni consume otro turno.
            before=install(GameState(Zone.SWAMP,6,3,3,0,True),Action.ATTACK)
            app._update_combat_visuals(80);app._command('skip_animation')
            count=len(played);app._update_combat_visuals(2000)
            assert len(played)==count and snapshot()==before
            before=install(world.start_state(),Action.ROUTE_FOREST)
            app._command('skip_animation');assert not app.presentation_busy and snapshot()==before
            # Cambiar preferencias por teclado y clic nunca toca el controlador.
            draw();before=snapshot();app._on_key(pygame.K_F10)
            assert app.audio.settings.volume==.45
            app._on_click(next(b.rect.center for b in app.buttons if b.command=='audio_down'))
            assert app.audio.settings.volume==.35
            app._on_key(pygame.K_F8);assert app.audio.settings.muted
            assert AudioSettings.load(prefs).muted
            assert not app.audio.play('impact');capture('silenciado')
            app._on_key(pygame.K_F8);assert not app.audio.settings.muted and snapshot()==before
            assert AudioManager(ROOT/'assets/audio',prefs).settings==app.audio.settings
            # Una señal consumida durante el silencio no reaparece al activarlo.
            install(world.start_state(),Action.ROUTE_FOREST)
            app._command('audio_mute');played.clear();app._update_combat_visuals(40)
            app._command('audio_mute');app._update_combat_visuals(0)
            assert 'travel' not in played
            finish_visuals()
            # Galería: sonido optativo una vez por clic y sin avances del MDP.
            app._command('effects');before=snapshot()
            for i,name in enumerate(ALL_EFFECTS):
                app._command('effect_select',i);played.clear();app._command('effect_listen')
                assert played==[name] and snapshot()==before
                heard.add(name)
            capture('galeria_audio')
            report['checks']=['23_wavs_load_in_mixer','missing_sound_is_non_fatal',
                'sounds_follow_resolved_turn','cancel_has_no_enemy_sound','one_outcome_jingle',
                'pause_freezes_clock_and_audio','skip_has_no_sound_burst_or_extra_turn',
                'mute_volume_and_persistence','unmute_does_not_replay_consumed_cues',
                'gallery_audio_is_opt_in_and_read_only','transition_blocks_input_and_preserves_rng',
                'render_is_silent_and_preserves_episode','labels_and_buttons_fit']
            if args.video:
                from grabar_demo_v018 import record_demo
                report['video']=record_demo(app,world,args.output).name
            pygame.mixer.quit()
            app._command('audio_test')
            assert not app.audio.available
            capture('mixer_cerrado')
            report['checks'].append('mixer_shutdown_is_non_fatal')
        report['sounds']=sorted(heard)
        report['status']='PASS'
    except Exception as exc:
        report['error']=repr(exc);raise
    finally:
        (args.output/'validacion.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
        pygame.quit();temporary.cleanup()
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
