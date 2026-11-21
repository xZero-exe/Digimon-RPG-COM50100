"""Gestión de imágenes Pygame: sprites originales incluidos + recursos externos opcionales.

Prioridad: assets/digimon (autorizados, locales) -> assets/demo/digimon (arte propio).
No se descarga material ajeno. El motor MDP permanece independiente de Pygame.
"""
from __future__ import annotations

from pathlib import Path
import math
import warnings

import pygame

from ..assets_catalog import resolve_asset


class SpriteManager:
    """Cachea PNG locales y superficies escaladas; fallback es responsabilidad de la vista."""

    def __init__(self, root: Path):
        self.root = Path(root)
        self._originals: dict[Path, pygame.Surface | None] = {}
        self._scaled: dict[tuple[Path, tuple[int, int], bool], pygame.Surface | None] = {}
        self._backgrounds: dict[tuple[Path, tuple[int, int]], pygame.Surface | None] = {}

    def _resolve(self, category: str, name: str) -> Path:
        return resolve_asset(self.root, category, name)

    def _load(self, path: Path) -> pygame.Surface | None:
        if path not in self._originals:
            if not path.is_file():
                self._originals[path] = None
            else:
                try:
                    img = pygame.image.load(str(path)).convert_alpha()
                    # Elimina márgenes transparentes sin deformar el pixel art.
                    crop = img.get_bounding_rect(min_alpha=1)
                    self._originals[path] = img.subsurface(crop).copy() if crop.width and crop.height else None
                except (OSError, pygame.error) as exc:
                    warnings.warn(f"No se pudo cargar {path}: {exc}", stacklevel=2)
                    self._originals[path] = None
        return self._originals[path]

    def _image(self, path: Path, size: tuple[int, int], mirror: bool) -> pygame.Surface | None:
        key = (path, size, mirror)
        if key not in self._scaled:
            original = self._load(path)
            if original is None:
                self._scaled[key] = None
            else:
                width, height = original.get_size()
                factor = min(size[0] / width, size[1] / height)
                scaled = pygame.transform.scale(original, (max(1, round(width * factor)),
                                                           max(1, round(height * factor))))
                if mirror:
                    scaled = pygame.transform.flip(scaled, True, False)
                self._scaled[key] = scaled
        return self._scaled[key]

    def sprite(self, name: str, max_size: tuple[int, int], mirror: bool = False) -> pygame.Surface | None:
        return self._image(self._resolve("digimon", name), max_size, mirror)

    def background(self, name: str, size: tuple[int, int]) -> pygame.Surface | None:
        """Rellena por recorte central, sin estirar ni suavizar el pixel art."""
        return self._cover_image(self._resolve("backgrounds", name), size)

    def world_map(self, size: tuple[int, int]) -> pygame.Surface | None:
        return self._cover_image(self.root / "maps" / "world_map.png", size)

    def _cover_image(self, path: Path, size: tuple[int, int]) -> pygame.Surface | None:
        key = (path, size)
        if key not in self._backgrounds:
            img = self._load(path)
            if img is None:
                self._backgrounds[key] = None
            else:
                width, height = img.get_size()
                factor = max(size[0] / width, size[1] / height)
                scaled = pygame.transform.scale(img, (math.ceil(width * factor),
                                                       math.ceil(height * factor)))
                crop = pygame.Rect(0, 0, *size)
                crop.center = scaled.get_rect().center
                self._backgrounds[key] = scaled.subsurface(crop).copy()
        return self._backgrounds[key]

    def available(self, names: tuple[str, ...]) -> tuple[str, ...]:
        return tuple(name for name in names if self._resolve("digimon", name).is_file())

    def external_count(self, names: tuple[str, ...]) -> int:
        """Cuenta los sprites que fueron instalados externamente."""
        return sum((self.root / "digimon" / f"{name}.png").is_file() for name in names)
