"""Copia local de diez PNG desde una copia del repositorio Digidex.

NO descarga archivos. Se exige confirmar que se cuenta con permiso de uso.
Los PNG importados se excluyen del Git mediante .gitignore.

Ejemplo:
  python scripts/import_digidex_sprites.py --source C:/arte/digidex --i-have-permission
"""
from __future__ import annotations

import argparse
from pathlib import Path
import shutil

NAMES = ("agumon", "greymon", "betamon", "goblimon", "ogremon", "devimon", "piedmon")


def copy_authorized_assets(source: Path, target: Path, scale: str, permission: bool) -> tuple[str, ...]:
    if not permission:
        raise PermissionError("Se requiere autorización de los autores. Usa --i-have-permission solo si ya cuentas con ella.")
    origin = source / "resources" / "img" / "sprites" / scale
    if not origin.is_dir():
        raise FileNotFoundError(f"No existe: {origin}")
    missing = [name for name in NAMES if not (origin / f"{name}.png").is_file()]
    if missing:
        raise FileNotFoundError("Faltan sprites en la copia de Digidex: " + ", ".join(missing))
    target.mkdir(parents=True, exist_ok=True)
    for name in NAMES:
        shutil.copy2(origin / f"{name}.png", target / f"{name}.png")
    return NAMES


def main() -> None:
    parser = argparse.ArgumentParser(description="Instalar sprites de Digidex para uso local autorizado")
    parser.add_argument("--source", required=True, type=Path, help="Carpeta local del repositorio Digidex")
    parser.add_argument("--target", type=Path, default=Path("assets/digimon"))
    parser.add_argument("--scale", choices=("x1", "x2", "x5"), default="x5")
    parser.add_argument("--i-have-permission", action="store_true", help="Confirmo contar con permiso de los artistas para este uso")
    args = parser.parse_args()
    try:
        names = copy_authorized_assets(args.source, args.target, args.scale, args.i_have_permission)
    except (PermissionError, FileNotFoundError) as exc:
        parser.error(str(exc))
    print(f"Importados {len(names)} sprites a {args.target}: {', '.join(names)}")
    print("Recuerda acreditar a cada artista y no redistribuir los PNG sin permiso para ello.")


if __name__ == "__main__":
    main()
