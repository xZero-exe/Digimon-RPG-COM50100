"""Entrena y guarda políticas: python -m digimon_rl.train --episodes 10000"""
from __future__ import annotations

import argparse
from pathlib import Path

from .agents import MonteCarloAgent, ValueIterationAgent
from .environment import DigitalWorld
from .policy_io import save_policy


def main() -> None:
    parser = argparse.ArgumentParser(description="Entrenar y exportar las políticas del RPG")
    parser.add_argument("--episodes", type=int, default=10000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--gamma", type=float, default=0.95)
    parser.add_argument("--epsilon", type=float, default=0.15)
    parser.add_argument("--output", type=Path, default=Path("politicas"))
    args = parser.parse_args()
    if args.episodes < 1:
        parser.error("--episodes debe ser mayor a cero")
    world = DigitalWorld()
    print("Calculando Value Iteration...")
    dp = ValueIterationAgent(world, gamma=args.gamma).train()
    save_policy(args.output / "dp.json", dp.policy, algorithm="value_iteration", gamma=args.gamma)
    print(f"Programación Dinámica: {len(dp.policy)} estados; {len(dp.deltas)} iteraciones")
    print(f"Entrenando Monte Carlo durante {args.episodes:,} episodios...")
    mc = MonteCarloAgent(world, gamma=args.gamma, epsilon=args.epsilon, seed=args.seed)
    mc.train(episodes=args.episodes)
    policy = mc.deterministic_policy()
    save_policy(args.output / "mc.json", policy, algorithm="monte_carlo_first_visit",
                gamma=args.gamma, episodes=args.episodes, seed=args.seed)
    print(f"Monte Carlo: {len(policy)} estados aprendidos; "
          f"{mc.visited_pairs} pares (s,a); "
          f"{mc.completed_episodes} episodios completos y "
          f"{mc.truncated_episodes} truncados excluidos de Q")
    print(f"Políticas guardadas en: {args.output.resolve()}")


if __name__ == "__main__":
    main()
