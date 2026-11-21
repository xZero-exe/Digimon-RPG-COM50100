"""Gráficos opcionales a partir de CSV existentes; requiere matplotlib.

Uso: python scripts/plot_results.py --dir resultados
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def moving_average(values: list[float], window: int) -> list[float]:
    acc = 0.0
    out = []
    for index, value in enumerate(values):
        acc += value
        if index >= window:
            acc -= values[index - window]
        out.append(acc / min(index + 1, window))
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", type=Path, default=Path("resultados"))
    args = parser.parse_args()
    try:
        import matplotlib.pyplot as plt
    except ImportError as e:
        raise SystemExit("Para gráficos, instala matplotlib: python -m pip install matplotlib") from e

    with (args.dir / "monte_carlo_entrenamiento.csv").open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    x = [int(r["episodio"]) for r in rows]
    wins = [1.0 if r["victoria"] == "True" else 0.0 for r in rows]
    rewards = [float(r["recompensa"]) for r in rows]
    window = max(25, min(500, len(x) // 20))

    plt.figure(figsize=(9, 4.5))
    plt.plot(x, moving_average(wins, window))
    plt.ylim(-0.03, 1.03)
    plt.xlabel("Episodios de entrenamiento")
    plt.ylabel("Fracción de victorias (media móvil)")
    plt.title(f"Monte Carlo: aprendizaje ({window} episodios)")
    plt.grid(alpha=0.2)
    plt.tight_layout()
    plt.savefig(args.dir / "victorias_mc.png", dpi=160)
    plt.close()

    plt.figure(figsize=(9, 4.5))
    plt.plot(x, moving_average(rewards, window))
    plt.xlabel("Episodios de entrenamiento")
    plt.ylabel("Recompensa media móvil")
    plt.title(f"Monte Carlo: recompensa ({window} episodios)")
    plt.grid(alpha=0.2)
    plt.tight_layout()
    plt.savefig(args.dir / "recompensa_mc.png", dpi=160)
    plt.close()

    with (args.dir / "comparacion.json").open(encoding="utf-8") as f:
        data = json.load(f)
    plt.figure(figsize=(7, 4))
    algorithms = ["Value Iteration", "Monte Carlo"]
    scores = [data["dynamic_programming"]["win_rate"] * 100,
              data["monte_carlo"]["win_rate"] * 100]
    bars = plt.bar(algorithms, scores)
    for bar, score in zip(bars, scores):
        plt.text(bar.get_x() + bar.get_width() / 2, score + 1, f"{score:.1f}%", ha="center")
    plt.ylim(0, 108)
    plt.ylabel("Victorias en evaluación (%)")
    plt.title("Comparación de políticas (una semilla)")
    plt.tight_layout()
    plt.savefig(args.dir / "comparacion_politicas.png", dpi=160)
    plt.close()
    print(f"Gráficos generados en {args.dir.resolve()}")


if __name__ == "__main__":
    main()
