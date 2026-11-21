"""Inspección reproducible sin Pygame: python -m digimon_rl.inspect_policies.

Presenta Q*(s,a) de Bellman y estimaciones Q_MC de visitas completas.
"""
from __future__ import annotations
import argparse
import csv
from pathlib import Path

from .environment import DigitalWorld
from .inspector import PolicyInspector, _restore_state
from .policy_io import load_policy


def main() -> None:
    parser = argparse.ArgumentParser(description="Analizar decisiones DP y MC sin Pygame")
    parser.add_argument("--policies", type=Path, default=Path("politicas"))
    parser.add_argument("--state", type=str, default=None,
                        help="10 enteros CSV: zona,PS,EN,PS enemigo,evol,pocion,carga,nucleo,XP,mejora")
    parser.add_argument("--csv", type=Path, default=None,
                        help="Exportar tabla de acciones al archivo CSV")
    args = parser.parse_args()
    world = DigitalWorld()
    dp = load_policy(args.policies / "dp.json", world)
    mc = load_policy(args.policies / "mc.json", world)
    inspector = PolicyInspector.from_export(world, dp, mc,
                                           args.policies / "analisis_v010.json.gz",
                                           args.policies / "dp.json",
                                           args.policies / "mc.json")
    try:
        state = _restore_state([int(v.strip()) for v in args.state.split(",")]) if args.state else world.start_state()
        insight = inspector.inspect(state)
    except (ValueError, KeyError) as exc:
        parser.error(f"Estado incorrecto: {exc}")
    print(f"Estado: {state.zone.label} / {state.form_name} / PS={state.hp} EN={state.energy}")
    print(f"Cobertura estados MC: {inspector.coverage:.1%}; pares visitados: {inspector.visited_pairs}")
    print(f"DP: {insight.dp_action.value if insight.dp_action else 'no disponible'}")
    print(f"MC: {insight.mc_action.value if insight.mc_action else 'no aprendida'}")
    rows = []
    for a in insight.actions:
        print(f"{a.label:23} DP={f'{a.dp_q:.3f}' if a.dp_q is not None else '---':>9} "
              f"MC={f'{a.mc_q:.3f}' if a.mc_q is not None else 'NO VISITADO':>11} n={a.mc_visits:>6}")
        rows.append({"accion": a.action.value, "q_dp": a.dp_q, "q_mc": a.mc_q,
                     "visitas_mc": a.mc_visits, "recomendada_dp": a.dp_recommended,
                     "recomendada_mc": a.mc_recommended})
    if args.csv:
        args.csv.parent.mkdir(parents=True, exist_ok=True)
        with args.csv.open("w", encoding="utf-8-sig", newline="") as fp:
            writer = csv.DictWriter(fp, fieldnames=list(rows[0]) if rows else ["accion"])
            writer.writeheader()
            writer.writerows(rows)
        print(f"CSV creado: {args.csv}")


if __name__ == "__main__":
    main()
