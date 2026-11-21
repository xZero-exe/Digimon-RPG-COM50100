"""Carga atlas PNG de efectos. No recorta cada frame: conserva su punto de anclaje."""
from pathlib import Path
import warnings
import pygame


class EffectSprites:
    def __init__(self, assets: Path):
        self.root = Path(assets) / 'effects'
        self._frames = {}

    def frames(self, name: str, size: int = 144, mirror: bool = False):
        key = (name, size, mirror)
        if key not in self._frames:
            path = self.root / (name+'.png')
            if not path.is_file():
                self._frames[key] = ()
            else:
                try:
                    sheet = pygame.image.load(str(path)).convert_alpha()
                    w, h = sheet.get_size()
                    if w != h or w % 2:
                        raise ValueError('El atlas debe ser cuadrado y divisible en 2 × 2')
                    tiles = []
                    for index in range(4):
                        tile = sheet.subsurface((index%2*w//2, index//2*h//2, w//2, h//2))
                        # Cuadrícula lógica 64 × 64, ampliación nearest-neighbor.
                        pixel = pygame.transform.scale(tile, (64, 64))
                        tile = pygame.transform.scale(pixel, (size, size))
                        if mirror:
                            tile = pygame.transform.flip(tile, True, False)
                        tiles.append(tile)
                    self._frames[key] = tuple(tiles)
                except (OSError, ValueError, pygame.error) as exc:
                    warnings.warn(f'No se pudo cargar efecto {path}: {exc}', stacklevel=2)
                    self._frames[key] = ()
        return self._frames[key]

    def frame(self, name: str, index: int, size: int = 144, mirror: bool = False):
        frames = self.frames(name, size, mirror)
        return frames[max(0, min(3, index))] if frames else None
