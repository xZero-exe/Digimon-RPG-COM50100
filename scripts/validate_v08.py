"""Entrenamiento y evaluación reproducible de la versión 0.8 (Python puro)."""
from __future__ import annotations
import csv
import json
from pathlib import Path
from time import perf_counter
from digimon_rl.agents import ValueIterationAgent, MonteCarloAgent
from digimon_rl.environment import DigitalWorld
from digimon_rl.experiments import evaluate, sample_adventure
from digimon_rl.domain import Action, GameState
from digimon_rl.policy_io import save_policy

ROOT = Path(__file__).resolve().parents[1]
SEED = 42
EPISODES = 90000

def main() -> None:
    world = DigitalWorld()
    print('Estados nominales:', world.total_nominal_states(),flush=True)
    t = perf_counter()
    reachable = world.reachable_states()
    print('Estados alcanzables:',len(reachable),'BFS s:',round(perf_counter()-t,2),flush=True)
    t = perf_counter()
    dp = ValueIterationAgent(world, gamma=0.95).train()
    dp_seconds = round(perf_counter()-t,3)
    print('DP: estados',len(dp.policy),'iteraciones',len(dp.deltas),'segundos',dp_seconds,flush=True)
    t = perf_counter()
    mc=MonteCarloAgent(world,gamma=0.95,epsilon=0.15,seed=SEED)
    mc.train(episodes=EPISODES)
    mc_seconds=round(perf_counter()-t,3)
    policy=mc.deterministic_policy()
    print('MC: estados vistos',len(policy),'segundos',mc_seconds,flush=True)
    dp_eval=evaluate(world,dp.policy,episodes=500,seed=2042)
    mc_eval=evaluate(world,policy,episodes=500,seed=2042)
    print('Evaluación DP',dp_eval,flush=True)
    print('Evaluación MC',mc_eval,flush=True)
    (ROOT/'politicas').mkdir(exist_ok=True)
    save_policy(ROOT/'politicas'/'dp.json',dp.policy,algorithm='value_iteration',gamma=0.95)
    save_policy(ROOT/'politicas'/'mc.json',policy,algorithm='monte_carlo_first_visit',gamma=0.95,seed=SEED,episodes=EPISODES)
    results=ROOT/'resultados'
    results.mkdir(exist_ok=True)
    rows=[]
    for i in range(0,EPISODES,500):
        samples=mc.history[i:i+500]
        rows.append({'episodes':i+len(samples),
                     'win_rate':sum(x[2] for x in samples)/len(samples),
                     'mean_reward':sum(x[1] for x in samples)/len(samples)})
    with (results/'entrenamiento_v0_8.csv').open('w',encoding='utf8',newline='') as file:
        writer=csv.DictWriter(file,fieldnames=['episodes','win_rate','mean_reward'])
        writer.writeheader();writer.writerows(rows)
    example=sample_adventure(world,dp.policy,seed=4)
    data={'version':'0.8.0','seed':SEED,'mc_training_episodes':EPISODES,'eval_episodes':500,
          'nominal_states':world.total_nominal_states(),'reachable_states':len(reachable),
          'trained_states':sum(s.trained for s in reachable),
          'dp_train_seconds':dp_seconds,'mc_train_seconds':mc_seconds,
          'dp_iterations':len(dp.deltas),'dp_policy_states':len(dp.policy),
          'mc_policy_states':len(policy),
          'dp_training_actions':sum(a==Action.TRAIN for a in dp.policy.values()),
          'mc_training_actions':sum(a==Action.TRAIN for a in policy.values()),
          'dp':vars(dp_eval),'mc':vars(mc_eval),
          'dp_sample':{'won':example.won,'steps':len(example.steps),'used_training':any(s.action==Action.TRAIN for s in example.steps),
                       'actions':[s.action.value for s in example.steps]}}
    (results/'validacion_v0_8.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8')
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        fig,ax=plt.subplots(figsize=(9,4.5))
        ax.plot([r['episodes'] for r in rows],[r['win_rate']*100 for r in rows])
        ax.set(xlabel='Episodios de entrenamiento',ylabel='Victorias por bloque de 500 (%)',title='Monte Carlo: entrenamiento v0.8',ylim=(0,105))
        fig.tight_layout();fig.savefig(results/'entrenamiento_v0_8.png',dpi=150);plt.close(fig)
        fig,ax=plt.subplots(figsize=(7,4.3))
        vals=[dp_eval.win_rate*100,mc_eval.win_rate*100]
        bars=ax.bar(['Programación Dinámica','Monte Carlo'],vals)
        for b,v in zip(bars,vals):ax.text(b.get_x()+b.get_width()/2,b.get_height()+1,f'{v:.1f}%',ha='center')
        ax.set(ylabel='Victorias (%)',ylim=(0,108),title='Comparación de políticas v0.8 (500 episodios)')
        fig.tight_layout();fig.savefig(results/'comparacion_v0_8.png',dpi=150);plt.close(fig)
    except ImportError:
        print('Matplotlib no instalado. Solo CSV y JSON generados.',flush=True)
    print('DONE',flush=True)

if __name__=='__main__':main()
