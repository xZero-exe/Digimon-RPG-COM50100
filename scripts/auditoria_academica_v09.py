"""Auditoría reproducible DP vs MC on-policy first-visit (COM50100; version 0.9).

Solo Python estándar; no descarga nada ni utiliza bibliotecas de RL.
Desde la raíz del proyecto:
 python scripts/auditoria_academica_v09.py --seeds 41,42,43,44,45 --mc-episodes 10000
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from dataclasses import asdict
from pathlib import Path
from statistics import mean, stdev
import sys
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from digimon_rl.agents import MonteCarloAgent
from digimon_rl.environment import DigitalWorld
from digimon_rl.experiments import evaluate
from digimon_rl.policy_io import load_policy


def stats(numbers):
    return {"mean": mean(numbers), "std_by_seed": stdev(numbers) if len(numbers) > 1 else 0.0,
            "minimum": min(numbers), "maximum": max(numbers)}


def svg_plot(records, output):
    """Gráfico SVG sencillo con solo Python estándar (eje Y: tasa victoria)."""
    w, h, padding = 900, 440, 80
    maxx = len(records) - 1 or 1
    x = lambda i: padding + (w - 2 * padding) * i / maxx
    y = lambda rate: h - padding - (h - 2 * padding) * rate
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<text x="80" y="35" font-size="20" font-family="sans-serif" font-weight="bold">Digimon RPG: victorias por semilla</text>',
        '<text x="80" y="58" font-size="12" font-family="sans-serif">Mismas semillas de evaluación para DP y MC dentro de cada corrida</text>',
        '<line x1="80" y1="360" x2="820" y2="360" stroke="#222"/>',
        '<line x1="80" y1="80" x2="80" y2="360" stroke="#222"/>',
    ]
    for fraction in (0, .25, .50, .75, 1):
        yy = y(fraction)
        lines.extend([f'<line x1="80" y1="{yy:.1f}" x2="820" y2="{yy:.1f}" stroke="#e4e7eb"/>',
                      f'<text x="45" y="{yy+4:.1f}" font-size="12" font-family="sans-serif">{int(fraction*100)}%</text>'])
    methods = [("dp_win_rate", "#2575a7"), ("mc_win_rate", "#df8c21")]
    for key, color in methods:
        points = " ".join(f"{x(i):.2f},{y(row[key]):.2f}" for i, row in enumerate(records))
        lines.append(f'<polyline fill="none" stroke="{color}" stroke-width="3" points="{points}"/>')
        for i, row in enumerate(records):
            lines.append(f'<circle cx="{x(i):.2f}" cy="{y(row[key]):.2f}" r="5" fill="{color}"/>')
    for i, row in enumerate(records):
        lines.append(f'<text x="{x(i):.1f}" y="383" text-anchor="middle" font-size="11" font-family="sans-serif">{row["seed"]}</text>')
    lines.extend(['<text x="420" y="410" text-anchor="middle" font-size="12" font-family="sans-serif">Semilla de entrenamiento MC</text>',
                  '<rect x="560" y="25" width="12" height="12" fill="#2575a7"/><text x="578" y="36" font-size="12" font-family="sans-serif">Value Iteration</text>',
                  '<rect x="710" y="25" width="12" height="12" fill="#df8c21"/><text x="728" y="36" font-size="12" font-family="sans-serif">Monte Carlo</text>',
                  '</svg>'])
    output.write_text("\n".join(lines), encoding="utf-8")


def run(seeds: list[int], mc_episodes: int, evaluation_episodes: int,
        max_steps: int, output: Path, gamma: float, epsilon: float, window: int):
    output.mkdir(parents=True, exist_ok=True)
    world = DigitalWorld()
    dp_policy = load_policy(ROOT / "politicas" / "dp.json", world)
    print(f"DP cargada desde disco: {len(dp_policy)} estados; no es necesario recalcularla")
    rows = []
    learning_rows = []
    for i, seed in enumerate(seeds):
        mc = MonteCarloAgent(world, gamma=gamma, epsilon=epsilon, seed=seed)
        mc.train(episodes=mc_episodes, max_steps=max_steps)
        policy = mc.deterministic_policy()
        evaluation_seed = 2042 + 19 * i
        dp = evaluate(world, dp_policy, episodes=evaluation_episodes,
                      gamma=gamma, seed=evaluation_seed, max_steps=max_steps)
        ev = evaluate(world, policy, episodes=evaluation_episodes,
                      gamma=gamma, seed=evaluation_seed, max_steps=max_steps)
        row = {
            "seed": seed, "evaluation_seed": evaluation_seed,
            "dp_win_rate": dp.win_rate, "mc_win_rate": ev.win_rate,
            "dp_return": dp.mean_discounted_return, "mc_return": ev.mean_discounted_return,
            "dp_truncated_eval": dp.truncated, "mc_truncated_eval": ev.truncated,
            "mc_train_completed": mc.completed_episodes,
            "mc_train_truncated": mc.truncated_episodes,
            "mc_visited_states": mc.visited_states,
            "mc_visited_pairs": mc.visited_pairs,
            "mc_coverage_reachable": mc.visited_states / len(dp_policy),
            "mc_fallback_actions": ev.fallback_actions,
            "mc_fallback_episodes": ev.fallback_episodes,
            "mc_fallback_action_rate": ev.fallback_action_rate,
            "mc_unseen_states_encountered": ev.distinct_unseen_states,
        }
        rows.append(row)
        for start in range(0, len(mc.history), window):
            block = mc.history[start:start + window]
            learning_rows.append({"seed": seed, "episode": block[-1][0],
                                  "mean_training_reward": mean(e[1] for e in block),
                                  "training_win_rate": sum(e[2] for e in block)/len(block)})
        print(f"MC semilla={seed}: victoria {ev.win_rate:.1%}; DP {dp.win_rate:.1%}; "
              f"cobertura={row['mc_coverage_reachable']:.1%}; "
              f"respaldo={ev.fallback_actions} acciones; truncados entrenamiento={mc.truncated_episodes}", flush=True)
    with (output / "resultados_por_semilla.csv").open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    with (output / "aprendizaje_por_bloques.csv").open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=list(learning_rows[0]))
        writer.writeheader()
        writer.writerows(learning_rows)
    summary = {
        "method_mc": "on-policy first-visit MC control epsilon-greedy; no exploring starts",
        "method_dp": "value iteration",
        "source_catedra": "Catedra 13 Monte Carlo Methods III, diapositiva 8",
        "environment_version": "v0.9-tecnicas-por-forma",
        "parameters": {"seeds": seeds, "mc_episodes_per_seed": mc_episodes,
                       "evaluation_episodes_per_method_per_seed": evaluation_episodes,
                       "gamma": gamma, "epsilon": epsilon, "max_steps": max_steps},
        "limitations": [
            "Aventuras interrumpidas por max_steps no se actualizan en MC: no hay retorno terminal observado.",
            "Los estados desconocidos se resuelven con primera acción legal, pero se contabilizan.",
            "La comparación de DP y MC usa las mismas semillas de evaluación dentro de cada corrida; no asegura trayectorias idénticas.",
            "La dispersión por semillas describe estas corridas y no garantiza un intervalo de confianza poblacional.",
            "DP guardada con gamma=0.95; para cambiar gamma hay que recalcularla.",
        ],
        "metrics": {
            "dp_win_rate": stats([r["dp_win_rate"] for r in rows]),
            "mc_win_rate": stats([r["mc_win_rate"] for r in rows]),
            "win_rate_gap_dp_minus_mc": stats([r["dp_win_rate"] - r["mc_win_rate"] for r in rows]),
            "dp_discounted_return": stats([r["dp_return"] for r in rows]),
            "mc_discounted_return": stats([r["mc_return"] for r in rows]),
            "mc_coverage_reachable": stats([r["mc_coverage_reachable"] for r in rows]),
            "mc_fallback_action_rate": stats([r["mc_fallback_action_rate"] for r in rows]),
            "mc_truncated_train": stats([r["mc_train_truncated"] for r in rows]),
        },
        "per_seed": rows,
    }
    (output / "resumen_multisemilla.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    svg_plot(rows, output / "comparacion_multisemilla.svg")
    print("Resumen:", json.dumps(summary["metrics"], indent=2))
    print("Archivos:", output.resolve())
    return summary


def main():
    p = argparse.ArgumentParser(description="Auditoría de Monte Carlo First-Visit del RPG")
    p.add_argument("--seeds", default="41,42,43,44,45")
    p.add_argument("--mc-episodes", type=int, default=10000)
    p.add_argument("--eval-episodes", type=int, default=300)
    p.add_argument("--max-steps", type=int, default=80)
    p.add_argument("--gamma", type=float, default=0.95)
    p.add_argument("--epsilon", type=float, default=0.15)
    p.add_argument("--window", type=int, default=500)
    p.add_argument("--output", type=Path, default=ROOT / "resultados" / "auditoria_v0_9")
    args = p.parse_args()
    if args.gamma != 0.95:
        p.error("La política DP incluida tiene gamma=0.95. Recalcula DP antes de cambiarlo.")
    if args.mc_episodes < 1 or args.eval_episodes < 1 or args.max_steps < 1 or args.window < 1:
        p.error("Los tamaños y el límite de pasos deben ser positivos")
    try:
        seeds = list(dict.fromkeys(int(x.strip()) for x in args.seeds.split(",")))
        if not seeds:
            raise ValueError("no seeds")
    except ValueError:
        p.error("Especifica las semillas como enteros separados por comas")
    run(seeds, args.mc_episodes, args.eval_episodes, args.max_steps,
        args.output, args.gamma, args.epsilon, args.window)


if __name__ == "__main__":
    main()
