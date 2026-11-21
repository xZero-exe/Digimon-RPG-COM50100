"""Comprueba los siete fondos con Pygame real y genera evidencia de integración.

No entrena ni altera políticas. --headless usa SDL dummy; no certifica Windows.
"""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import platform
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--headless', action='store_true')
    parser.add_argument('--output', type=Path, default=ROOT/'resultados/fondos_v015')
    args = parser.parse_args()
    if args.headless:
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
    os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
    import pygame
    from digimon_rl.assets_catalog import BACKGROUND_NAMES, resolve_asset
    from digimon_rl.domain import GameState, Zone
    from digimon_rl.environment import DigitalWorld
    from digimon_rl.gui.app import RPGApp
    from digimon_rl.gui.sprites import SpriteManager
    from digimon_rl.presentation import Screen
    from digimon_rl.session import AdventureController, ControlMode

    args.output.mkdir(parents=True, exist_ok=True)
    app = RPGApp(AdventureController(DigitalWorld(), {}, {}), asset_root=ROOT/'assets')
    report = {'status': 'FAIL', 'platform': platform.platform(), 'python': platform.python_version(),
              'pygame': pygame.version.ver, 'headless': args.headless,
              'checks': [], 'screenshots': [], 'backgrounds': []}
    try:
        app.initialize((1280, 820))
        # Un círculo debe permanecer circular al cubrir un recuadro cuadrado.
        # Rojo/azul en los extremos comprueban que se recorta, en lugar de estirar.
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root/'backgrounds').mkdir()
            synthetic = pygame.Surface((200, 100)); synthetic.fill('green')
            pygame.draw.rect(synthetic, 'red', (0, 0, 50, 100))
            pygame.draw.rect(synthetic, 'blue', (150, 0, 50, 100))
            pygame.draw.circle(synthetic, 'white', (100, 50), 20)
            pygame.image.save(synthetic, str(root/'backgrounds/test.png'))
            manager = SpriteManager(root)
            covered = manager.background('test', (100, 100))
            assert covered.get_at((0, 50))[:3] == pygame.Color('green')[:3]
            white = pygame.mask.from_threshold(covered, pygame.Color('white'), (1,1,1,255))
            box = white.get_bounding_rects()[0]
            assert abs(box.width-box.height) <= 1, box
            assert set(map(tuple, pygame.surfarray.array3d(covered).reshape(-1,3))) <= {
                tuple(pygame.Color(c)[:3]) for c in ('green','white')}
            assert manager.background('test', (100,100)) is covered
            (root/'demo/backgrounds').mkdir(parents=True)
            pygame.image.save(synthetic, str(root/'demo/backgrounds/fallback.png'))
            assert manager.background('fallback', (414,225)) is not None
            assert manager.background('absent', (414,225)) is None
        report['checks'].extend(['cover_preserves_aspect', 'center_crop', 'nearest_neighbor',
                                 'cache', 'demo_fallback', 'missing_fallback'])
        thumbnails = []

        def capture(name):
            before = (app.controller.state, app.controller.turn, app.controller.reward,
                      app.controller.rng.getstate())
            app.draw(); app._present_frame()
            after = (app.controller.state, app.controller.turn, app.controller.reward,
                     app.controller.rng.getstate())
            assert before == after, 'El render modificó el episodio o su RNG'
            file = name+'.png'
            pygame.image.save(app.screen, str(args.output/file))
            report['screenshots'].append(file)

        capture('00_inicio')
        title_thumb = pygame.transform.scale(app.screen, (520,333))
        app._new_adventure(ControlMode.MANUAL)
        app.notice_ticks = 0; app.cue_ticks = 0
        for zone, name in BACKGROUND_NAMES.items():
            path = ROOT/'assets/backgrounds'/f'{name}.png'
            assert resolve_asset(ROOT/'assets', 'backgrounds', name) == path
            raw = pygame.image.load(str(path))
            w,h = raw.get_size()
            assert w >= 1000 and h >= 500 and 1.7 < w/h < 1.9
            assert raw.get_bounding_rect(min_alpha=255).size == raw.get_size()
            for size in ((414,225), (573,306), (1280,820)):
                bg = app.sprites.background(name,size)
                assert bg.get_size() == size
                assert bg is app.sprites.background(name,size)
            report['backgrounds'].append({'name':name,'zone':zone.label,'size':[w,h]})
            for form in range(4):
                app.presentation.screen = Screen.GAME
                # Casos de composición visual; no forman un entrenamiento.
                app.controller.state = GameState(zone,6,6,0 if zone in (Zone.VILLAGE,Zone.REFUGE) else 2,
                                                form,True,True)
                app.controller.last_report = None
                capture(f'{name}_forma{form}')
                if form == 0:
                    thumb = pygame.transform.scale(app.screen.subsurface((820,197,414,225)), (520,283))
                    thumbnails.append((zone.label, thumb))
        app._command('effects')
        # Índices 4..9 corresponden a los seis enemigos/regiones de combate.
        for index in range(4,10):
            app._command('effect_select',index); app.effect_elapsed = 650
            capture(f'galeria_region_{index}')
        report['checks'].extend(['nine_primary_backgrounds', 'all_four_forms',
                                 'title_and_six_gallery_regions', 'render_preserves_state_and_rng'])
        sheet = pygame.Surface((1080, 1680)); sheet.fill((12,23,38))
        for index,(label,thumb) in enumerate(thumbnails):
            x,y = 14+(index%2)*540, 12+(index//2)*322
            sheet.blit(app.small.render(label,True,(240,219,156)), (x,y))
            sheet.blit(thumb,(x,y+28))
        sheet.blit(app.small.render('Inicio · nuevo bosque', True, (240,219,156)), (554,1300))
        sheet.blit(title_thumb,(554,1328))
        pygame.image.save(sheet, str(args.output/'Vista_Previa_Fondos_v015.png'))
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
