"""Ejecutar: python -m digimon_rl --episodes 10000 --output resultados"""
from __future__ import annotations

import argparse
import csv
import json
from dataclasses import asdict
from pathlib import Path

from .agents import MonteCarloAgent, ValueIterationAgent
from .domain import Ending, GameState
from .environment import DigitalWorld
from .experiments import evaluate, sample_adventure


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Digimon RPG RL: comparar Value Iteration y control Monte Carlo")
    parser.add_argument("--episodes", type=int, default=10000,
                        help="Episodios de entrenamiento Monte Carlo (por defecto: 10000)")
    parser.add_argument("--eval-episodes", type=int, default=500,
                        help="Episodios de evaluación por agente (por defecto: 500)")
    parser.add_argument("--gamma", type=float, default=0.95)
    parser.add_argument("--epsilon", type=float, default=0.15)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", type=Path, default=Path("resultados"))
    args = parser.parse_args()
    if args.episodes < 1 or args.eval_episodes < 1:
        parser.error("--episodes y --eval-episodes deben ser positivos")
    args.output.mkdir(parents=True, exist_ok=True)

    world = DigitalWorld()
    print("=== Digimon: La corrupción del Mundo Digital ===")
    print(f"Estados nominales: {world.total_nominal_states():,}")
    print("Calculando estados alcanzables...")
    reachable = world.reachable_states()
    print(f"Estados alcanzables: {len(reachable):,} (+ terminales)")

    print("Entrenando Programación Dinámica (Value Iteration)...")
    dp = ValueIterationAgent(world, gamma=args.gamma).train()
    print(f"Convergencia DP: {len(dp.deltas)} iteraciones; delta final={dp.deltas[-1]:.3g}")

    print(f"Entrenando Monte Carlo: {args.episodes:,} episodios...")
    mc = MonteCarloAgent(world, gamma=args.gamma, epsilon=args.epsilon, seed=args.seed)
    mc.train(episodes=args.episodes)
    mc_policy = mc.deterministic_policy()
    print(f"MC: completos={mc.completed_episodes}, truncados={mc.truncated_episodes}, "
          f"estados visitados={mc.visited_states}, pares visitados={mc.visited_pairs}")

    # Misma semilla y mismo entorno para ambas políticas.
    dp_eval = evaluate(world, dp.policy, episodes=args.eval_episodes, seed=args.seed + 1,
                       gamma=args.gamma)
    mc_eval = evaluate(world, mc_policy, episodes=args.eval_episodes, seed=args.seed + 1,
                       gamma=args.gamma)

    for label, result in (("DP", dp_eval), ("MC", mc_eval)):
        print(f"{label}: victorias={result.win_rate:.1%}, "
              f"recompensa media={result.mean_reward:.2f}, "
              f"retorno descontado={result.mean_discounted_return:.2f}, "
              f"turnos medios={result.mean_steps:.1f}, "
          f"acciones de respaldo={result.fallback_actions} "
          f"({result.fallback_action_rate:.2%})")

    with (args.output / "comparacion.json").open("w", encoding="utf-8") as fp:
        json.dump({
            "config": {"episodes_mc": args.episodes, "evaluation_episodes": args.eval_episodes,
                       "gamma": args.gamma, "epsilon": args.epsilon, "seed": args.seed},
            "states": {"nominal": world.total_nominal_states(), "reachable": len(reachable)},
            "dynamic_programming": asdict(dp_eval),
            "monte_carlo": asdict(mc_eval),
            "dp_iterations": len(dp.deltas),
            "dp_last_delta": dp.deltas[-1],
        }, fp, ensure_ascii=False, indent=2)

    with (args.output / "monte_carlo_entrenamiento.csv").open("w", newline="", encoding="utf-8") as fp:
        writer = csv.writer(fp)
        writer.writerow(["episodio", "recompensa", "victoria", "turnos"])
        writer.writerows(mc.history)

    with (args.output / "convergencia_dp.csv").open("w", newline="", encoding="utf-8") as fp:
        writer = csv.writer(fp)
        writer.writerow(["iteracion", "delta"])
        writer.writerows(enumerate(dp.deltas, start=1))

    print("\n--- Aventura de ejemplo con política DP ---")
    adventure = sample_adventure(world, dp.policy, seed=args.seed + 10)
    for index, step in enumerate(adventure.steps, 1):
        s = step.state
        actor = s.form_name
        print(f"{index:02} | {s.zone.label:20s} | {actor:13s} "
              f"HP {s.hp}/{world.MAX_HP} E {s.energy}/{world.MAX_ENERGY} "
              f"Enemigo {s.enemy_hp} | {step.action.value:17s} | r={step.reward:+.1f}")
    outcome = adventure.final_state.value if isinstance(adventure.final_state, Ending) else "truncado"
    print(f"Final: {outcome}; recompensa acumulada: {adventure.total_reward:.2f}")
    print(f"\nArchivos de resultados: {args.output.resolve()}")


if __name__ == "__main__":
    main()
