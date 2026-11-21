"""Reentrenar solo Monte Carlo sin recalcular Value Iteration (v0.8.2)."""
from pathlib import Path
from dataclasses import asdict
import json
import sys
from time import perf_counter

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from digimon_rl.environment import DigitalWorld
from digimon_rl.agents import MonteCarloAgent
from digimon_rl.experiments import evaluate
from digimon_rl.policy_io import load_policy, save_policy


def main():
    world = DigitalWorld()
    start = perf_counter()
    agent = MonteCarloAgent(world, seed=42, gamma=.95, epsilon=.15)
    agent.train(episodes=90000, max_steps=80)
    policy = agent.deterministic_policy()
    save_policy(ROOT/'politicas/mc.json', policy,
                algorithm='monte_carlo_first_visit_on_policy_epsilon_greedy',
                gamma=.95, episodes=90000, seed=42)
    print('MC entrenado', round(perf_counter()-start, 1), 'segundos, completos:',
          agent.completed_episodes, 'truncados:', agent.truncated_episodes,
          'estados:', agent.visited_states, 'pares:', agent.visited_pairs, flush=True)
    evaluations = {}
    for name, existing in [('MC',policy),('DP',load_policy(ROOT/'politicas/dp.json',world))]:
        ev = evaluate(world, existing, episodes=500, seed=2042, gamma=.95, max_steps=80)
        print(name, ev, flush=True)
        evaluations[name] = asdict(ev)
    details = {
        'config': {'method': 'on-policy first-visit MC control epsilon-greedy',
                   'seed_train':42,'episodes_train':90000,'seed_eval':2042,
                   'episodes_eval':500,'gamma':.95,'epsilon':.15,'max_steps':80},
        'training': {'complete':agent.completed_episodes,'truncated':agent.truncated_episodes,
                     'visited_states':agent.visited_states,'visited_pairs':agent.visited_pairs},
        'evaluation': evaluations,
    }
    (ROOT/'resultados/auditoria_mc_v082.json').write_text(
        json.dumps(details,ensure_ascii=False,indent=2),encoding='utf-8')

if __name__=='__main__':
    main()
