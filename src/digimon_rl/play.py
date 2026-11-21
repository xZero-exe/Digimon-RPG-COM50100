"""Entrada al juego: python -m digimon_rl.play [--policies politicas]"""
from __future__ import annotations

import argparse
from pathlib import Path

from .environment import DigitalWorld
from .policy_io import load_policy
from .session import AdventureController


def main() -> None:
    parser = argparse.ArgumentParser(description="Interfaz Digimon RPG con Pygame")
    parser.add_argument("--policies", type=Path, default=Path("politicas"))
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--assets", type=Path, default=None,
                        help="Raíz assets, con demo/* ya incluido y archivos locales autorizados opcionales")
    args = parser.parse_args()

    try:
        import pygame  # noqa: F401
    except ImportError as exc:
        raise SystemExit('Falta Pygame. Instala con: python -m pip install -e ".[game]"') from exc

    world = DigitalWorld()
    try:
        dp = load_policy(args.policies / "dp.json", world)
        mc = load_policy(args.policies / "mc.json", world)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise SystemExit(
            f"No se pudieron cargar las políticas: {exc}\n"
            "Genera primero los archivos con: python -m digimon_rl.train --episodes 10000"
        ) from exc

    from .inspector import PolicyInspector
    analysis_path = args.policies / "analisis_v010.json.gz"
    inspector = None
    if analysis_path.exists():
        try:
            inspector = PolicyInspector.from_export(
                world, dp, mc, analysis_path,
                args.policies / "dp.json", args.policies / "mc.json")
        except (OSError, ValueError, KeyError, TypeError) as exc:
            print(f"Aviso: análisis no disponible ({exc}). El juego funciona normalmente.")

    from .academic_dashboard import AcademicDashboard
    results_dir = Path(__file__).resolve().parents[2] / "resultados" / "convergencia_v021"
    dashboard = None
    try:
        dashboard = AcademicDashboard.load(results_dir)
        if dashboard.rules_version != world.RULES_VERSION or dashboard.reachable_states != len(dp):
            raise ValueError("Los resultados académicos no corresponden a las reglas actuales")
    except (OSError, ValueError, KeyError, TypeError, StopIteration) as exc:
        dashboard = None
        print(f"Aviso: resultados académicos no disponibles ({exc}). El RPG sigue funcionando.")

    from .gui.app import RPGApp

    controller = AdventureController(world, dp, mc, seed=args.seed)
    RPGApp(controller, asset_root=args.assets, inspector=inspector, dashboard=dashboard).run()


if __name__ == "__main__":
    main()
