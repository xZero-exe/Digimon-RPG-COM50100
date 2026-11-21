"""Geometría de presentación; no conoce estados ni políticas del MDP."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Viewport:
    """Escala uniforme y bandas para conservar la composición y los clics."""
    width: int
    height: int
    logical_width: int = 1280
    logical_height: int = 820

    @property
    def size(self) -> tuple[int, int]:
        scale = min(self.width / self.logical_width, self.height / self.logical_height)
        return max(1, round(self.logical_width * scale)), max(1, round(self.logical_height * scale))

    @property
    def origin(self) -> tuple[int, int]:
        w, h = self.size
        return (self.width - w) // 2, (self.height - h) // 2

    def to_logical(self, point: tuple[int, int]) -> tuple[int, int] | None:
        x, y = point
        ox, oy = self.origin
        w, h = self.size
        if not (ox <= x < ox + w and oy <= y < oy + h):
            return None
        return (int((x-ox) * self.logical_width / w),
                int((y-oy) * self.logical_height / h))


def episode_positions(episodes: tuple[int, ...], left: float, width: float) -> tuple[float, ...]:
    """Eje lineal de episodios; 2.000 y 20.000 no son categorías equidistantes."""
    if not episodes or any(n <= 0 for n in episodes):
        raise ValueError("Se requieren episodios positivos")
    if tuple(sorted(set(episodes))) != episodes:
        raise ValueError("Los episodios deben ser únicos y crecientes")
    last = episodes[-1]
    return tuple(left + width * n / last for n in episodes)
