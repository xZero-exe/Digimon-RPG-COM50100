"""Reproductor de WAV locales con canales propios y degradación silenciosa."""
from __future__ import annotations
from dataclasses import replace
from pathlib import Path
import pygame
from ..audio_settings import AudioSettings, default_audio_path


class AudioManager:
    GROUPS = {'ui':0,'cast':1,'impact':2,'event':3,'preview':4}

    def __init__(self,root: Path,settings_path: Path | None=None):
        self.root = Path(root)
        self.settings_path = Path(settings_path) if settings_path is not None else default_audio_path()
        self.settings = AudioSettings.load(self.settings_path)
        self.available = False
        self.status = 'Audio sin inicializar'
        self.saved = None
        self.paused = False
        self.channels = {}
        self.gains = dict.fromkeys(self.GROUPS,1.)
        self.sounds = {}
        self.observer = None  # Diagnóstico opcional; el juego no guarda un registro ilimitado.

    def initialize(self) -> None:
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=22050,size=-16,channels=1,buffer=512)
            pygame.mixer.set_num_channels(max(8,pygame.mixer.get_num_channels()))
            self.channels = {name:pygame.mixer.Channel(index) for name,index in self.GROUPS.items()}
            self.available = True
            self.status = 'Efectos originales de estilo retro'
            self._apply_volume()
        except (pygame.error,OSError):
            self._disable()

    def _disable(self) -> None:
        self.available = False
        self.channels.clear()
        self.status = 'Audio no disponible; el juego continúa sin sonido'

    @property
    def effective_volume(self) -> float:
        return 0. if self.settings.muted else self.settings.volume

    def _apply_volume(self) -> None:
        try:
            for group,channel in self.channels.items():
                channel.set_volume(self.effective_volume*self.gains[group])
        except pygame.error:
            self._disable()

    def _save(self) -> None:
        self.saved = self.settings.save(self.settings_path)
        self._apply_volume()

    def toggle_mute(self) -> None:
        self.settings = replace(self.settings,muted=not self.settings.muted)
        if self.settings.muted:
            self.stop_gameplay(); self.stop_preview()
            if self.available:
                self.channels['ui'].stop()
        self._save()

    def change_volume(self,delta: float) -> None:
        self.settings = replace(self.settings,volume=round(min(1.,max(0.,self.settings.volume+delta)),2))
        self._save()

    def sound(self,name: str):
        if not self.available:
            return None
        if name not in self.sounds:
            try:
                self.sounds[name] = pygame.mixer.Sound(str(self.root/f'{name}.wav'))
            except (pygame.error,OSError):
                self.sounds[name] = None
        return self.sounds[name]

    def play(self,name: str,group: str='cast',gain: float=1.) -> bool:
        if (not self.available or self.effective_volume<=0 or group not in self.channels
                or self.paused and group in ('cast','impact','event')):
            return False
        sound = self.sound(name)
        if sound is None:
            return False
        self.gains[group] = min(1.,max(0.,gain))
        try:
            self.channels[group].set_volume(self.effective_volume*self.gains[group])
            self.channels[group].play(sound)
        except pygame.error:
            self._disable()
            return False
        if self.observer is not None:
            self.observer(name,group,gain)
        return True

    def set_paused(self,paused: bool) -> None:
        if self.paused == paused:
            return
        self.paused = paused
        try:
            for group in ('cast','impact','event'):
                channel = self.channels.get(group)
                if channel is not None:
                    channel.pause() if paused else channel.unpause()
        except pygame.error:
            self._disable()

    def stop_gameplay(self) -> None:
        try:
            for group in ('cast','impact','event'):
                if group in self.channels:
                    self.channels[group].stop()
        except pygame.error:
            self._disable()

    def stop_preview(self) -> None:
        try:
            if 'preview' in self.channels:
                self.channels['preview'].stop()
        except pygame.error:
            self._disable()
