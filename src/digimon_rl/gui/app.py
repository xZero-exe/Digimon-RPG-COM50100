"""Interfaz 2D con título, narrativa, sprites PNG y fallback geométrico.

La vista NO modifica las reglas del MDP y NO descarga imágenes externas.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

import pygame

from ..domain import Action, Ending, GameState, Zone
from ..presentation import GamePresentation, Screen, StoryBeat, MODE_DESCRIPTIONS
from ..session import ACTION_LABELS, ENEMIES, ENEMY_SKILLS, AdventureController, ControlMode
from ..assets_catalog import (BACKGROUND_NAMES, ENEMY_SPRITES, HERO_SPRITES,
                              SPRITE_NAMES, find_asset_root)
from .sprites import SpriteManager
from .layout import Viewport, episode_positions
from .effects import EffectSprites
from .world_map import WorldMapRenderer
from .audio import AudioManager
from .journal import JournalViews
from ..adventure_summary import summarize
from ..digidex import load_entries
from ..audio_events import SoundCue, SoundTimeline, combat_cues
from ..region_transition import RegionTransition
from ..world_map import MAP_POSITIONS, WorldMapView
from ..combat_visuals import CombatAnimation, ENEMY_EFFECTS, EFFECT_LABELS, ALL_EFFECTS
from ..combat_feedback import IMPACT_FRACTION
from ..techniques import technique_for
from ..inspector import PolicyInspector
from ..academic_dashboard import AcademicDashboard, METRICS

WIDTH, HEIGHT = 1280, 820
FPS = 30
BG = (12, 18, 35)
PANEL = (21, 31, 51)
PANEL_LIGHT = (28, 42, 66)
WHITE = (232, 243, 250)
MUTED = (153, 174, 192)
CYAN = (87, 226, 229)
GOLD = (255, 192, 96)
GREEN = (107, 219, 162)
RED = (246, 120, 133)
PURPLE = (183, 157, 245)

ZONE_COLORS = {
    Zone.REFUGE:(100,235,214), Zone.ABYSS:(210,122,245),
    Zone.VILLAGE: (94, 199, 224),
    Zone.FOREST: (95, 205, 151),
    Zone.CAVE: (240, 171, 109),
    Zone.SWAMP: (103, 187, 170),
    Zone.RUINS: (175, 156, 236),
    Zone.TOWER: (241, 193, 99),
    Zone.FORTRESS: (248, 111, 148),
}

ZONE_POS = MAP_POSITIONS


@dataclass(frozen=True)
class HitBox:
    rect: pygame.Rect
    command: str
    value: object = None


class RPGApp(JournalViews):
    """Vista + controlador de entrada. La lógica del MDP está en DigitalWorld."""

    def __init__(self, controller: AdventureController, asset_root: Path | None = None,
                 inspector: PolicyInspector | None = None,
                 dashboard: AcademicDashboard | None = None,
                 audio_settings_path: Path | None = None):
        self.controller = controller
        self.inspector = inspector
        self.dashboard = dashboard
        self.results_metric_index = 0
        self.demo_index = 0
        self.dex_filter = "all"
        self.dex_index = 0
        self.dex_source_notice = False
        self.summary_page = 0
        self.analysis_from_summary = False
        self.effect_index = 0
        self.effect_elapsed = 0
        self.inspection_history: list[GameState] = [controller.world.start_state()]
        self.inspection_index = 0
        self.presentation = GamePresentation()
        self.notice_ticks = 0
        self.cue_ticks = 0
        self.last_cue = ""
        self.title_scene: pygame.Surface | None = None
        self.sprites = SpriteManager(find_asset_root(asset_root))
        self.effects = EffectSprites(self.sprites.root)
        self.map_renderer = WorldMapRenderer()
        self.audio = AudioManager(self.sprites.root/'audio',audio_settings_path)
        self.audio_timeline = SoundTimeline(())
        self.region_transition: RegionTransition | None = None
        self.outcome_sound_played = False
        self.combat_animation: CombatAnimation | None = None
        self.animation_speed = 1  # 1 normal, 2 rápida, 0 sin animación
        self.scene_cache: dict[tuple[Zone, tuple[int, int]], pygame.Surface] = {}
        self.fx_ticks = 0
        self.fx_kind: Action | None = None
        self.running = True
        self.auto = False
        self.auto_interval_ms = 690
        self.elapsed = 0
        self.buttons: list[HitBox] = []
        self.last_mouse = (0, 0)
        self.frames = 0
        self.screen: pygame.Surface | None = None
        self.window: pygame.Surface | None = None
        self.viewport = Viewport(WIDTH, HEIGHT)
        self.fullscreen = False
        self.windowed_size = (WIDTH, HEIGHT)
        self.font_cache: dict[tuple[int, int], pygame.font.Font] = {}
        self.tooltips: list[tuple[pygame.Rect, str]] = []

    def initialize(self, window_size: tuple[int, int] | None = None) -> None:
        """Inicializa SDL y una superficie lógica independiente de la ventana."""
        pygame.init()
        self.audio.initialize()
        self._sync_audio_pause()
        info = pygame.display.Info()
        if window_size is None:
            # Reserva espacio para barra de tareas y bordes en notebooks Windows.
            scale = min(1.0, max(320, info.current_w-80)/WIDTH,
                        max(240, info.current_h-100)/HEIGHT)
            window_size = (round(WIDTH*scale), round(HEIGHT*scale))
        self.windowed_size = window_size
        self.window = pygame.display.set_mode(window_size, pygame.RESIZABLE)
        self.screen = pygame.Surface((WIDTH, HEIGHT)).convert()
        self.viewport = Viewport(*self.window.get_size())
        pygame.display.set_caption("Digimon RPG | La corrupción del Mundo Digital - RL v0.22")
        self.clock = pygame.time.Clock()
        self.small = pygame.font.SysFont("segoeui,verdana,arial", 15)
        self.body = pygame.font.SysFont("segoeui,verdana,arial", 18)
        self.title = pygame.font.SysFont("segoeui,verdana,arial", 27, bold=True)
        self.big_title = pygame.font.SysFont("segoeui,verdana,arial", 70, bold=True)
        self.subtitle = pygame.font.SysFont("segoeui,verdana,arial", 22, bold=True)
        self.tiny = pygame.font.SysFont("segoeui,verdana,arial", 13)
        self._build_background()

    def _present_frame(self) -> None:
        assert self.window is not None and self.screen is not None
        self.viewport = Viewport(*self.window.get_size())
        self.window.fill(BG)
        size = self.viewport.size
        canvas = self.screen if size == (WIDTH, HEIGHT) else pygame.transform.smoothscale(self.screen, size)
        self.window.blit(canvas, self.viewport.origin)
        pygame.display.flip()

    def _toggle_fullscreen(self) -> None:
        assert self.window is not None
        if not self.fullscreen:
            self.windowed_size = self.window.get_size()
        self.fullscreen = not self.fullscreen
        self.window = pygame.display.set_mode((0, 0) if self.fullscreen else self.windowed_size,
                                              pygame.FULLSCREEN if self.fullscreen else pygame.RESIZABLE)
        self.viewport = Viewport(*self.window.get_size())

    def _pointer(self, point: tuple[int, int]) -> tuple[int, int]:
        return self.viewport.to_logical(point) or (-1, -1)

    def run(self, max_frames: int | None = None) -> None:
        try:
            self.initialize()
            while self.running:
                delta = self.clock.tick(FPS)
                self.frames += 1
                if self.presentation.screen == Screen.GAME:
                    self.fx_ticks = max(0, self.fx_ticks - 1)
                self._update_combat_visuals(delta)
                if not self.transition_busy:
                    self.notice_ticks = max(0, self.notice_ticks - 1)
                self.cue_ticks = max(0, self.cue_ticks - 1)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_F11:
                            self._toggle_fullscreen()
                        else:
                            self._on_key(event.key)
                    elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        self._on_click(self._pointer(event.pos))
                    elif event.type == pygame.VIDEORESIZE and not self.fullscreen:
                        self.window = pygame.display.set_mode((max(320, event.w), max(240, event.h)), pygame.RESIZABLE)
                        self.viewport = Viewport(*self.window.get_size())
                if self.presentation.screen == Screen.EFFECTS:
                    self.effect_elapsed += delta
                self.last_mouse = self._pointer(pygame.mouse.get_pos())
                if (self.presentation.screen == Screen.GAME and self.auto
                        and self.controller.mode != ControlMode.MANUAL and not self.controller.finished
                        and self.notice_ticks <= 0 and not self.presentation_busy):
                    self.elapsed += delta
                    if self.elapsed >= self.auto_interval_ms:
                        self.elapsed = 0
                        self._advance()
                if self.controller.finished:
                    self.auto = False
                self.draw()
                self._draw_tooltip()
                self._present_frame()
                if max_frames is not None and self.frames >= max_frames:
                    self.running = False
        finally:
            pygame.quit()

    def _build_background(self) -> None:
        self.background = pygame.Surface((WIDTH, HEIGHT))
        for y in range(HEIGHT):
            t = y / HEIGHT
            color = (int(12 + 7 * t), int(18 + 5 * t), int(35 + 13 * t))
            pygame.draw.line(self.background, color, (0, y), (WIDTH, y))
        # Constelación original de pequeños píxeles, determinista.
        for i in range(145):
            x = (i * 191 + 47) % WIDTH
            y = (i * 137 + 31) % HEIGHT
            if y < 106 or (x > 785 and y > 575):
                pygame.draw.circle(self.background, (47, 75, 103), (x, y), 1)

    @property
    def animation_busy(self) -> bool:
        # Los tests del controlador sin ventana no necesitan esperar al render.
        return self.screen is not None and self.combat_animation is not None and self.combat_animation.active

    @property
    def transition_busy(self) -> bool:
        seq = self.region_transition
        report = self.controller.last_report
        return (self.screen is not None and seq is not None and seq.active
                and report is not None and report.step is seq.step)

    @property
    def presentation_busy(self) -> bool:
        return self.animation_busy or self.transition_busy

    def _sync_audio_pause(self) -> None:
        self.audio.set_paused(self.presentation.screen != Screen.GAME)
        if self.presentation.screen != Screen.EFFECTS:
            self.audio.stop_preview()

    def _play_outcome_sound(self) -> None:
        if (not self.outcome_sound_played and not self.presentation_busy
                and self.controller.last_report is not None
                and isinstance(self.controller.state,Ending)):
            self.audio.play('victory' if self.controller.state == Ending.WIN else 'loss','event')
            self.outcome_sound_played = True

    def _finish_turn_presentation(self) -> None:
        if self.combat_animation is not None:
            self.combat_animation.finish()
        if self.region_transition is not None:
            self.region_transition.finish()
        self.audio_timeline.discard()
        self.audio.stop_gameplay()
        self.fx_ticks = 0
        self._play_outcome_sound()

    def _update_combat_visuals(self, delta_ms: int) -> None:
        self._sync_audio_pause()
        if self.presentation.screen != Screen.GAME:
            return
        seq = self.combat_animation if self.animation_busy else self.region_transition if self.transition_busy else None
        if seq is not None:
            if self.animation_speed == 0:
                self._finish_turn_presentation()
            else:
                seq.update(max(0,delta_ms)*self.animation_speed)
                for cue in self.audio_timeline.advance(seq.elapsed_ms):
                    self.audio.play(cue.name,cue.group,cue.gain)
        self._play_outcome_sound()

    def _on_key(self, key: int) -> None:
        audio_keys = {getattr(pygame,'K_F8',-10008):'audio_mute',
                      getattr(pygame,'K_F9',-10009):'audio_down',
                      getattr(pygame,'K_F10',-10010):'audio_up'}
        if key in audio_keys:
            self._command(audio_keys[key])
            return
        self._handle_key(key)
        self._sync_audio_pause()

    def _handle_key(self, key: int) -> None:
        screen = self.presentation.screen
        if key == getattr(pygame, "K_F7", -10007):
            self._command("back" if screen == Screen.DIGIDEX else "digidex")
            return
        if key == getattr(pygame, "K_TAB", -10009):
            self._command("back" if screen == Screen.SUMMARY else "summary")
            return
        if screen == Screen.DIGIDEX:
            if key in (pygame.K_ESCAPE,pygame.K_RETURN): self._command("back")
            elif key in (pygame.K_RIGHT,pygame.K_DOWN): self._command("dex_shift",1)
            elif key in (pygame.K_LEFT,pygame.K_UP): self._command("dex_shift",-1)
            return
        if screen == Screen.SUMMARY or screen == Screen.GAME and self.controller.finished and not self.presentation_busy:
            if key == pygame.K_ESCAPE:self._command("title" if self.controller.finished else "back")
            elif key == pygame.K_r:self._command("reset")
            elif key == pygame.K_RIGHT:self._command("summary_shift",1)
            elif key == pygame.K_LEFT:self._command("summary_shift",-1)
            elif key == pygame.K_m:self._command("title")
            elif key == pygame.K_t:
                moments=summarize(self.controller).moments[self.summary_page*4:self.summary_page*4+4]
                if moments:self._command("summary_inspect",moments[0].index)
            elif key == getattr(pygame,"K_F4",-10004):self._command("results")
            elif key == getattr(pygame,"K_F5",-10005):self._command("demo")
            elif key == getattr(pygame,"K_F6",-10006):self._command("effects")
            elif self.controller.finished and key in (pygame.K_F1,pygame.K_F2,pygame.K_F3):
                self._command("mode",{pygame.K_F1:ControlMode.DYNAMIC_PROGRAMMING,
                    pygame.K_F2:ControlMode.MONTE_CARLO,pygame.K_F3:ControlMode.MANUAL}[key])
            return
        if key == getattr(pygame, "K_F6", -10006) and screen != Screen.EFFECTS:
            self._command("effects")
            return
        if screen == Screen.EFFECTS:
            if key in (pygame.K_ESCAPE, getattr(pygame, "K_F6", -10006)):
                self.presentation.close()
            elif key == pygame.K_RIGHT:
                self._command("effect_shift", 1)
            elif key == pygame.K_LEFT:
                self._command("effect_shift", -1)
            elif key in (pygame.K_SPACE, pygame.K_RETURN):
                self.effect_elapsed = 0
            return
        if screen == Screen.RESULTS:
            if key in (pygame.K_ESCAPE, getattr(pygame, "K_F4", -10004), pygame.K_RETURN):
                self.presentation.close()
            elif key in (pygame.K_RIGHT, pygame.K_DOWN):
                self._command("metric_shift", 1)
            elif key in (pygame.K_LEFT, pygame.K_UP):
                self._command("metric_shift", -1)
            elif key == getattr(pygame, "K_F5", -10005):
                self._command("demo")
            return
        if screen == Screen.DEMO:
            if key in (pygame.K_ESCAPE, getattr(pygame, "K_F5", -10005)):
                self.presentation.close()
            elif key in (pygame.K_RIGHT, pygame.K_SPACE, pygame.K_RETURN):
                self._command("demo_shift", 1)
            elif key == pygame.K_LEFT:
                self._command("demo_shift", -1)
            elif key == pygame.K_F1:
                self._command("start", ControlMode.DYNAMIC_PROGRAMMING)
            elif key == pygame.K_F2:
                self._command("start", ControlMode.MONTE_CARLO)
            elif key == getattr(pygame, "K_F4", -10004):
                self._command("results")
            return
        if screen == Screen.ANALYSIS:
            if key in (pygame.K_t, pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE):
                self._command("back")
            elif key == pygame.K_LEFT:
                self._command("analysis_shift", -1)
            elif key == pygame.K_RIGHT:
                self._command("analysis_shift", 1)
            return
        if screen in (Screen.HELP, Screen.CREDITS, Screen.PAUSE):
            if key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE,
                       pygame.K_h, pygame.K_p, pygame.K_c):
                self.presentation.close()
            return
        if screen == Screen.TITLE:
            if key == pygame.K_ESCAPE:
                self.running = False
            elif key in (pygame.K_RETURN, pygame.K_SPACE):
                self._command("start", self.controller.mode)
            elif key in (pygame.K_F1, pygame.K_F2, pygame.K_F3):
                self._command("start", {
                    pygame.K_F1: ControlMode.DYNAMIC_PROGRAMMING,
                    pygame.K_F2: ControlMode.MONTE_CARLO,
                    pygame.K_F3: ControlMode.MANUAL,
                }[key])
            elif key == getattr(pygame, "K_F4", -10004):
                self._command("results")
            elif key == getattr(pygame, "K_F5", -10005):
                self._command("demo")
            elif key == pygame.K_h:
                self._command("help")
            elif key == pygame.K_c:
                self._command("credits")
            return
        if key == pygame.K_ESCAPE or key == pygame.K_m:
            self._command("title")
        elif key == pygame.K_h:
            self._command("help")
        elif key == pygame.K_c:
            self._command("credits")
        elif key == pygame.K_p:
            self._command("pause")
        elif key == pygame.K_t:
            self._command("analysis")
        elif key == getattr(pygame, "K_F4", -10004):
            self._command("results")
        elif key == getattr(pygame, "K_F5", -10005):
            self._command("demo")
        elif key in (pygame.K_F1, pygame.K_F2, pygame.K_F3):
            mode = {
                pygame.K_F1: ControlMode.DYNAMIC_PROGRAMMING,
                pygame.K_F2: ControlMode.MONTE_CARLO,
                pygame.K_F3: ControlMode.MANUAL,
            }[key]
            self._command("mode", mode)
        elif key == pygame.K_r:
            self._command("reset")
        elif key == pygame.K_a:
            self._command("auto")
        elif key == getattr(pygame, "K_v", -10022):
            self._command("animation_speed")
        elif key in (pygame.K_SPACE, pygame.K_RETURN):
            if self.presentation_busy:
                self._command("skip_animation")
            elif self.notice_ticks > 0:
                self.notice_ticks = 0
            else:
                self._command("next")
        elif key in (pygame.K_PLUS, pygame.K_EQUALS, pygame.K_KP_PLUS):
            self.auto_interval_ms = max(180, self.auto_interval_ms - 100)
        elif key in (pygame.K_MINUS, pygame.K_KP_MINUS):
            self.auto_interval_ms = min(1700, self.auto_interval_ms + 100)
        elif key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6, pygame.K_7):
            if self.controller.mode == ControlMode.MANUAL and not self.controller.finished:
                index = key - pygame.K_1
                if index < len(self.controller.legal_actions):
                    self._command("action", self.controller.legal_actions[index])

    def _on_click(self, pos: tuple[int, int]) -> None:
        for box in reversed(self.buttons):
            if box.rect.collidepoint(pos):
                self._command(box.command, box.value)
                return

    def _new_adventure(self, mode: ControlMode | None = None) -> None:
        self.auto = False
        self.elapsed = 0
        self.fx_ticks = 0
        self.combat_animation = None
        self.region_transition = None
        self.audio_timeline = SoundTimeline(())
        self.outcome_sound_played = False
        self.audio.stop_gameplay(); self.audio.stop_preview()
        self.cue_ticks = 0
        self.summary_page = 0
        self.analysis_from_summary = False
        self.controller.reset(mode)
        self.inspection_history = [self.controller.world.start_state()]
        self.inspection_index = 0
        self.presentation.start(self.controller.mode)
        self.notice_ticks = 160

    def _command(self, command: str, value: object = None) -> None:
        if command in ("title","start","mode","analysis","effects","results","demo"):
            self.analysis_from_summary=False
        if command in ("action", "next") and self.presentation_busy:
            return
        if command not in ('audio_mute','audio_down','audio_up','audio_test','effect_listen'):
            self.audio.play('ui','ui')
        if command == "start" or command == "mode":
            self._new_adventure(ControlMode(value))
        elif command == "title":
            self.auto = False
            self.presentation.title()
            self.notice_ticks = 0
        elif command == "help":
            self.auto = False
            self.presentation.open(Screen.HELP)
        elif command == "credits":
            self.auto = False
            self.presentation.open(Screen.CREDITS)
        elif command == "pause":
            self.auto = False
            self.presentation.open(Screen.PAUSE)
        elif command == "analysis":
            if self.presentation.screen == Screen.GAME:
                self.auto = False
                self.inspection_index = len(self.inspection_history) - 1
                self.presentation.open(Screen.ANALYSIS)
        elif command == "digidex":
            self.auto = False
            self.analysis_from_summary = False
            self.presentation.open(Screen.DIGIDEX)
        elif command == "dex_filter":
            if value in ("all","heroes","enemies"):
                self.dex_filter = value; self.dex_index = 0
        elif command in ("dex_shift","dex_select"):
            self.dex_index = (self.dex_index+int(value) if command=="dex_shift" else int(value)) % len(self._dex_entries())
            self.dex_source_notice = False
        elif command == "dex_source":
            if self.presentation.screen == Screen.DIGIDEX:
                import webbrowser
                entry = self._dex_entries()[self.dex_index % len(self._dex_entries())]
                try:self.dex_source_notice = not webbrowser.open(entry.source_url)
                except OSError:self.dex_source_notice = True
        elif command == "summary":
            self.auto = False
            self.analysis_from_summary = False
            self.presentation.open(Screen.SUMMARY)
        elif command == "summary_shift":
            count=len(summarize(self.controller).moments)
            self.summary_page = max(0,min(max(0,(count-1)//4),self.summary_page+int(value)))
        elif command == "summary_inspect":
            index=int(value)
            if 0 <= index < len(self.controller.decisions):
                self.auto=False
                if self.presentation.screen != Screen.SUMMARY:self.presentation.open(Screen.SUMMARY)
                self.inspection_history=[r.step.state for r in self.controller.decisions]
                if isinstance(self.controller.state,GameState):self.inspection_history.append(self.controller.state)
                self.inspection_index=index
                self.analysis_from_summary=True
                self.presentation.screen=Screen.ANALYSIS
        elif command == "effects":
            self.auto = False
            self.effect_elapsed = 0
            self.presentation.open(Screen.EFFECTS)
        elif command in ("effect_shift", "effect_select"):
            self.audio.stop_preview()
            self.effect_index = ((self.effect_index+int(value)) if command == "effect_shift" else int(value)) % len(ALL_EFFECTS)
            self.effect_elapsed = 0
        elif command == "effect_replay":
            self.effect_elapsed = 0
        elif command == "effect_listen":
            self.audio.play(ALL_EFFECTS[self.effect_index],'preview')
        elif command == "audio_mute":
            self.audio.toggle_mute()
            self.audio.play('ui','ui')
        elif command in ("audio_down","audio_up"):
            self.audio.change_volume(-.1 if command=='audio_down' else .1)
            self.audio.play('ui','ui')
        elif command == "audio_test":
            self.audio.play('baby_flame','ui')
        elif command == "results":
            self.auto = False
            # Si estamos en otro modal, volvemos primero al origen real.
            if self.presentation.screen == Screen.DEMO:
                self.presentation.close()
            self.presentation.open(Screen.RESULTS)
        elif command == "metric_shift":
            self.results_metric_index = max(0, min(len(METRICS)-1,
                                                  self.results_metric_index + int(value)))
        elif command == "metric_select":
            self.results_metric_index = max(0, min(len(METRICS)-1, int(value)))
        elif command == "demo":
            self.auto = False
            if self.presentation.screen == Screen.RESULTS:
                self.presentation.close()
            self.demo_index = 0
            self.presentation.open(Screen.DEMO)
        elif command == "demo_shift":
            max_page = len(self.dashboard.slides())-1 if self.dashboard else 0
            self.demo_index = max(0, min(max_page, self.demo_index + int(value)))
        elif command == "analysis_shift":
            self.inspection_index = max(0, min(len(self.inspection_history)-1,
                                               self.inspection_index + int(value)))
        elif command == "back":
            if self.presentation.screen==Screen.ANALYSIS and self.analysis_from_summary:
                self.presentation.screen=Screen.SUMMARY
                self.analysis_from_summary=False
            elif self.presentation.screen==Screen.SUMMARY and self.controller.finished:
                self.presentation.title()
            else:self.presentation.close()
        elif command == "reset":
            self._new_adventure()
        elif command == "auto":
            if (self.presentation.screen == Screen.GAME and
                    self.controller.mode != ControlMode.MANUAL and not self.controller.finished):
                self.auto = not self.auto
                self.elapsed = 0
                # El aviso de zona sigue visible si se inicia automático.
        elif command == "animation_speed":
            self.animation_speed = {1: 2, 2: 0, 0: 1}[self.animation_speed]
            if self.animation_speed == 0:
                self._finish_turn_presentation()
        elif command == "skip_animation":
            self._finish_turn_presentation()
        elif command == "next":
            if self.controller.mode != ControlMode.MANUAL and not self.controller.finished:
                self.auto = False
                self._advance()
        elif command == "action":
            # Un doble clic puede conservar un botón de la imagen anterior.
            # Se vuelve a comprobar la legalidad antes de consumir el turno.
            if (self.controller.mode == ControlMode.MANUAL and not self.controller.finished
                    and Action(value) in self.controller.legal_actions):
                self._advance(Action(value))
        elif command == "dismiss_notice":
            self.notice_ticks = 0
        elif command == "exit":
            self.running = False
        self._sync_audio_pause()

    def _advance(self, action: Action | None = None) -> None:
        report = self.controller.advance(action)
        self.combat_animation = CombatAnimation.from_step(report.step)
        self.region_transition = RegionTransition.from_step(report.step)
        self.outcome_sound_played = False
        self.audio.stop_gameplay()
        if self.combat_animation is not None:
            cues = combat_cues(self.combat_animation)
        elif self.region_transition is not None:
            cues = (SoundCue(0,'travel'),)
            if report.step.next_state.hp < report.step.state.hp:
                cues += (SoundCue(280,'impact','impact',.7),)
        else:
            cues = ()
        self.audio_timeline = SoundTimeline(cues)
        self._sync_audio_pause()
        # Historial para inspeccionar decisiones previas; no modifica el MDP.
        if isinstance(report.step.next_state, GameState):
            self.inspection_history.append(report.step.next_state)
        else:
            # El último estado inspeccionable es el anterior al terminal.
            self.inspection_history.append(report.step.state)
        self.inspection_index = len(self.inspection_history) - 1
        self.fx_kind = report.step.action
        self.fx_ticks = 22 if report.step.action == Action.DIGIVOLVE else 13
        if self.animation_speed == 0:
            if self.combat_animation is not None:
                self.combat_animation.finish()
            self.fx_ticks = 0
            if self.region_transition is not None:
                self.region_transition.finish()
            self.audio_timeline.discard()
            if cues:
                self.audio.play(cues[0].name,cues[0].group,cues[0].gain)
        event = self.presentation.on_transition(
            report.step.state, report.step.action, report.step.next_state)
        if event is not None:
            self.notice_ticks = 130 if not report.finished else 0
        self.last_cue = f"{ACTION_LABELS[report.step.action]}    {report.step.reward:+.0f} recompensa"
        self.cue_ticks = 52
        self._play_outcome_sound()

    def _text(self, value: object, x: int, y: int, *, font=None, color=WHITE,
              center: bool = False) -> None:
        face = font or self.body
        text = face.render(str(value), True, color)
        rect = text.get_rect()
        if center:
            rect.center = (x, y)
        else:
            rect.topleft = (x, y)
        assert self.screen is not None
        self.screen.blit(text, rect)

    def _panel(self, rect: pygame.Rect) -> None:
        assert self.screen is not None
        pygame.draw.rect(self.screen, PANEL, rect, border_radius=22)
        pygame.draw.rect(self.screen, (51, 75, 103), rect, 1, border_radius=22)

    def _button(self, rect: pygame.Rect, title: str, command: str, value=None,
                selected: bool = False, enabled: bool = True, accent=CYAN,
                size: str = "body") -> None:
        assert self.screen is not None
        active = enabled and rect.collidepoint(self.last_mouse)
        background = ((45, 82, 101) if active else (37, 67, 89)) if selected else (
            (46, 63, 85) if active else PANEL_LIGHT)
        border = accent if selected else ((80, 112, 134) if enabled else (47, 59, 73))
        pygame.draw.rect(self.screen, background, rect, border_radius=11)
        pygame.draw.rect(self.screen, border, rect, 2 if selected else 1, border_radius=11)
        face = self._fit_font(title, self.small if size == "small" else self.body, rect.width-18)
        self._text(title, rect.centerx, rect.centery, font=face,
                   color=WHITE if enabled else (98, 116, 131), center=True)
        if enabled:
            self.buttons.append(HitBox(rect, command, value))
            self.tooltips.append((rect, title))

    def _fit_font(self, text: str, font, width: int):
        if font.size(text)[0] <= width:
            return font
        # Cache por tamaño objetivo y fuente; el ajuste final usa el ancho real.
        size = max(10, round(font.get_height() * min(1, width/font.size(text)[0]) * .8))
        cache_key = (id(font), size)
        if cache_key not in self.font_cache:
            self.font_cache[cache_key] = pygame.font.SysFont("segoeui,verdana,arial", size)
        return self.font_cache[cache_key]

    def _draw_tooltip(self) -> None:
        if not self.screen:
            return
        for rect, text in reversed(self.tooltips):
            if rect.collidepoint(self.last_mouse):
                w = min(WIDTH-40, self.small.size(text)[0]+28)
                x = min(WIDTH-w-12, max(12, rect.centerx-w//2))
                y = max(8, rect.top-42)
                pygame.draw.rect(self.screen, (7, 18, 32), (x, y, w, 34), border_radius=8)
                pygame.draw.rect(self.screen, CYAN, (x, y, w, 34), 1, border_radius=8)
                self._text(text, x+14, y+8, font=self.small)
                break

    def _bar(self, x: int, y: int, width: int, ratio: float, color: tuple[int, int, int],
             trail_ratio: float | None = None) -> None:
        assert self.screen is not None
        ratio = min(1.0, max(0.0, ratio))
        pygame.draw.rect(self.screen, (45, 58, 75), (x, y, width, 13), border_radius=6)
        if trail_ratio is not None and trail_ratio > ratio:
            trail = round(width * min(1., trail_ratio))
            if trail > 0:
                pygame.draw.rect(self.screen, (189, 143, 93), (x, y, trail, 13), border_radius=6)
        filled = round(width * ratio)
        if filled > 0:
            pygame.draw.rect(self.screen, color, (x, y, filled, 13), border_radius=6)

    def _draw_header(self) -> None:
        self._text("DIGIMON", 31, 17, font=self.title, color=CYAN)
        self._text("LA CORRUPCIÓN DEL MUNDO DIGITAL", 32, 57, font=self.small, color=MUTED)
        self._text("MDP / POO / RL", 405, 29, font=self.small, color=(120, 154, 178))
        self._button(pygame.Rect(404, 49, 125, 28), "F4 Resultados", "results", size="small")
        self._button(pygame.Rect(536, 49, 125, 28), "F5 Presentación", "demo", size="small")
        self._button(pygame.Rect(404, 80, 125, 24), "F7 Digidex", "digidex", size="small")
        self._button(pygame.Rect(536, 80, 125, 24), "Tab Diario", "summary", size="small")
        controls = [
            ("F1   Value Iteration", ControlMode.DYNAMIC_PROGRAMMING),
            ("F2   Monte Carlo", ControlMode.MONTE_CARLO),
            ("F3   Manual", ControlMode.MANUAL),
        ]
        x = 704
        for label, mode in controls:
            w = 180 if mode == ControlMode.DYNAMIC_PROGRAMMING else 166
            self._button(pygame.Rect(x, 25, w, 45), label, "mode", mode,
                         selected=self.controller.mode == mode, size="small")
            x += w + 9
        speed_label = {1: "normal", 2: "rápida ×2", 0: "sin animación"}[self.animation_speed]
        self._button(pygame.Rect(704, 77, 238, 24), "V  Animación: " + speed_label,
                     "animation_speed", size="small", accent=PURPLE)
        self._button(pygame.Rect(951, 77, 295, 24), "Espacio · Omitir animación",
                     "skip_animation", size="small", enabled=self.presentation_busy)

    def _map_view(self, state: GameState) -> WorldMapView:
        return WorldMapView.build(state,self.inspection_history,self.controller.visited_zones,
                                 self.controller.legal_actions,
                                 can_choose=(self.presentation.screen == Screen.GAME
                                     and self.controller.mode == ControlMode.MANUAL
                                     and not self.controller.finished and not self.presentation_busy))

    def _draw_map(self, state: GameState) -> None:
        self._panel(pygame.Rect(28,108,755,471))
        self._text("MAPA DEL MUNDO DIGITAL",52,128,font=self.subtitle)
        view = self._map_view(state)
        visited = f"{len(view.visited)}/{len(Zone)} VISITADAS"
        self._text(visited,655,137,font=self.tiny,color=CYAN)
        if self.presentation_busy:
            hint = "Mostrando el turno · Espacio para omitir la animación."
        elif self.controller.mode != ControlMode.MANUAL:
            hint = "Sigue el recorrido del agente · las rutas se eligen según su política."
        elif state.enemy_hp > 0:
            hint = "Derrota al guardián para abrir la siguiente ruta."
        elif view.destinations:
            hint = "Elige una ruta iluminada · Buscar recursos se decide en el panel."
        else:
            hint = "Avanza desde el panel para completar la aventura."
        self._text(hint,52,162,font=self._fit_font(hint,self.small,705),color=MUTED)
        for hotspot in self.map_renderer.draw(self,state,view):
            self.tooltips.append((hotspot.rect,hotspot.tooltip))
            if hotspot.action is not None:
                self.buttons.append(HitBox(hotspot.rect,"action",hotspot.action))

    def _draw_hero(self, cx: int, cy: int, evolved: int) -> None:
        """Carga la forma evolutiva del personaje o usa un respaldo local."""
        assert self.screen is not None
        wobble = int(3 * math.sin(self.frames / 15))
        cy += wobble
        sprite = self.sprites.sprite(HERO_SPRITES[evolved], (164, 164))
        if sprite is not None:
            if self.fx_ticks and self.fx_kind == Action.DIGIVOLVE:
                radius = 63 + int(9 * math.sin(self.frames / 2))
                pygame.draw.circle(self.screen, GOLD, (cx, cy), radius, 3)
                pygame.draw.circle(self.screen, CYAN, (cx, cy), radius + 11, 2)
            self._blit_combatant(sprite, (cx, cy), "hero")
            return
        self._draw_hero_placeholder(cx, cy, evolved)

    def _draw_hero_placeholder(self, cx: int, cy: int, evolved: int) -> None:
        """Ilustración original generada por código: fallback sin PNG."""
        assert self.screen is not None
        orange = (248, 161, 74) if not evolved else (238, 135, 83)
        light = (255, 205, 115)
        dark = (158, 86, 75)
        # Cola dentada, cuerpo, patas y garras.
        pygame.draw.polygon(self.screen, dark, [(cx - 37, cy + 15), (cx - 96, cy - 12),
                            (cx - 78, cy + 23), (cx - 108, cy + 26), (cx - 45, cy + 61)])
        pygame.draw.ellipse(self.screen, orange, (cx - 54, cy - 20, 105, 113))
        pygame.draw.ellipse(self.screen, light, (cx - 25, cy + 30, 54, 47))
        pygame.draw.ellipse(self.screen, orange, (cx - 72, cy - 83, 131, 94))
        pygame.draw.polygon(self.screen, orange, [(cx-48, cy-55), (cx-45, cy-117),
                            (cx-17, cy-78)])
        pygame.draw.polygon(self.screen, orange, [(cx+12, cy-78), (cx+33, cy-112),
                            (cx+42, cy-48)])
        if evolved:
            for dx in (-29, -5, 20):
                pygame.draw.polygon(self.screen, light, [(cx+dx,cy-91),
                                    (cx+dx+4,cy-123), (cx+dx+17,cy-88)])
            pygame.draw.polygon(self.screen, (204, 228, 218), [(cx-55,cy-80),
                                (cx-23,cy-98), (cx+43,cy-75), (cx+51,cy-53),
                                (cx-46,cy-55)])
        pygame.draw.ellipse(self.screen, (253, 237, 224), (cx+5, cy-50, 20, 25))
        pygame.draw.ellipse(self.screen, (41, 42, 59), (cx+15, cy-43, 8, 17))
        pygame.draw.circle(self.screen, dark, (cx+46, cy-22), 5)
        pygame.draw.arc(self.screen, dark, (cx+3,cy-30,51,30), 0, 2.2, 3)
        for dx in (-38, 31):
            pygame.draw.ellipse(self.screen, orange, (cx+dx-15, cy+73, 29, 23))
            pygame.draw.polygon(self.screen, light, [(cx+dx,cy+90), (cx+dx+7,cy+105),
                                (cx+dx+13,cy+89)])

    def _draw_enemy(self, cx: int, cy: int, zone: Zone) -> None:
        assert self.screen is not None
        wobble = int(2 * math.sin(self.frames / 21 + 1))
        cy += wobble
        sprite = self.sprites.sprite(ENEMY_SPRITES.get(zone, ""), (158, 161), mirror=zone != Zone.ABYSS)
        if sprite is not None:
            self._blit_combatant(sprite, (cx, cy), "enemy")
            return
        self._draw_enemy_placeholder(cx, cy, zone)

    def _blit_combatant(self, sprite: pygame.Surface, center: tuple[int, int], actor: str) -> None:
        """Destello breve y desplazamiento local; nunca modifica el PNG ni usa RNG."""
        assert self.screen is not None
        seq = self.combat_animation if self.animation_busy else None
        flash = seq.feedback.flash_for(seq.beats, seq.elapsed_ms, actor) if seq else None
        if flash:
            sprite = sprite.copy()
            sprite.fill((110,160,110,0) if flash == "heal" else (160,120,120,0),
                        special_flags=pygame.BLEND_RGBA_ADD)
            if flash == "damage":
                center = (center[0] + (3 if (seq.elapsed_ms//45)%2 else -3), center[1])
        self.screen.blit(sprite, sprite.get_rect(center=center))

    def _draw_enemy_placeholder(self, cx: int, cy: int, zone: Zone) -> None:
        assert self.screen is not None
        colors = {
            Zone.FOREST: (101, 194, 131), Zone.CAVE: (217, 144, 110),
            Zone.SWAMP: (100, 182, 167), Zone.RUINS: (152, 139, 215),
            Zone.FORTRESS: (184, 94, 162),
        }
        color = colors.get(zone, PURPLE)
        pygame.draw.polygon(self.screen, (53, 44, 77), [(cx-55,cy+41),(cx-72,cy-65),
                            (cx-33,cy-34),(cx-20,cy-97),(cx+3,cy-59),
                            (cx+35,cy-86),(cx+57,cy+32)])
        pygame.draw.ellipse(self.screen, color, (cx-66,cy-52,132,139))
        pygame.draw.polygon(self.screen, (54, 47, 83), [(cx-64,cy-35),
                            (cx-85,cy-8),(cx-60,cy+25)])
        pygame.draw.polygon(self.screen, (54, 47, 83), [(cx+64,cy-35),
                            (cx+85,cy-8),(cx+60,cy+25)])
        for offset in (-24, 22):
            pygame.draw.ellipse(self.screen, (247, 230, 200), (cx+offset-12,cy-15,24,32))
            pygame.draw.circle(self.screen, (48, 42, 67), (cx+offset,cy-2), 8)
        pygame.draw.arc(self.screen, (53, 48, 73), (cx-25,cy+23,50,29), 3.25, 6.2, 4)
        pygame.draw.polygon(self.screen, (245, 227, 226), [(cx-11,cy+47),
                            (cx-3,cy+64),(cx+4,cy+45)])

    def _scene_background(self, zone: Zone, size: tuple[int, int]) -> pygame.Surface:
        """Fondo local si existe o escenario procedural diferenciado por región."""
        custom = self.sprites.background(BACKGROUND_NAMES[zone], size)
        if custom is not None:
            return custom
        cache_key = (zone, size)
        if cache_key in self.scene_cache:
            return self.scene_cache[cache_key]
        w, h = size
        palette = {
            Zone.REFUGE: ((20,90,87),(60,160,142),(30,92,76)),
            Zone.ABYSS: ((35,10,72),(109,25,139),(51,26,84)),
            Zone.VILLAGE: ((41, 105, 146), (90, 166, 155), (45, 110, 83)),
            Zone.FOREST: ((23, 87, 101), (51, 145, 121), (25, 88, 68)),
            Zone.CAVE: ((62, 53, 91), (133, 90, 99), (71, 61, 84)),
            Zone.SWAMP: ((26, 79, 86), (64, 117, 105), (34, 77, 76)),
            Zone.RUINS: ((66, 68, 119), (132, 111, 142), (68, 63, 96)),
            Zone.TOWER: ((35, 63, 89), (71, 145, 153), (42, 76, 87)),
            Zone.FORTRESS: ((77, 40, 77), (145, 60, 88), (68, 43, 82)),
        }
        top, bottom, ground = palette[zone]
        canvas = pygame.Surface(size)
        for y in range(h):
            frac = y / h
            col = tuple(round(top[k] * (1 - frac) + bottom[k] * frac) for k in range(3))
            pygame.draw.line(canvas, col, (0, y), (w, y))
        pygame.draw.ellipse(canvas, ground, (-70, h-65, w + 170, 120))
        pygame.draw.ellipse(canvas, tuple(min(255, k+18) for k in ground),
                           (0, h-29, w, 70))
        if zone in (Zone.FOREST, Zone.SWAMP, Zone.VILLAGE):
            for x in (16, 83, 140, 208, 279, 376):
                y = 113 + ((x * 17) % 36)
                pygame.draw.rect(canvas, (40, 63, 67), (x, y, 11, h-y))
                pygame.draw.polygon(canvas, (22, 92, 82),
                                    [(x - 27, y + 12), (x + 5, y-53), (x+37, y+12)])
                pygame.draw.polygon(canvas, (36, 118, 94),
                                    [(x - 25, y-8), (x+5, y-72), (x+34,y-8)])
        elif zone == Zone.CAVE:
            for x in range(15, w, 50):
                pygame.draw.polygon(canvas, (45, 36, 75),
                                    [(x-16, 0), (x+31,0), (x+11, 82+(x*7)%50)])
                pygame.draw.polygon(canvas, (75, 63, 97),
                                    [(x-22,h), (x+36,h), (x+9,h-70-(x*3)%33)])
        elif zone == Zone.RUINS:
            for x in (25, 112, 240, 335):
                pygame.draw.rect(canvas, (91, 90, 119), (x, 68, 31, 114))
                pygame.draw.rect(canvas, (151, 139, 153), (x-7, 61, 44, 12))
                pygame.draw.rect(canvas, (79, 72, 113), (x-7, 103, 44, 8))
        else:
            for x in (45, 154, 265, 354):
                pygame.draw.polygon(canvas, (42, 37, 67),
                                    [(x-28,176), (x-28,82), (x,38), (x+28,82), (x+28,176)])
                pygame.draw.rect(canvas, (195, 83, 114), (x-5, 111, 10, 24))
        self.scene_cache[cache_key] = canvas
        return canvas

    def _draw_fx(self) -> None:
        """Representa el turno ya muestreado; ninguna tirada se hace al dibujar."""
        assert self.screen is not None
        if self.animation_busy:
            current = self.combat_animation.current
            if current is not None:
                beat, progress = current
                clip = self.screen.get_clip()
                self.screen.set_clip(pygame.Rect(822, 199, 410, 221))
                if beat.actor == "status":
                    pygame.draw.line(self.screen, CYAN, (1115,292), (1151,328), 4)
                    pygame.draw.line(self.screen, CYAN, (1151,292), (1115,328), 4)
                else:
                    hero = beat.actor == "hero"
                    start, end = ((980, 286), (1120, 307)) if hero else ((1092, 286), (943, 307))
                    travel = min(1., max(0., (progress-.15)/.65))
                    cx = round(start[0]+(end[0]-start[0])*travel)
                    cy = round(start[1]+(end[1]-start[1])*travel)
                    frame = min(3, int(progress*4))
                    if beat.result in ("SIN DAÑO", "ATAQUE", "FALLÓ") and frame == 3:
                        frame = 2  # No dibuja una explosión que afirme un acierto inexistente.
                    size = (192 if beat.effect == "terra_force" else 160 if beat.effect != "baby_flame" else 128)
                    if not hero and not beat.charged:
                        size = 112
                    img = self.effects.frame(beat.effect, frame, size, mirror=not hero) if beat.effect else None
                    if img is not None:
                        self.screen.blit(img, img.get_rect(center=(cx, cy)))
                    elif hero and self.combat_animation.step.action in (Action.HEAL, Action.GUARD, Action.DIGIVOLVE):
                        color = GREEN if self.combat_animation.step.action == Action.HEAL else CYAN
                        pygame.draw.rect(self.screen, color, (893, 249, 82, 108), 3, border_radius=6)
                        self._text("+" if self.combat_animation.step.action == Action.HEAL else "◇", 934, 282,
                                   font=self.title, center=True, color=color)
                    else:
                        for k in range(3):
                            pygame.draw.line(self.screen, GOLD if hero else RED,
                                (cx-12+k*8, cy-16+k*10), (cx+10+k*8,cy-31+k*10), 4)
                self.screen.set_clip(clip)
            return
        if self.fx_ticks <= 0 or self.fx_kind is None:
            return
        # Respaldo para curaciones/evoluciones y recursos no combatientes.
        if self.fx_kind == Action.HEAL:
            for k in range(5):
                pygame.draw.circle(self.screen, GREEN, (872+k*27,249-self.fx_ticks), 3)
        elif self.fx_kind == Action.DIGIVOLVE:
            for k in range(9):
                angle = k*math.tau/9+self.frames/12
                pygame.draw.circle(self.screen, GOLD,
                    (int(934+math.cos(angle)*75),int(310+math.sin(angle)*65)),4)

    def _draw_contact_shadow(self, name: str, center: tuple[int, int],
                             size: tuple[int, int]) -> None:
        """Sombra discreta ajustada a los pies del sprite, sobre el suelo local."""
        assert self.screen is not None
        sprite = self.sprites.sprite(name, size)
        width, height = sprite.get_size() if sprite is not None else size
        shadow = pygame.Surface((max(24, round(width * .68)), 12), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (9, 14, 25, 60), shadow.get_rect())
        pygame.draw.ellipse(shadow, (9, 14, 25, 55), shadow.get_rect().inflate(-12, -4))
        self.screen.blit(shadow, shadow.get_rect(center=(center[0], center[1] + height // 2 - 1)))

    def _draw_combat_feedback(self) -> None:
        if not self.animation_busy:
            return
        assert self.screen is not None
        seq = self.combat_animation
        current = seq.current
        actor = current[0].actor if current else 'result'
        color = {'hero':GOLD, 'enemy':RED, 'status':CYAN, 'result':GREEN}[actor]
        phase = {'hero':'TU ACCIÓN', 'enemy':'CONTRAATAQUE',
                 'status':'INTERRUMPIDO', 'result':'RESULTADO'}[actor]
        pygame.draw.rect(self.screen, (9,20,34), (830,206,148,26), border_radius=5)
        pygame.draw.rect(self.screen, color, (830,206,148,26), 1, border_radius=5)
        self._text(phase, 904,219, font=self.tiny, color=color, center=True)
        clip = self.screen.get_clip()
        self.screen.set_clip(pygame.Rect(822,234,410,186))
        for notice in seq.feedback.notices(seq.beats, seq.elapsed_ms):
            if notice.target == 'enemy':
                x,y = 1133,310
            elif notice.target == 'energy':
                x,y = 934,367
            else:
                x,y = 934,294 if notice.kind == 'heal' else 329
            y -= round(26*notice.progress)
            color = (CYAN if notice.kind in ('energy','cancel') else GREEN if notice.kind == 'heal'
                     else MUTED if notice.text in ('SIN DAÑO','FALLÓ') else GOLD if notice.target == 'enemy' else RED)
            font = self.small if notice.text in ('SIN DAÑO','CANCELADO','FALLÓ') else self.subtitle
            glyph = font.render(notice.text, True, color)
            badge = pygame.Surface((glyph.get_width()+18, glyph.get_height()+10), pygame.SRCALPHA)
            pygame.draw.rect(badge, (8,17,30,225), badge.get_rect(), border_radius=5)
            pygame.draw.rect(badge, (*color,210), badge.get_rect(), 1, border_radius=5)
            badge.blit(glyph,(9,5))
            badge.set_alpha(round(255*min(1.,max(0.,(1-notice.progress)/.24))))
            self.screen.blit(badge,badge.get_rect(center=(x,y)))
        pygame.draw.rect(self.screen, (9,20,34), (830,390,396,25), border_radius=5)
        label = 'Turno resuelto'
        if current:
            beat = current[0]
            label = beat.title if beat.title.upper() == beat.result else beat.title + ' · ' + beat.result
        self._text(label, 1028,402,font=self._fit_font(label,self.small,380), color=WHITE,center=True)
        self.screen.set_clip(clip)

    def _draw_arena(self, state: GameState) -> None:
        seq = self.combat_animation if self.animation_busy else None
        vitals = seq.feedback.sample(seq.beats,seq.elapsed_ms) if seq else None
        hp = vitals.hero_hp if vitals else state.hp
        energy = vitals.energy if vitals else state.energy
        enemy_hp = vitals.enemy_hp if vitals else state.enemy_hp
        rect = pygame.Rect(800, 108, 452, 471)
        self._panel(rect)
        self._text("ESCENA DE AVENTURA", 825, 128, font=self.subtitle)
        self._text(state.zone.label.upper(), 826, 165, font=self.small,
                   color=ZONE_COLORS[state.zone])
        installed = self.sprites.available(SPRITE_NAMES)
        third_party = self.sprites.external_count(SPRITE_NAMES)
        indicator = f"Sprites {len(installed)}/{len(SPRITE_NAMES)}"
        self._text(indicator, 1073, 165,
                   font=self.tiny, color=GREEN if len(installed) == len(SPRITE_NAMES) else GOLD)
        assert self.screen is not None
        scene = pygame.Rect(820, 197, 414, 225)
        self.screen.blit(self._scene_background(state.zone, scene.size), scene.topleft)
        pygame.draw.rect(self.screen, (83, 123, 146), scene, 2, border_radius=9)
        self._draw_contact_shadow(HERO_SPRITES[state.evolved], (934, 311), (164, 164))
        self._draw_hero(934, 311, state.evolved)
        if state.enemy_hp > 0:
            self._draw_contact_shadow(ENEMY_SPRITES[state.zone], (1133, 306), (158, 161))
            self._draw_enemy(1133, 306, state.zone)
            if state.enemy_charging and (seq is None or seq.elapsed_ms < seq.beats[0].duration_ms):
                pygame.draw.circle(self.screen, GOLD, (1177, 287), 21, 3)
                self._text("!", 1177, 286, font=self.title, color=GOLD, center=True)
        elif state.zone == Zone.VILLAGE:
            self._text("Elige tu primera ruta", 1123, 238,
                       font=self.tiny, color=WHITE, center=True)
        else:
            self._text("Zona despejada", 1123, 238,
                       font=self.small, color=GREEN, center=True)
        self._draw_fx()
        if state.enemy_hp > 0:
            enemy_name = ENEMIES.get(state.zone, "Enemigo").upper()
            shade = pygame.Surface((164, 45), pygame.SRCALPHA)
            shade.fill((8, 18, 31, 205))
            self.screen.blit(shade, (1058, 206))
            counter = '?' if enemy_hp is None else str(round(enemy_hp))
            enemy_label = f"{enemy_name}  {counter}/{self.controller.world.ENEMY_HP[state.zone]}"
            self._text(enemy_label, 1065, 210, font=self._fit_font(enemy_label,self.tiny,146), color=WHITE)
            if enemy_hp is None:
                pygame.draw.rect(self.screen,(45,58,75),(1065,231,146,13),border_radius=6)
                for x in range(1070,1203,12):
                    pygame.draw.line(self.screen,MUTED,(x,241),(x+6,233),1)
            else:
                self._bar(1065, 231, 146,
                          enemy_hp / self.controller.world.ENEMY_HP[state.zone], RED,
                          (state.enemy_hp / self.controller.world.ENEMY_HP[state.zone]) if seq else None)
        self._draw_combat_feedback()
        if self.cue_ticks > 0 and not self.animation_busy:
            shade = pygame.Surface((389, 27), pygame.SRCALPHA)
            shade.fill((11, 23, 40, 214))
            self.screen.blit(shade, (832, 388))
            self._text(self.last_cue[:43], 840, 393, font=self.tiny, color=GOLD)
        actor = state.form_name.upper()
        self._text(actor, 828, 436, font=self.small, color=GOLD)
        self._text(f"PS {round(hp)}/{self.controller.world.MAX_HP}", 1164, 436,
                   font=self.small, color=WHITE)
        old_hp = state.hp
        if seq and seq.elapsed_ms >= seq.beats[0].duration_ms:
            old_hp += sum(c.amount or 0 for c in seq.feedback.hero_changes if c.kind == 'heal')
        self._bar(830, 458, 384, hp / self.controller.world.MAX_HP, GREEN,
                  old_hp / self.controller.world.MAX_HP if seq else None)
        self._text(f"ENERGÍA {round(energy)}/{self.controller.world.MAX_ENERGY}",
                   829, 481, font=self.tiny, color=MUTED)
        self._bar(830, 500, 242, energy / self.controller.world.MAX_ENERGY, CYAN,
                  state.energy / self.controller.world.MAX_ENERGY if seq else None)
        self._text(("NÚCLEO: SÍ" if state.data_core else "NÚCLEO: NO"),
                   1084, 476, font=self.tiny, color=GOLD if state.data_core else MUTED)
        potion = state.potion and not (seq and seq.step.action == Action.HEAL and
                    seq.elapsed_ms >= seq.beats[0].duration_ms*IMPACT_FRACTION)
        self._text("POCIÓN: " + ("1" if potion else "0"),
                   1094, 498, font=self.small, color=GOLD)
        self._text(f"XP {state.xp}/2  |  ATAQUE +{int(state.trained)}",
                   830, 518, font=self.tiny, color=GOLD if state.trained else CYAN)
        if state.enemy_hp > 0:
            # El aviso anuncia el estado visible; no predice el resultado aleatorio.
            if seq:
                label = 'Acción resuelta · mostrando el resultado'
                hint = 'Espacio: omitir  ·  V: velocidad de animación'
                accent = CYAN
            elif state.enemy_charging:
                label = 'PREPARA: '+ENEMY_SKILLS[state.zone]
                hint = ('Defiende o intenta interrumpir el golpe potente' if state.energy > 0
                        else 'Defiende para reducir el golpe potente')
                accent = GOLD
            else:
                label = 'Intención enemiga: ataque normal'
                hint = ('Armadura 2; vulnerable al cargar · núcleo y +2 EN'
                        if state.zone == Zone.ABYSS else
                        'Armadura 1; desaparece mientras prepara su ataque'
                        if state.zone == Zone.TOWER else
                        'WarGreymon: 2 EN · resistencia mejorada ante Piedmon'
                        if state.zone == Zone.FORTRESS and state.evolved == 2 else
                        'Armadura: reduce hasta 2 PS · daño mínimo 1'
                        if state.evolved == 3 else
                        'El contraataque ocurre si el enemigo sobrevive')
                accent = MUTED
            pygame.draw.rect(self.screen, (10,23,38), (824,533,403,40), border_radius=5)
            pygame.draw.line(self.screen, accent, (825,536),(825,569),3)
            self._text(label, 834,535,font=self.tiny,color=accent)
            self._text(hint,834,553,font=self._fit_font(hint,self.tiny,382),color=MUTED)
        else:
            self._text("Recuperado: +2 PS, +1 EN y poción" if state.zone == Zone.REFUGE else
                       "Sin combate activo · Explora el Mundo Digital", 830, 539,
                       font=self.small, color=MUTED)

    def _draw_controls(self) -> None:
        rect = pygame.Rect(28, 596, 755, 195)
        self._panel(rect)
        self._text("CENTRO DE DECISIONES", 52, 613, font=self.subtitle)
        self._text("F1: DP   F2: MC   F3: Manual   R: Reiniciar   M: Menú   H: Ayuda", 52, 644,
                   font=self.tiny, color=MUTED)
        if self.controller.mode == ControlMode.MANUAL:
            actions = self.controller.legal_actions
            for index, action in enumerate(actions):
                columns = min(4, len(actions))
                width = (705 - (columns-1)*10) // columns
                x = 52 + (index % columns) * (width+10)
                y = 674 + (index // columns) * 41
                label = (f"A {self.controller.world.FORM_NAMES[int(self.controller.state.evolved)+1]}"
                         if action == Action.DIGIVOLVE else
                         technique_for(self.controller.state.evolved).name
                         if action == Action.TECHNIQUE else ACTION_LABELS[action])
                title = f"{index+1}. {label}"
                self._button(pygame.Rect(x, y, width, 35 if len(actions)>4 else 53), title,
                             "action", action, accent=GOLD, size="small", enabled=not self.presentation_busy)
            if self.controller.finished:
                self._text("Aventura terminada. Presiona R para reiniciar.", 55, 695,
                           font=self.small, color=GOLD)
            if isinstance(self.controller.state, GameState) and self.controller.state.enemy_hp > 0:
                skill = technique_for(self.controller.state.evolved)
                self._text(f"Técnica: {skill.name} | costo {skill.energy_cost} EN | daño {skill.damage} | precisión {skill.hit_probability:.0%}",
                           53, 752, font=self.small, color=GOLD)
            else:
                self._text("Modo manual: pulsa 1–7 o haz clic para decidir", 53, 752,
                           font=self.small, color=MUTED)
        else:
            suggested = self.controller.selected_action()
            self._text("PRÓXIMA DECISIÓN DEL AGENTE", 52, 673, font=self.tiny,
                       color=MUTED)
            decision = (f"Evolucionar a {self.controller.world.FORM_NAMES[int(self.controller.state.evolved)+1]}"
                        if suggested == Action.DIGIVOLVE else
                        technique_for(self.controller.state.evolved).name if suggested == Action.TECHNIQUE
                        else ACTION_LABELS[suggested] if suggested else self.controller.outcome)
            self._text(decision, 52, 698,
                       font=self._fit_font(decision, self.subtitle, 399), color=CYAN)
            self._button(pygame.Rect(473, 671, 136, 56), "▶ Siguiente", "next",
                         enabled=not self.controller.finished and not self.presentation_busy)
            self._button(pygame.Rect(620, 671, 137, 56),
                         "Ⅱ Pausar" if self.auto else "▷ Automático", "auto",
                         selected=self.auto, enabled=not self.controller.finished, size="small")
            self._text("Espacio: turno / omitir animación   A: automático   +/-: velocidad", 52, 754,
                       font=self.small, color=MUTED)
        self._button(pygame.Rect(523, 611, 116, 37), "T  Analizar", "analysis", size="small")
        self._button(pygame.Rect(648, 611, 109, 37), "↻ Reiniciar", "reset", size="small")

    def _draw_log(self) -> None:
        rect = pygame.Rect(800, 596, 452, 195)
        self._panel(rect)
        self._text("REGISTRO DE AVENTURA", 824, 613, font=self.subtitle)
        self._text(f"TURNO {self.controller.turn:02d} / {self.controller.max_steps}",
                   824, 645, font=self.small, color=MUTED)
        self._text(f"RECOMPENSA {self.controller.reward:+.0f}", 1068, 645,
                   font=self.small, color=GOLD)
        recent = self.controller.history[-4:]
        for index, message in enumerate(recent):
            # Recorte visual de mensajes largos, sin afectar el registro real.
            text = message if len(message) <= 54 else message[:51] + "..."
            self._text("• " + text, 824, 672 + index * 24, font=self.tiny,
                       color=WHITE if index == len(recent)-1 else MUTED)

    def _draw_end_overlay(self) -> None:
        if not self.controller.finished or self.presentation_busy or self.presentation.screen != Screen.GAME:
            return
        self.buttons.clear()
        self.tooltips.clear()
        self._draw_adventure_summary()

    def _dark_veil(self, opacity: int = 184) -> None:
        assert self.screen is not None
        dim = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        dim.fill((6, 13, 28, opacity))
        self.screen.blit(dim, (0, 0))

    def _draw_title(self) -> None:
        """Pantalla de inicio: selección de política y acceso a guía/créditos."""
        assert self.screen is not None
        scene = self.sprites.background("forest", (WIDTH, HEIGHT))
        self.screen.blit(scene if scene is not None else self.background, (0, 0))
        shade = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        shade.fill((7, 14, 29, 142))
        self.screen.blit(shade, (0, 0))
        pygame.draw.rect(self.screen, PANEL, (52, 70, 670, 664), border_radius=24)
        pygame.draw.rect(self.screen, (56, 100, 140), (52, 70, 670, 664), 2,
                         border_radius=24)
        self._text("DIGIMON", 82, 98, font=self.big_title, color=CYAN)
        self._text("LA CORRUPCIÓN DEL MUNDO DIGITAL", 86, 194,
                   font=self.subtitle, color=WHITE)
        self._text("Un RPG donde la inteligencia aprende a decidir.", 87, 237,
                   font=self.body, color=MUTED)
        self._text("ELIGE CÓMO JUGAR", 87, 294, font=self.subtitle, color=GOLD)
        options = [
            ("F1  /  PROGRAMACIÓN DINÁMICA", ControlMode.DYNAMIC_PROGRAMMING, CYAN),
            ("F2  /  MONTE CARLO", ControlMode.MONTE_CARLO, GREEN),
            ("F3  /  AVENTURA MANUAL", ControlMode.MANUAL, GOLD),
        ]
        for i, (name, mode, accent) in enumerate(options):
            y = 341 + i * 86
            self._button(pygame.Rect(87, y, 584, 55), name,
                         "start", mode, accent=accent,
                         selected=mode == self.controller.mode)
            self._text(MODE_DESCRIPTIONS[mode], 94, y + 59,
                       font=self.tiny, color=MUTED)
        self._button(pygame.Rect(87, 637, 156, 48), "H  /  Ayuda", "help")
        self._button(pygame.Rect(256, 637, 170, 48), "C  /  Créditos", "credits")
        self._button(pygame.Rect(444, 637, 224, 48), "Salir", "exit")
        self._button(pygame.Rect(87, 696, 280, 30), "F7 · Digidex", "digidex", size="small")
        right = pygame.Rect(758, 70, 468, 664)
        pygame.draw.rect(self.screen, (12, 25, 46), right, border_radius=24)
        pygame.draw.rect(self.screen, (54, 84, 112), right, 2, border_radius=24)
        self._text("TU MISIÓN", 784, 100, font=self.subtitle, color=GOLD)
        for i, line in enumerate((
            "Explora nueve regiones y elige tus desvíos.",
            "Anticipa habilidades enemigas anunciadas.",
            "Administra salud, energia y pociones.",
            "Digievoluciona para derrotar a Piedmon.",
        )):
            self._text("• " + line, 784, 143 + i * 32, font=self.small)
        for idx, (name, x) in enumerate(zip(
                ("agumon", "greymon", "metalgreymon", "wargreymon"),
                (828, 937, 1045, 1154))):
            self._text(name.upper(), x, 332, font=self.tiny, color=GOLD, center=True)
            img = self.sprites.sprite(name, (102, 118))
            if img is not None:
                self.screen.blit(img, img.get_rect(center=(x, 430)))
            if idx < 3:
                self._text("›", x + 53, 424, font=self.title, color=CYAN, center=True)
        pygame.draw.line(self.screen, (76, 103, 129), (780, 574), (1203, 574), 1)
        self._text("Python · POO · MDP finito · Monte Carlo", 786, 579,
                   font=self.small, color=MUTED)
        self._text("4 formas · 13 efectos de combate animados", 786, 612,
                   font=self.small, color=GREEN)
        self._text("COM50100 · v0.22 · F11 pantalla completa", 786, 646,
                   font=self.tiny, color=MUTED)
        self._button(pygame.Rect(784, 676, 132, 42), "F4 RESULTADOS", "results",
                     accent=CYAN, size="small")
        self._button(pygame.Rect(925, 676, 132, 42), "F5 DEMO", "demo",
                     accent=GOLD, size="small")

        self._button(pygame.Rect(1066, 676, 132, 42), "F6 EFECTOS", "effects",
                     accent=PURPLE, size="small")

    def _draw_modal(self) -> None:
        screen = self.presentation.screen
        if screen not in (Screen.HELP, Screen.CREDITS, Screen.PAUSE):
            return
        assert self.screen is not None
        self._dark_veil(210)
        rect = pygame.Rect(256, 160, 768, 505)
        pygame.draw.rect(self.screen, PANEL, rect, border_radius=22)
        pygame.draw.rect(self.screen, CYAN, rect, 2, border_radius=22)
        self._button(pygame.Rect(941, 173, 55, 41), "X", "back", accent=RED)
        if screen == Screen.PAUSE:
            heading = "AVENTURA EN PAUSA"
            rows = [
                "La simulación está detenida.",
                "Vuelve al juego cuando estés listo.",
                "P / Enter / Esc: continuar",
                "M: volver al menú principal (desde el juego)",
            ]
        elif screen == Screen.HELP:
            heading = "GUÍA Y CONTROLES"
            rows = [
                "F1 / F2 / F3: elegir Programación Dinámica, Monte Carlo o Manual.",
                "Espacio / Enter: siguiente turno, cerrar aviso u omitir animación.",
                "A: iniciar o pausar el automático.    R: reiniciar aventura.",
                "1–7 o clic: acciones legales. El mapa ilumina los destinos disponibles.",
                "V: animación normal, rápida o sin animación.  + / -: ritmo automático.",
                "P: pausar.    H: ayuda.    C: créditos.    M / Esc: menú. F11: pantalla completa.",
                "T: laboratorio de decisiones (DP, MC, valores Q y cobertura).",
                "F4: resultados. F5: presentación. F6: habilidades. F7: Digidex. Tab: diario.",
                "Espacio: omitir ataque o viaje.  F8: silencio. F9 / F10: volumen.",
            ]
        else:
            heading = "CRÉDITOS Y USO ACADÉMICO"
            rows = [
                "Digimon RPG: La corrupción del Mundo Digital — v0.22",
                "Aprendizaje reforzado COM50100 · Proyecto académico individual.",
                "Algoritmos desde cero: Programación Dinámica y Monte Carlo.",
                "Sprites: Zebub Al-Zemechiel, DragonRod342, SergioGranSol,",
                "Opdisk, Topaz66, Arcanin1412, Neroesaurus, Demo9ic, Matykiller,",
                "Maxtyrannus, ScorchedDragonStudio, Sharkmon, CadejoWhite,",
                "VictoryD, Extyrannomon, Thousand_13 y Yggdrasil Library.",
                "Fuente: github.com/SergioGranSol/digidex · Enlaces: CREDITOS.md",
                "Fondos y efectos: recursos preparados para este proyecto.",
                "Digimon: Akiyoshi Hongo, Toei Animation y Bandai.",
            ]
        self._text(heading, 298, 201, font=self.title, color=CYAN)
        for i, line in enumerate(rows):
            self._text(line, 298, 262 + i * (28 if screen == Screen.CREDITS else 35), font=self.small,
                       color=WHITE if i < len(rows) - 1 else GOLD)
        self._button(pygame.Rect(510, 585, 259, 52), "Volver  /  Enter", "back")

    def _draw_story_notice(self) -> None:
        if (self.notice_ticks <= 0 or not self.presentation.notice or self.transition_busy or
                self.controller.finished and not self.presentation_busy):
            return
        assert self.screen is not None
        beat = self.presentation.notice
        colors = {"cyan": CYAN, "gold": GOLD, "green": GREEN,
                  "purple": PURPLE, "red": RED}
        color = colors.get(beat.accent, CYAN)
        rect = pygame.Rect(813, 668, 426, 112)
        # La narración ocupa temporalmente el registro: deja visibles el mapa
        # completo y los botones de decisión, incluida la ruta inferior.
        pygame.draw.rect(self.screen, (10, 25, 43), rect, border_radius=13)
        pygame.draw.rect(self.screen, color, rect, 2, border_radius=13)
        self._text(beat.title, 830, 679,
                   font=self._fit_font(beat.title,self.small,354), color=color)
        lines = []
        line = ''
        for word in beat.description.split():
            candidate = (line+' '+word).strip()
            if line and self.small.size(candidate)[0] > 390:
                lines.append(line); line = word
            else:
                line = candidate
        if line:
            lines.append(line)
        for i,line in enumerate(lines):
            self._text(line,830,707+i*20,font=self.small)
        self._button(pygame.Rect(1202,675,29,25), "X", "dismiss_notice", size="small")

    def _draw_analysis(self) -> None:
        """Pantalla solo lectura: valores tabulares calculados, nunca inventados."""
        assert self.screen is not None
        self._dark_veil(239)
        panel = pygame.Rect(72, 60, 1136, 702)
        pygame.draw.rect(self.screen, PANEL, panel, border_radius=20)
        pygame.draw.rect(self.screen, CYAN, panel, 2, border_radius=20)
        self._text("LABORATORIO DE POLÍTICAS", 104, 83, font=self.title, color=CYAN)
        self._text("Bellman / Q*(s,a)   frente a   First-Visit / Q_MC(s,a)",
                   106, 126, font=self.small, color=MUTED)
        state = self.inspection_history[self.inspection_index]
        self._text(f"Estado {self.inspection_index+1} de {len(self.inspection_history)}  ·  "
                   f"{state.zone.label}  ·  {state.form_name}",
                   106, 167, font=self.subtitle, color=GOLD)
        self._text(f"PS {state.hp}   EN {state.energy}   Enemigo {state.enemy_hp}   "
                   f"Evolución {state.evolved}   XP {state.xp}   "
                   f"Cargado {int(state.enemy_charging)}   Núcleo {int(state.data_core)}   "
                   f"Mejora {int(state.trained)}", 106, 202, font=self.small)
        self._text(f"Poción: {'sí' if state.potion else 'no'}", 106, 229, font=self.small,
                   color=MUTED)
        if self.inspector is None:
            self._text("No hay archivo de valores Q compatible con estas políticas.",
                       113, 306, font=self.subtitle, color=GOLD)
            self._text("Las políticas siguen disponibles para jugar; el análisis no inventa Q.",
                       113, 349, font=self.body)
        else:
            data = self.inspector.inspect(state)
            coverage = 100 * self.inspector.coverage
            self._text(f"Cobertura MC: {coverage:.1f}% de estados con política · "
                       f"{self.inspector.visited_pairs:,} pares visitados · "
                       f"{self.inspector.episodes or 0:,} episodios",
                       106, 257, font=self.small, color=GREEN)
            self._text("ACCIÓN LEGAL", 111, 300, font=self.small, color=CYAN)
            self._text("DP: Q*(s,a)", 652, 300, font=self.small, color=CYAN)
            self._text("MC: Q(s,a)", 842, 300, font=self.small, color=CYAN)
            self._text("VISITAS", 1074, 300, font=self.small, color=CYAN)
            pygame.draw.line(self.screen, (75, 101, 129), (106, 327), (1170, 327), 1)
            for i, row in enumerate(data.actions):
                y = 336 + i*34
                if y > 660:
                    break
                if i % 2 == 0:
                    pygame.draw.rect(self.screen, (31, 48, 70), (107, y-2, 1060, 33), border_radius=5)
                name = ("DP / MC  " if row.dp_recommended and row.mc_recommended else
                        "DP  " if row.dp_recommended else "MC  " if row.mc_recommended else "") + row.label
                self._text(name, 116, y+4, font=self.small,
                           color=GREEN if row.dp_recommended and row.mc_recommended else
                           GOLD if row.dp_recommended or row.mc_recommended else WHITE)
                self._text(f"{row.dp_q:.2f}" if row.dp_q is not None else "Sin dato",
                           662, y+4, font=self.small)
                self._text(f"{row.mc_q:.2f}" if row.mc_q is not None else "No visitado",
                           852, y+4, font=self.small,
                           color=WHITE if row.mc_q is not None else MUTED)
                self._text(str(row.mc_visits), 1085, y+4, font=self.small, color=MUTED)
            flag = ("Coinciden" if data.agrees else "Decisiones distintas" if data.agrees is False
                    else "MC no aprendió una política para este estado")
            self._text(flag, 114, 680, font=self.small,
                       color=GREEN if data.agrees else GOLD)
        self._button(pygame.Rect(790, 698, 120, 42), "← Anterior",
                     "analysis_shift", -1, enabled=self.inspection_index > 0, size="small")
        self._button(pygame.Rect(918, 698, 120, 42), "Siguiente →",
                     "analysis_shift", 1,
                     enabled=self.inspection_index < len(self.inspection_history)-1, size="small")
        self._button(pygame.Rect(1044, 698, 125, 42), "T / Volver", "back", size="small")

    def _academic_chart(self, key: str, area: pygame.Rect, *, compact: bool = False) -> None:
        """Gráfico Pygame con el CSV v0.11. NUNCA modifica Q, V o las políticas."""
        if self.dashboard is None or self.screen is None:
            return
        spec = self.dashboard.metric(key)
        mc, dp, sd = self.dashboard.values(key)
        xs = episode_positions(tuple(row.episodes for row in self.dashboard.rows),
                               area.left+58, area.width-100)
        graph_top = area.top + 28
        graph_bottom = area.bottom - 57
        plot_h = graph_bottom - graph_top

        def py(value: float) -> int:
            frac = min(1.0, max(0.0, (value - spec.y_min)/(spec.y_max - spec.y_min)))
            return round(graph_bottom - frac * plot_h)

        pygame.draw.rect(self.screen, (15, 29, 48), area, border_radius=12)
        for step in range(5):
            level = spec.y_min + (spec.y_max-spec.y_min) * step / 4
            y = py(level)
            pygame.draw.line(self.screen, (48, 66, 86), (area.left+48, y), (area.right-24, y))
            label = f"{level:.0%}" if spec.unit == "%" else f"{level:.0f}"
            self._text(label, area.left+5, y-10, font=self.tiny, color=MUTED)
        for i, x in enumerate(xs):
            episode = self.dashboard.rows[i].episodes
            label = f"{episode/1000:g}k" if episode >= 1000 else str(episode)
            self._text(label, int(x), graph_bottom+17, font=self.tiny, center=True, color=MUTED)
        if dp is not None:
            for i in range(len(dp)-1):
                pygame.draw.line(self.screen, GOLD, (round(xs[i]), py(dp[i])),
                                 (round(xs[i+1]), py(dp[i+1])), 2)
            for i, value in enumerate(dp):
                pygame.draw.circle(self.screen, GOLD, (round(xs[i]), py(value)), 4)
        if sd is not None:
            for i, value in enumerate(mc):
                x = round(xs[i]); a = py(value+sd[i]); b = py(value-sd[i])
                pygame.draw.line(self.screen, (68, 139, 147), (x,a), (x,b), 3)
                pygame.draw.line(self.screen, (68,139,147), (x-5,a), (x+5,a), 2)
                pygame.draw.line(self.screen, (68,139,147), (x-5,b), (x+5,b), 2)
        for i in range(len(mc)-1):
            pygame.draw.line(self.screen, CYAN, (round(xs[i]), py(mc[i])),
                             (round(xs[i+1]), py(mc[i+1])), 3)
        for i, value in enumerate(mc):
            pygame.draw.circle(self.screen, CYAN, (round(xs[i]), py(value)), 5)
        self._text("Episodios de entrenamiento", area.centerx, area.bottom-15,
                   font=self.tiny, color=MUTED, center=True)

    def _academic_shell(self, heading: str, subtitle: str) -> None:
        assert self.screen is not None
        self.screen.blit(self.background, (0, 0))
        self._panel(pygame.Rect(39, 26, 1202, 766))
        self._text(heading, 73, 52, font=self.title, color=CYAN)
        self._text(subtitle, 74, 95, font=self.small, color=MUTED)
        self._button(pygame.Rect(1106, 47, 93, 42), "VOLVER", "back", size="small")

    def _draw_results(self) -> None:
        version = self.dashboard.experiment_version if self.dashboard else "0.22"
        self._academic_shell(f"RESULTADOS ACADÉMICOS · v{version}",
                             "Cinco entrenamientos MC independientes · Comparación sobre el mismo MDP")
        if self.dashboard is None:
            self._text("No se encontraron resultados compatibles. El videojuego sigue disponible.",
                       100, 250, font=self.subtitle, color=GOLD)
            return
        spec = METRICS[self.results_metric_index]
        for i, m in enumerate(METRICS):
            self._button(pygame.Rect(77 + 280*i, 135, 270, 49), m.title,
                         "metric_select", i, selected=i == self.results_metric_index,
                         size="small", accent=CYAN)
        self._text(spec.explanation, 85, 201, font=self.small, color=WHITE)
        self._academic_chart(spec.key, pygame.Rect(82, 242, 781, 427))
        self._panel(pygame.Rect(889, 240, 320, 428))
        first, last = self.dashboard.rows[0], self.dashboard.rows[-1]
        mc, dp, sd = self.dashboard.values(spec.key)
        fmt = (lambda x: f"{x:.1%}") if spec.unit == "%" else (lambda x: f"{x:.2f}")
        self._text("LECTURA DEL EXPERIMENTO", 909, 262, font=self.small, color=GOLD)
        self._text(f"Inicio ({first.episodes:,} ep.)", 909, 303, font=self.small, color=MUTED)
        self._text(fmt(mc[0]), 909, 329, font=self.title, color=CYAN)
        self._text(f"Final ({last.episodes:,} ep.)", 909, 384, font=self.small, color=MUTED)
        self._text(fmt(mc[-1]), 909, 411, font=self.title, color=CYAN)
        if dp is not None:
            self._text("Referencia DP", 909, 474, font=self.small, color=MUTED)
            self._text(fmt(dp[-1]), 909, 496, font=self.title, color=GOLD)
        else:
            self._text("Sin referencia DP", 909, 486, font=self.small, color=MUTED)
        self._text(f"Semillas: {len(self.dashboard.train_seeds)}", 909, 558,
                   font=self.small, color=WHITE)
        self._text(f"Evaluaciones: {self.dashboard.eval_episodes} / semilla", 909, 586,
                   font=self.small, color=WHITE)
        self._text("MC (cian) · DP (dorado) · ±1 DE entre semillas", 112, 692, font=self.small, color=CYAN)
        self._text("Promedios observados, no prueba matemática de convergencia.",
                   112, 722, font=self.small, color=MUTED)
        self._button(pygame.Rect(971, 694, 212, 48), "F5  PRESENTACIÓN", "demo",
                     size="small", accent=GOLD)

    def _draw_demo(self) -> None:
        self._academic_shell("PRESENTACIÓN GUIADA · 10 MINUTOS",
                             "Usa ← → o Espacio para avanzar. F1/F2 inicia una aventura real.")
        if self.dashboard is None:
            self._text("No están disponibles los datos del experimento.",
                       100, 275, font=self.subtitle, color=GOLD)
            return
        slides = self.dashboard.slides()
        slide = slides[self.demo_index]
        self._text(slide.title, 84, 163, font=self.subtitle, color=GOLD)
        if slide.metric:
            for i, line in enumerate(slide.lines):
                self._text("•  " + line, 87, 213 + i*42, font=self.small)
            self._academic_chart(slide.metric, pygame.Rect(170, 402, 940, 252), compact=True)
        else:
            for i, line in enumerate(slide.lines):
                self._text("•  " + line, 87, 230 + i*65, font=self.body)
            if self.demo_index == len(slides)-1:
                self._button(pygame.Rect(183, 511, 401, 68), "F1  JUGAR CON VALUE ITERATION",
                             "start", ControlMode.DYNAMIC_PROGRAMMING, accent=CYAN)
                self._button(pygame.Rect(621, 511, 401, 68), "F2  JUGAR CON MONTE CARLO",
                             "start", ControlMode.MONTE_CARLO, accent=GREEN)
        self._text(slide.footnote, 90, 671, font=self.small, color=MUTED)
        self._button(pygame.Rect(805, 710, 151, 49), "← Anterior", "demo_shift", -1,
                     enabled=self.demo_index > 0, size="small")
        self._button(pygame.Rect(977, 710, 151, 49), "Siguiente →", "demo_shift", 1,
                     enabled=self.demo_index < len(slides)-1, size="small")
        self._text(f"{self.demo_index+1} / {len(slides)}", 108, 725,
                   font=self.small, color=GOLD)

    def _draw_effect_gallery(self) -> None:
        self._academic_shell("GALERÍA DE HABILIDADES · 8 BITS",
                             "← →: cambiar habilidad · Espacio: repetir · F6 / Esc: volver")
        owners = ("Agumon", "Greymon", "MetalGreymon", "WarGreymon",
                  "Betamon", "Goblimon", "Ogremon", "Devimon", "Andromon", "Piedmon",
                  "General", "General", "General")
        for i, name in enumerate(ALL_EFFECTS):
            x, y = 80 + (i%2)*252, 167 + (i//2)*52
            self._button(pygame.Rect(x,y,240,43), owners[i]+" · "+EFFECT_LABELS[name],
                         "effect_select", i, selected=i == self.effect_index, size="small", accent=PURPLE)
        name = ALL_EFFECTS[self.effect_index]
        hero_attack = self.effect_index < 4 or self.effect_index >= 10
        zone = Zone.FORTRESS if hero_attack else next(z for z,n in ENEMY_EFFECTS.items() if n == name)
        form = self.effect_index if self.effect_index < 4 else 3
        scene = pygame.Rect(626, 199, 573, 306)
        assert self.screen is not None
        self.screen.blit(self._scene_background(zone, scene.size), scene.topleft)
        pygame.draw.rect(self.screen, (83,123,146), scene, 2, border_radius=9)
        left = self.sprites.sprite(HERO_SPRITES[form], (146,146))
        right = self.sprites.sprite(ENEMY_SPRITES[zone], (146,146), mirror=True)
        self._draw_contact_shadow(HERO_SPRITES[form], (724,366), (146,146))
        self._draw_contact_shadow(ENEMY_SPRITES[zone], (1100,366), (146,146))
        if left is not None: self.screen.blit(left,left.get_rect(center=(724,366)))
        if right is not None: self.screen.blit(right,right.get_rect(center=(1100,366)))
        time = self.effect_elapsed % 1600
        progress = min(1.,time/1200)
        if time < 1200:
            frame = min(3,int(progress*4))
            x = round(794+306*progress) if hero_attack else round(1030-306*progress)
            img = self.effects.frame(name,frame,192,mirror=not hero_attack)
            if img is not None:
                clip=self.screen.get_clip();self.screen.set_clip(scene.inflate(-4,-4))
                self.screen.blit(img,img.get_rect(center=(x,350)))
                self.screen.set_clip(clip)
        self._text(owners[self.effect_index]+" / "+EFFECT_LABELS[name], 647, 218,
                   font=self.small,color=GOLD)
        self._text("CUATRO FOTOGRAMAS · CARGA, LANZAMIENTO E IMPACTO", 638,535,font=self.tiny,color=MUTED)
        for i in range(4):
            tile=self.effects.frame(name,i,128)
            if tile is not None:self.screen.blit(tile,(645+i*138,563))
        self._text("Vista gráfica: no consume turnos ni entrena al agente.", 83, 550,
                   font=self.small, color=MUTED)
        self._text("PNG transparentes · cuadrícula lógica de 64 × 64",83,582,font=self.small,color=MUTED)
        self._text("Ataques propios y contraataques diferenciados.",83,614,font=self.small,color=MUTED)
        self._text("Las reglas de combate siguen siendo las del MDP.",83,646,font=self.small,color=MUTED)
        self._button(pygame.Rect(83,688,230,49),"↻ Repetir animación","effect_replay",size="small")
        self._button(pygame.Rect(83,746,230,34),"Escuchar efecto","effect_listen",size="small",
                     enabled=self.audio.available and self.audio.effective_volume>0)
        self._text(f"{self.effect_index+1} / {len(ALL_EFFECTS)}", 344,706,font=self.small,color=PURPLE)

    def _draw_audio_controls(self) -> None:
        label = ('F8 Sonido: OFF' if self.audio.settings.muted else 'F8 Sonido: ON')
        if not self.audio.available:
            label = 'Audio no disponible'
        self._button(pygame.Rect(345,792,180,25),label,'audio_mute',size='small',accent=CYAN)
        self._button(pygame.Rect(533,792,70,25),'F9 −','audio_down',size='small')
        self._text(f'{self.audio.settings.volume:.0%}',636,804,font=self.tiny,color=CYAN,center=True)
        self._button(pygame.Rect(670,792,70,25),'F10 +','audio_up',size='small')
        self._button(pygame.Rect(748,792,112,25),'Probar sonido','audio_test',size='small',
                     enabled=self.audio.available and self.audio.effective_volume>0)
        tooltip = self.audio.status
        if self.audio.saved is True:
            tooltip += ' · Preferencia guardada'
        elif self.audio.saved is False:
            tooltip += ' · Preferencia solo para esta sesión'
        self.tooltips.append((pygame.Rect(345,792,180,25),tooltip))

    def _draw_region_transition(self) -> None:
        if not self.transition_busy:
            return
        seq = self.region_transition
        rect = pygame.Rect(820,197,414,225)
        veil = pygame.Surface(rect.size,pygame.SRCALPHA)
        veil.fill((6,17,30,seq.opacity))
        self.screen.blit(veil,rect.topleft)
        if .18 < seq.progress < .85:
            title = seq.step.next_state.zone.label.upper()
            self._text('VIAJANDO A',1027,270,font=self.tiny,color=CYAN,center=True)
            self._text(title,1027,302,font=self._fit_font(title,self.subtitle,386),color=WHITE,center=True)
            for i in range(8):
                color = CYAN if i < round(seq.progress*8) else (47,78,93)
                pygame.draw.rect(self.screen,color,(969+i*15,331,9,5))
            loss = seq.step.state.hp-seq.step.next_state.hp
            if loss > 0:
                self._text(f'Emboscada al llegar · −{loss} PS',1027,364,font=self.small,color=GOLD,center=True)

    def draw(self) -> None:
        if self.screen is None:
            raise RuntimeError("Pygame todavía no ha inicializado la ventana")
        self.buttons.clear()
        self.tooltips.clear()
        self.screen.blit(self.background, (0, 0))
        if self.presentation.screen == Screen.TITLE:
            self._draw_title()
            self._draw_audio_controls()
            return
        if (self.presentation.screen in (Screen.HELP, Screen.CREDITS)
                and self.presentation.return_screen == Screen.TITLE):
            self._draw_title()
            self.buttons.clear()
            self.tooltips.clear()
            self._draw_modal()
            self._draw_audio_controls()
            return
        if self.presentation.screen in (Screen.DIGIDEX,Screen.SUMMARY):
            if self.presentation.screen==Screen.DIGIDEX:self._draw_digidex()
            else:self._draw_adventure_summary()
            self._draw_audio_controls()
            return
        self._draw_header()
        if isinstance(self.controller.state, GameState):
            state = self.controller.state
        elif self.controller.last_report is not None:
            state = self.controller.last_report.step.state
        else:
            state = self.controller.world.start_state()
        self._draw_map(state)
        scene_state = (self.combat_animation.display_state if self.animation_busy else
                       self.region_transition.display_state if self.transition_busy else state)
        self._draw_arena(scene_state)
        self._draw_region_transition()
        self._draw_controls()
        self._draw_log()
        self._text("COM50100 · v0.22", 32, 798, font=self.tiny, color=MUTED)
        self._text("F11: pantalla completa · ventana ajustable", 915, 798, font=self.tiny, color=MUTED)
        self._draw_end_overlay()
        if self.presentation.screen == Screen.GAME:
            self._draw_story_notice()
        elif self.presentation.screen == Screen.ANALYSIS:
            self.buttons.clear()
            self.tooltips.clear()
            self._draw_analysis()
        elif self.presentation.screen == Screen.RESULTS:
            self.buttons.clear()
            self.tooltips.clear()
            self._draw_results()
        elif self.presentation.screen == Screen.EFFECTS:
            self.buttons.clear()
            self.tooltips.clear()
            self._draw_effect_gallery()
        elif self.presentation.screen == Screen.DEMO:
            self.buttons.clear()
            self.tooltips.clear()
            self._draw_demo()
        else:
            self.buttons.clear()
            self.tooltips.clear()
            self._draw_modal()
        self._draw_audio_controls()
