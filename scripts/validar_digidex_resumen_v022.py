"""Prueba fichas, diario y navegación T con SDL, sin reentrenar agentes.

--headless usa SDL dummy: no certifica Windows ni audio físico.
Las capturas corresponden al render del juego y a episodios reales.
"""
import argparse
import json
import os
from pathlib import Path
import platform
import sys
from tempfile import TemporaryDirectory
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--headless',action='store_true')
    parser.add_argument('--output',type=Path,default=ROOT/'resultados/diario_v022/interfaz')
    args=parser.parse_args()
    if args.headless:os.environ['SDL_VIDEODRIVER']='dummy'
    os.environ.setdefault('SDL_AUDIODRIVER','dummy')
    import pygame
    from digimon_rl.adventure_summary import summarize
    from digimon_rl.digidex import load_entries
    from digimon_rl.domain import Action,GameState
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
    args.output.mkdir(parents=True,exist_ok=True)
    report={'status':'FAIL','platform':platform.platform(),'headless':args.headless,
            'native_windows':platform.system()=='Windows','pygame':pygame.version.ver,
            'checks':[],'screenshots':[],'fichas':[],'episodes':[]}
    def snapshot():
        c=app.controller
        return (c.state,c.turn,c.reward,c.rng.getstate(),tuple(c.decisions))
    def draw():
        before=snapshot();app.draw();app._present_frame()
        assert snapshot()==before,'La consulta alteró la partida'
        bounds=pygame.Rect(0,0,1280,820)
        for i,b in enumerate(app.buttons):
            assert bounds.contains(b.rect),(b,'fuera de pantalla')
            assert all(not b.rect.colliderect(c.rect) for c in app.buttons[i+1:]),(b,'solapamiento')
    def capture(name):
        draw();pygame.image.save(app.screen,str(args.output/(name+'.png')))
        report['screenshots'].append(name+'.png')
    def click(command,value=None):
        draw()
        box=next(b for b in app.buttons if b.command==command and (value is None or b.value==value))
        app._on_click(box.rect.center)
    def fresh(seed=42,max_steps=80,mode=ControlMode.DYNAMIC_PROGRAMMING):
        app.controller=AdventureController(world,dp,mc,seed=seed,max_steps=max_steps)
        app.controller.mode=mode;app.presentation.start(mode)
        app.inspection_history=[app.controller.state];app.inspection_index=0
        app.combat_animation=None;app.region_transition=None
        app.notice_ticks=app.cue_ticks=0;app.summary_page=0
        app.analysis_from_summary=False
    with TemporaryDirectory() as temp:
        app=RPGApp(AdventureController(world,dp,mc),asset_root=ROOT/'assets',inspector=inspector,
                   dashboard=dashboard,audio_settings_path=Path(temp)/'audio.json')
        try:
            app.initialize((1280,820));original_text=app._text
            def checked(value,x,y,*,font=None,color=(232,243,250),center=False):
                rect=(font or app.body).render(str(value),True,color).get_rect()
                if center:rect.center=(x,y)
                else:rect.topleft=(x,y)
                assert pygame.Rect(0,0,1280,820).contains(rect),(value,rect)
                original_text(value,x,y,font=font,color=color,center=center)
            app._text=checked
            app._on_key(pygame.K_F7);assert app.presentation.screen==Screen.DIGIDEX
            for index,entry in enumerate(load_entries()):
                click('dex_select',index);draw()
                report['fichas'].append(entry.name)
                if entry.species in ('wargreymon','guardromon'):capture('digidex_'+entry.species)
            before=snapshot()
            with patch('webbrowser.open',return_value=True) as opened:
                click('dex_source');opened.assert_called_once_with(load_entries()[-1].source_url)
            with patch('webbrowser.open',side_effect=OSError('prueba controlada')):
                click('dex_source');assert app.dex_source_notice
            assert before==snapshot()
            for label,count in (('heroes',4),('enemies',7),('all',11)):
                click('dex_filter',label);assert len(app._dex_entries())==count;draw()
            app._on_key(pygame.K_ESCAPE);assert app.presentation.screen==Screen.TITLE
            report['checks']+=['11_offline_canonical_fichas','filters_4_7_11','source_click_exact_url_and_failure_handling','title_return']
            fresh();app._advance();assert app.presentation_busy
            elapsed=(getattr(app.combat_animation,'elapsed_ms',None),getattr(app.region_transition,'elapsed_ms',None))
            before=snapshot();app._on_key(pygame.K_F7);app._update_combat_visuals(500)
            assert elapsed==(getattr(app.combat_animation,'elapsed_ms',None),getattr(app.region_transition,'elapsed_ms',None))
            app._on_key(pygame.K_F7);assert app.presentation.screen==Screen.GAME
            app._finish_turn_presentation();app._on_key(pygame.K_TAB);capture('diario_en_curso')
            app._on_key(pygame.K_TAB);assert app.presentation.screen==Screen.GAME and before==snapshot()
            report['checks']+=['f7_pauses_current_animation','tab_live_diary_preserves_episode']
            fresh();app.animation_speed=0
            while not app.controller.finished:app._advance()
            assert app.controller.outcome=='VICTORIA'
            capture('resumen_victoria');data=summarize(app.controller)
            report['episodes'].append({'mode':'dp','seed':42,'outcome':data.outcome,'turns':data.turns,'reward':data.reward,'discounted_return':data.discounted_return})
            assert not any(b.command in ('action','next') for b in app.buttons)
            pages=max(1,(len(data.moments)+3)//4)
            for page in range(pages):
                app.summary_page=page;draw()
                moment=data.moments[page*4];before=snapshot()
                click('summary_inspect',moment.index)
                assert app.presentation.screen==Screen.ANALYSIS
                assert app.inspection_history[app.inspection_index]==app.controller.decisions[moment.index].step.state
                capture('laboratorio_turno_'+str(moment.index+1))
                app._on_key(pygame.K_ESCAPE);assert app.presentation.screen==Screen.SUMMARY
                assert before==snapshot()
            app.summary_page=pages-1;capture('resumen_ultimas_decisiones')
            app._on_key(pygame.K_t);assert app.presentation.screen==Screen.ANALYSIS
            app._on_key(pygame.K_ESCAPE);app._on_key(pygame.K_ESCAPE)
            assert app.presentation.screen==Screen.TITLE
            report['checks']+=['actual_dp_victory_full_summary','all_moment_pages','summary_to_exact_pre_action_inspector_state_and_back','t_shortcut','terminal_esc_returns_title']
            # Una derrota real, con acciones manuales legales; no se fuerza un terminal.
            fresh(seed=42,mode=ControlMode.MANUAL)
            while not app.controller.finished:
                legal=app.controller.legal_actions
                app._advance(Action.ATTACK if Action.ATTACK in legal else legal[0])
            assert app.controller.outcome=='DERROTA';capture('resumen_derrota')
            report['episodes'].append({'mode':'manual','seed':42,'outcome':app.controller.outcome,'turns':app.controller.turn})
            fresh(max_steps=1);app._advance();capture('resumen_limite')
            assert summarize(app.controller).outcome=='LIMITE DE TURNOS'
            report['checks']+=['actual_manual_defeat','truncation_not_loss']
            fresh(mode=ControlMode.MONTE_CARLO)
            while not app.controller.finished:app._advance()
            capture('resumen_monte_carlo')
            report['episodes'].append({'mode':'mc','seed':42,'outcome':app.controller.outcome,'turns':app.controller.turn})
            app._on_key(pygame.K_F4);assert app.presentation.screen==Screen.RESULTS
            app._on_key(pygame.K_ESCAPE);assert app.presentation.screen==Screen.GAME
            app._on_key(pygame.K_F6);assert app.presentation.screen==Screen.EFFECTS
            app._on_key(pygame.K_ESCAPE);assert app.presentation.screen==Screen.GAME
            report['checks']+=['actual_saved_mc_episode','terminal_f4_and_f6_preserved']
            # Las dos nuevas pantallas reutilizan el mismo mapeo de clics al redimensionar.
            app._command('digidex')
            for size in ((1024,768),(1366,768),(1280,820)):
                app.window=pygame.display.set_mode(size,pygame.RESIZABLE);draw()
                box=next(b for b in app.buttons if b.command=='dex_filter' and b.value=='enemies')
                ox,oy=app.viewport.origin;w,h=app.viewport.size
                point=(round(ox+box.rect.centerx*w/1280),round(oy+box.rect.centery*h/820))
                logical=app.viewport.to_logical(point);assert logical and box.rect.collidepoint(logical)
                app._on_click(logical);assert app.dex_filter=='enemies'
            report['checks']+=['three_window_sizes_and_scaled_clicks','labels_and_buttons_within_canvas','buttons_do_not_overlap','all_renders_preserve_state_rng_reward_and_ledger']
            report['status']='PASS'
        except Exception as exc:
            report['error']=repr(exc);raise
        finally:
            pygame.quit()
            (args.output/'reporte.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
