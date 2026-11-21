"""Prueba real de Pygame/SDL; --headless evita abrir una ventana.

El informe identifica el SO real. Ejecutar en Linux no certifica Windows.
No entrena agentes ni reemplaza políticas o resultados académicos.
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
sys.path.insert(0, str(ROOT / "src"))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--headless", action="store_true")
    parser.add_argument("--output", type=Path, default=ROOT / "resultados" / "interfaz_v013")
    args = parser.parse_args()
    if args.headless:
        os.environ["SDL_VIDEODRIVER"] = "dummy"
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
    import pygame
    from digimon_rl.gui.app import RPGApp, WIDTH, HEIGHT
    from digimon_rl.gui.layout import Viewport
    from digimon_rl.environment import DigitalWorld
    from digimon_rl.session import AdventureController, ControlMode
    from digimon_rl.domain import Ending, Zone
    from digimon_rl.policy_io import load_policy
    from digimon_rl.inspector import PolicyInspector
    from digimon_rl.academic_dashboard import AcademicDashboard
    from digimon_rl.presentation import Screen

    args.output.mkdir(parents=True, exist_ok=True)
    world = DigitalWorld()
    dp_file, mc_file = ROOT / "politicas/dp.json", ROOT / "politicas/mc.json"
    dp, mc = load_policy(dp_file, world), load_policy(mc_file, world)
    inspector = PolicyInspector.from_export(world, dp, mc,
        ROOT / "politicas/analisis_v010.json.gz", dp_file, mc_file)
    dashboard = AcademicDashboard.load(ROOT / "resultados/convergencia_v021")
    app = RPGApp(AdventureController(world, dp, mc), asset_root=ROOT / "assets",
                 inspector=inspector, dashboard=dashboard)
    report = {"platform": platform.platform(), "python": platform.python_version(),
              "pygame": pygame.version.ver, "headless": args.headless,
              "checks": [], "screenshots": [], "episodes": []}
    bounds_errors = []
    label = ""
    original_text = app._text

    def checked_text(value, x, y, *, font=None, color=(232, 243, 250), center=False):
        face = font or app.body
        rect = face.render(str(value), True, color).get_rect()
        if center:
            rect.center = (x, y)
        else:
            rect.topleft = (x, y)
        if not pygame.Rect(0, 0, WIDTH, HEIGHT).contains(rect):
            bounds_errors.append({"screen": label, "text": str(value), "rect": list(rect)})
        original_text(value, x, y, font=font, color=color, center=center)

    app._text = checked_text
    thumbs = []
    try:
        app.initialize((1280, 820))
        report["video_driver"] = pygame.display.get_driver()

        def capture(name):
            nonlocal label
            label = name
            app.last_mouse = (-1, -1)
            app.draw()
            app._present_frame()
            for box in app.buttons:
                assert pygame.Rect(0, 0, WIDTH, HEIGHT).contains(box.rect), (name, box)
            pygame.image.save(app.screen, str(args.output / (name + ".png")))
            report["screenshots"].append(name + ".png")
            thumbs.append((name, pygame.transform.smoothscale(app.screen, (384, 246))))

        capture("01_inicio")
        # Comprueba eventos reales de teclado y retorno de los paneles.
        for mode, key in ((ControlMode.DYNAMIC_PROGRAMMING, pygame.K_F1),
                          (ControlMode.MONTE_CARLO, pygame.K_F2),
                          (ControlMode.MANUAL, pygame.K_F3)):
            app._command("title")
            app._on_key(key)
            assert app.controller.mode == mode
            before = app.controller.state
            for key_modal in (pygame.K_F4, pygame.K_F5, pygame.K_t, pygame.K_h, pygame.K_p):
                app._on_key(key_modal)
                app.draw()
                app._on_key(pygame.K_ESCAPE)
                assert app.presentation.screen == Screen.GAME
                assert app.controller.state == before and app.controller.turn == 0
        report["checks"].append("F1/F2/F3, F4/F5/T/H/P y retorno sin modificar el estado")

        app._new_adventure(ControlMode.MANUAL)
        app.notice_ticks = 0
        capture("02_mapa_manual")
        # Escenario de presentación, no es una trayectoria ni resultado experimental.
        state = replace(world.start_state(), zone=Zone.FORTRESS, hp=4, energy=6,
                        enemy_hp=6, enemy_charging=True, evolved=2, xp=2)
        app.controller.state = state
        assert len(app.controller.legal_actions) == 7
        capture("03_siete_acciones")
        actions = [b for b in app.buttons if b.command == "action"]
        for i, first in enumerate(actions):
            assert all(not first.rect.colliderect(b.rect) for b in actions[i+1:])
        report["checks"].append("Siete acciones manuales: botones separados y dentro del panel")
        for form in range(4):
            app.controller.state = replace(state, evolved=form)
            capture(f"04_forma_{form}")

        app.inspection_history = [state]
        app.inspection_index = 0
        app._command("analysis")
        capture("05_laboratorio")
        app._command("back")
        app._command("results")
        for i in range(4):
            app.results_metric_index = i
            capture(f"06_resultados_{i}")
        app._command("demo")
        for i in range(6):
            app.demo_index = i
            capture(f"07_presentacion_{i}")
        app._command("back")

        # Clic en el botón F3 tras transformarlo a coordenadas de la ventana.
        for size in ((1366, 768), (1024, 768), (1920, 1080), (800, 600)):
            app.window = pygame.display.set_mode(size, pygame.RESIZABLE)
            app._command("title")
            app.draw()
            app._present_frame()
            button = next(b for b in app.buttons if b.command == "start" and b.value == ControlMode.MANUAL)
            v = Viewport(*app.window.get_size())
            ox, oy = v.origin
            w, h = v.size
            pos = (ox+round(button.rect.centerx*w/WIDTH), oy+round(button.rect.centery*h/HEIGHT))
            app._on_click(app._pointer(pos))
            assert app.controller.mode == ControlMode.MANUAL and app.presentation.screen == Screen.GAME
            assert app.controller.turn == 0
        report["checks"].append("Clic transformado y lienzo completo a cuatro resoluciones")
        app._toggle_fullscreen()
        app._toggle_fullscreen()
        report["checks"].append("Entrada/salida de pantalla completa SDL")

        for mode in (ControlMode.DYNAMIC_PROGRAMMING, ControlMode.MONTE_CARLO):
            app._new_adventure(mode)
            while not app.controller.finished:
                app._advance()
                app.draw()
            report["episodes"].append({"mode": mode.value, "turns": app.controller.turn,
                "outcome": app.controller.outcome, "reward": app.controller.reward})
            capture("08_final_"+mode.value)
        for terminal in (Ending.WIN, Ending.LOSS):
            app.controller.state = terminal
            capture("09_"+terminal.value)
        app._new_adventure(ControlMode.MANUAL)
        app._command("help")
        capture("10_ayuda")
        app._command("back")
        app._command("credits")
        capture("11_creditos")
        report["checks"].append("Aventuras DP/MC completas, finales, formas, laboratorio y seis diapositivas")
        assert not bounds_errors, bounds_errors
        report["checks"].append("Textos y botones dentro del lienzo lógico")
        # Contacto visual compacto para revisar las capturas.
        sheet = pygame.Surface((1152, ((len(thumbs)+2)//3)*270))
        sheet.fill((12, 18, 35))
        for i, (name, thumb) in enumerate(thumbs):
            x, y = (i%3)*384, (i//3)*270
            sheet.blit(thumb, (x,y+24))
            sheet.blit(app.tiny.render(name, True, (232,243,250)), (x+8,y+4))
        pygame.image.save(sheet, str(args.output / "contacto.png"))
        # Prueba adicional del bucle de eventos y cierre limpio.
        pygame.quit()
        loop_app = RPGApp(AdventureController(world, dp, mc), asset_root=ROOT/"assets", dashboard=dashboard)
        loop_app.run(max_frames=3)
        report["checks"].append("Bucle de eventos SDL y cierre limpio")
        report["status"] = "PASS"
    except Exception as exc:
        report["status"] = "FAIL"
        report["error"] = repr(exc)
        report["text_bounds_errors"] = bounds_errors
        raise
    finally:
        (args.output / "validacion.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        pygame.quit()
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
