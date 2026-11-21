"""Convergencia experimental de MC First-Visit on-policy vs Value Iteration.

ÚNICOS algoritmos RL: implementaciones propias en digimon_rl.agents.
No usa bibliotecas de RL ni requiere Pygame o Matplotlib para los gráficos SVG.

Ejemplo:
 python scripts/curvas_aprendizaje_v011.py --seeds 41,42,43,44,45 \\
   --checkpoints 500,2000,5000,10000,20000 --eval-episodes 200
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from statistics import mean, stdev
import sys
from time import perf_counter
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'src'
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from digimon_rl.agents import MonteCarloAgent
from digimon_rl.environment import DigitalWorld
from digimon_rl.experiments import evaluate
from digimon_rl.policy_io import load_policy


DEFAULT_CHECKPOINTS = (500, 2000, 5000, 10000, 20000)
DEFAULT_SEEDS = (41, 42, 43, 44, 45)


def parse_ints(raw: str) -> tuple[int, ...]:
    """Parsea una lista CSV sin aceptar valores repetidos, nulos o negativos."""
    items = tuple(int(v.strip()) for v in raw.split(','))
    if not items or any(v < 1 for v in items) or len(set(items)) != len(items):
        raise ValueError('Se requieren enteros positivos no repetidos')
    return items


def summarize(values: list[float]) -> dict[str, float]:
    return {'mean': mean(values), 'std': stdev(values) if len(values) > 1 else 0.0,
            'minimum': min(values), 'maximum': max(values)}


def group_summary(rows: list[dict], checkpoints: tuple[int, ...]) -> list[dict]:
    results = []
    for cp in checkpoints:
        group = [row for row in rows if row['checkpoint'] == cp]
        results.append({
            'checkpoint': cp,
            'n_seeds': len(group),
            'mc_win_rate': summarize([r['mc_win_rate'] for r in group]),
            'dp_win_rate': summarize([r['dp_win_rate'] for r in group]),
            'win_rate_gap': summarize([r['dp_win_rate'] - r['mc_win_rate'] for r in group]),
            'mc_discounted_return': summarize([r['mc_discounted_return'] for r in group]),
            'dp_discounted_return': summarize([r['dp_discounted_return'] for r in group]),
            'mc_state_coverage': summarize([r['mc_state_coverage'] for r in group]),
            'mc_fallback_action_rate': summarize([r['mc_fallback_action_rate'] for r in group]),
        })
    return results


def render_curve(data: list[dict], filename: Path, key: str, dp_key: str | None,
                 heading: str, ylabel: str) -> None:
    """Curva de promedios, desviación estándar muestral y DP como referencia."""
    w, h = 1000, 500
    x0, x1, y0, y1 = 100, 940, 110, 405
    n = len(data)
    xpos = lambda i: (x0 + (x1-x0)*i/(n-1)) if n > 1 else (x0+x1)/2
    ypos = lambda value: y1 - max(0.0, min(1.0, value)) * (y1-y0)
    texts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">',
        '<rect width="100%" height="100%" fill="white"/>',
        f'<text x="100" y="44" font-family="sans-serif" font-size="24" font-weight="bold" fill="#18202b">{escape(heading)}</text>',
        '<text x="100" y="70" font-family="sans-serif" font-size="13" fill="#4e5762">Medias por semilla; barras verticales: ±1 desviación estándar (muestral)</text>',
    ]
    for frac in (0, .25, .5, .75, 1.0):
        yy = ypos(frac)
        texts.append(f'<line x1="{x0}" x2="{x1}" y1="{yy:.1f}" y2="{yy:.1f}" stroke="#e0e3e8"/>')
        texts.append(f'<text x="{x0-14}" y="{yy+4:.1f}" font-size="13" text-anchor="end" fill="#555">{frac:.0%}</text>')
    texts.append(f'<text transform="translate(24 255) rotate(-90)" font-family="sans-serif" font-size="14">{escape(ylabel)}</text>')
    texts.append(f'<line x1="{x0}" x2="{x1}" y1="{y1}" y2="{y1}" stroke="#333"/>')
    for i, entry in enumerate(data):
        xx = xpos(i)
        texts.append(f'<text x="{xx:.1f}" y="{y1+25}" font-size="13" text-anchor="middle">{entry["checkpoint"]:,}</text>')
    texts.append('<text x="515" y="463" font-family="sans-serif" font-size="14" text-anchor="middle">Episodios acumulados de entrenamiento Monte Carlo</text>')
    if dp_key:
        baseline = mean([r[dp_key]['mean'] for r in data])
        yy = ypos(baseline)
        texts.append(f'<line x1="{x0}" x2="{x1}" y1="{yy:.1f}" y2="{yy:.1f}" stroke="#777" stroke-width="2" stroke-dasharray="8 5"/>')
        texts.append(f'<text x="{x1-3}" y="{yy-8:.1f}" font-size="12" text-anchor="end" fill="#555">DP {baseline:.1%}</text>')
    points = []
    for i, entry in enumerate(data):
        xx = xpos(i)
        val = entry[key]['mean']
        low, high = ypos(val-entry[key]['std']), ypos(val+entry[key]['std'])
        points.append(f'{xx:.1f},{ypos(val):.1f}')
        texts.append(f'<line x1="{xx:.1f}" y1="{low:.1f}" x2="{xx:.1f}" y2="{high:.1f}" stroke="#222" stroke-width="1.7"/>')
        texts.append(f'<line x1="{xx-6:.1f}" y1="{low:.1f}" x2="{xx+6:.1f}" y2="{low:.1f}" stroke="#222"/>')
        texts.append(f'<line x1="{xx-6:.1f}" y1="{high:.1f}" x2="{xx+6:.1f}" y2="{high:.1f}" stroke="#222"/>')
    texts.append(f'<polyline fill="none" stroke="#1b2733" stroke-width="3" points="{" ".join(points)}"/>')
    for i, entry in enumerate(data):
        xx, yy = xpos(i), ypos(entry[key]['mean'])
        texts.append(f'<circle cx="{xx:.1f}" cy="{yy:.1f}" r="5.5" fill="white" stroke="#1b2733" stroke-width="2.5"/>')
        texts.append(f'<text x="{xx:.1f}" y="{yy-15:.1f}" text-anchor="middle" font-size="12" fill="#18202b">{entry[key]["mean"]:.1%}</text>')
    texts.append('</svg>')
    filename.write_text('\n'.join(texts), encoding='utf-8')


def run(seeds: tuple[int, ...], checkpoints: tuple[int, ...], eval_episodes: int,
        max_steps: int, output: Path, gamma: float = .95, epsilon: float = .15) -> dict:
    if gamma != .95:
        raise ValueError('La política DP guardada usa gamma=0.95. Recalcula DP antes de cambiar gamma.')
    if eval_episodes < 1 or max_steps < 1:
        raise ValueError('eval-episodes y max-steps deben ser positivos')
    if tuple(sorted(checkpoints)) != checkpoints:
        raise ValueError('Los puntos de control deben estar en orden creciente')
    output.mkdir(parents=True, exist_ok=True)
    world = DigitalWorld()
    dp = load_policy(ROOT / 'politicas' / 'dp.json', world)
    nstates = len(dp)
    rows: list[dict] = []
    for i, seed in enumerate(seeds):
        evaluation_seed = 20261102 + i * 101
        baseline = evaluate(world, dp, episodes=eval_episodes, seed=evaluation_seed,
                            gamma=gamma, max_steps=max_steps)
        mc = MonteCarloAgent(world, gamma=gamma, epsilon=epsilon, seed=seed)
        last_checkpoint = 0
        elapsed = 0.0
        for cp in checkpoints:
            start_time = perf_counter()
            mc.train(episodes=cp-last_checkpoint, max_steps=max_steps)
            elapsed += perf_counter() - start_time
            if len(mc.history) != cp or mc.history[-1][0] != cp:
                raise RuntimeError('Numeración de episodios interrumpida')
            evaluation = evaluate(world, mc.deterministic_policy(), episodes=eval_episodes,
                                  seed=evaluation_seed, gamma=gamma, max_steps=max_steps)
            last_window = mc.history[max(0, cp-500):cp]
            row = {
                'seed': seed, 'evaluation_seed': evaluation_seed, 'checkpoint': cp,
                'mc_win_rate': evaluation.win_rate, 'dp_win_rate': baseline.win_rate,
                'mc_discounted_return': evaluation.mean_discounted_return,
                'dp_discounted_return': baseline.mean_discounted_return,
                'mc_mean_steps': evaluation.mean_steps,
                'mc_state_coverage': mc.visited_states/nstates,
                'mc_visited_states': mc.visited_states,
                'mc_visited_pairs': mc.visited_pairs,
                'mc_fallback_action_rate': evaluation.fallback_action_rate,
                'mc_fallback_actions': evaluation.fallback_actions,
                'mc_unseen_eval_states': evaluation.distinct_unseen_states,
                'mc_truncated_train': mc.truncated_episodes,
                'mc_truncated_eval': evaluation.truncated,
                'dp_truncated_eval': baseline.truncated,
                'recent_train_win_rate': sum(e[2] for e in last_window)/len(last_window),
                'train_time_seconds': round(elapsed,3),
            }
            rows.append(row)
            last_checkpoint = cp
            print(f'semilla={seed} episodios={cp}: MC {evaluation.win_rate:.1%}, '
                  f'DP {baseline.win_rate:.1%}, cobertura MC {row["mc_state_coverage"]:.1%}, '
                  f'respaldo {row["mc_fallback_actions"]}', flush=True)
    summary = group_summary(rows, checkpoints)
    with (output / 'resultados_por_semilla_y_checkpoint.csv').open('w', encoding='utf-8', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    with (output / 'curvas_resumen.csv').open('w', encoding='utf-8', newline='') as file:
        fields = ['checkpoint','n_seeds','mc_win_mean','mc_win_sd','dp_win_mean',
                  'mc_coverage_mean','mc_coverage_sd','fallback_mean',
                  'mc_return_mean','dp_return_mean']
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        for s in summary:
            writer.writerow({
                'checkpoint': s['checkpoint'], 'n_seeds': s['n_seeds'],
                'mc_win_mean': s['mc_win_rate']['mean'], 'mc_win_sd': s['mc_win_rate']['std'],
                'dp_win_mean': s['dp_win_rate']['mean'],
                'mc_coverage_mean': s['mc_state_coverage']['mean'],
                'mc_coverage_sd': s['mc_state_coverage']['std'],
                'fallback_mean': s['mc_fallback_action_rate']['mean'],
                'mc_return_mean': s['mc_discounted_return']['mean'],
                'dp_return_mean': s['dp_discounted_return']['mean'],
            })
    render_curve(summary, output / 'convergencia_v011.svg', 'mc_win_rate', 'dp_win_rate',
                 'Convergencia: MC frente a Value Iteration', 'Tasa de victoria')
    render_curve(summary, output / 'cobertura_v011.svg', 'mc_state_coverage', None,
                 'Cobertura de estados de Monte Carlo', 'Estados alcanzables visitados')
    report = {
        'title': 'Curvas MC On-policy First-Visit - COM50100',
        'algorithms': {'dp': 'Value Iteration tabular desde Bellman',
                       'mc': 'Control First-Visit on-policy epsilon-greedy (Cátedra 13)'},
        'dependencies_rl': [], 'numeric_backend_dp': 'numpy',
        'method': 'Una sola trayectoria de entrenamiento MC por semilla con checkpoints acumulativos. '
                  'Para cada semilla se reutiliza el mismo seed de evaluación en todos los checkpoints y para DP.',
        'settings': {'train_seeds': seeds, 'checkpoints': checkpoints,
                     'evaluation_episodes_per_seed_method_checkpoint': eval_episodes,
                     'max_steps': max_steps, 'gamma': gamma, 'epsilon': epsilon,
                     'reachable_states': nstates, 'date_context': '2026-11-02'},
        'per_seed': rows, 'by_checkpoint': summary,
        'caveats': [
            'La desviación estándar entre semillas no prueba convergencia matemática.',
            'Las mismas semillas de evaluación ayudan al control experimental, pero las trayectorias de políticas distintas no coinciden necesariamente.',
            'La política DP precomputada usa gamma=0.95 y el MDP v0.9; ambas políticas deben aplicar exactamente las mismas reglas.',
            'La cobertura de estados cuenta estados donde al menos un (s,a) fue actualizado; no demuestra optimalidad.',
            'Los episodios truncados no actualizan Q y se registran explícitamente.',
            'El MC evalúa una política greedy tras entrenar una política de comportamiento epsilon-greedy.',
            'Los sprites de terceros no deben publicarse sin permiso de los artistas.',
        ],
    }
    (output / 'resumen_v011.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    return report


def main() -> None:
    if getattr(DigitalWorld, "RULES_VERSION", "v0.9-tecnicas-por-forma") != "v0.9-tecnicas-por-forma":
        raise SystemExit("Las curvas v0.11 requieren la edición v0.19. Usa scripts/curvas_aprendizaje_v020.py para el balance actual.")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--seeds', default=','.join(map(str,DEFAULT_SEEDS)))
    parser.add_argument('--checkpoints', default=','.join(map(str, DEFAULT_CHECKPOINTS)))
    parser.add_argument('--eval-episodes', type=int, default=200)
    parser.add_argument('--max-steps', type=int, default=80)
    parser.add_argument('--gamma', type=float, default=.95)
    parser.add_argument('--epsilon', type=float, default=.15)
    parser.add_argument('--output', type=Path, default=ROOT/'resultados'/'convergencia_v011')
    args = parser.parse_args()
    try:
        seeds = parse_ints(args.seeds)
        checkpoints = parse_ints(args.checkpoints)
        run(seeds, checkpoints, args.eval_episodes, args.max_steps, args.output,
            args.gamma, args.epsilon)
    except ValueError as exc:
        parser.error(str(exc))


if __name__ == '__main__':
    main()
