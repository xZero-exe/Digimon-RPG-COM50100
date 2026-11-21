"""Manifiesto de recursos visuales opcionales; no depende de Pygame.

Las rutas de Digidex se han comprobado en la rama ``main``. El código no
concede ni presupone derechos de uso sobre el arte de terceros.
"""
from __future__ import annotations

from pathlib import Path

from .domain import Zone

SOURCE_REPOSITORY = "https://github.com/SergioGranSol/digidex"
SOURCE_PREFIX = Path("resources/img/sprites/x5")

HERO_SPRITES = {0: "agumon", 1: "greymon", 2: "metalgreymon", 3: "wargreymon"}
ENEMY_SPRITES = {
    Zone.ABYSS: "guardromon",
    Zone.FOREST: "betamon",
    Zone.CAVE: "goblimon",
    Zone.SWAMP: "ogremon",
    Zone.RUINS: "devimon",
    Zone.TOWER: "andromon",
    Zone.FORTRESS: "piedmon",
}
SPRITE_NAMES = ("agumon", "greymon", "metalgreymon", "wargreymon", "betamon", "goblimon", "ogremon", "devimon", "andromon", "piedmon", "guardromon")
DIGIDEX_NAMES = SPRITE_NAMES

BACKGROUND_NAMES = {
    Zone.REFUGE: "refuge",
    Zone.ABYSS: "abyss",
    Zone.VILLAGE: "village",
    Zone.FOREST: "forest",
    Zone.CAVE: "cave",
    Zone.SWAMP: "swamp",
    Zone.RUINS: "ruins",
    Zone.TOWER: "tower",
    Zone.FORTRESS: "fortress",
}


def find_asset_root(override: Path | None = None) -> Path:
    """Busca assets locales; ``--assets`` permite carpetas arbitrarias."""
    if override is not None:
        return Path(override).expanduser().resolve()
    candidates = (
        Path.cwd() / "assets",
        Path(__file__).resolve().parents[2] / "assets",  # editable install: raíz/src/digimon_rl
    )
    for candidate in candidates:
        if candidate.is_dir():
            return candidate.resolve()
    return candidates[0].resolve()


def resolve_asset(root: Path, category: str, name: str) -> Path:
    """Usa PNG local autorizado si existe; en otro caso recurso original del paquete.

    Esta función no requiere Pygame ni descarga archivos.
    """
    root = Path(root)
    custom = root / category / f"{name}.png"
    return custom if custom.is_file() else root / "demo" / category / f"{name}.png"
