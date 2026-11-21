"""Entrena y evalúa de forma reproducible ambas políticas de la v0.6."""
from __future__ import annotations
import json
import csv
from pathlib import Path
from time import perf_counter
from digimon_rl.agents import ValueIterationAgent, MonteCarloAgent
from digimon_rl.environment import DigitalWorld
from digimon_rl.experiments import evaluate, sample_adventure
from digimon_rl.policy_io import save_policy
from digimon_rl.domain import Action, GameState, Zone

ROOT=Path(__file__).resolve().parents[1]
POLICIES=ROOT/'politicas'
RESULTS=ROOT/'resultados'
SEED=42
EPISODES=40000

def main():
    POLICIES.mkdir(exist_ok=True)
    RESULTS.mkdir(exist_ok=True)
    world=DigitalWorld()
    reachable=world.reachable_states()
    t=perf_counter()
    dp=ValueIterationAgent(world, gamma=0.95).train()
    dp_sec=perf_counter()-t
    save_policy(POLICIES/'dp.json',dp.policy,algorithm='value_iteration',gamma=0.95)
    print('DP:',len(dp.policy),'states',len(dp.deltas),'iterations',round(dp_sec,2),'sec',flush=True)
    t=perf_counter()
    mc=MonteCarloAgent(world,gamma=0.95,epsilon=0.15,seed=SEED)
    mc.train(episodes=EPISODES)
    mc_sec=perf_counter()-t
    policy=mc.deterministic_policy()
    save_policy(POLICIES/'mc.json',policy,algorithm='monte_carlo_first_visit',gamma=0.95,
                episodes=EPISODES,seed=SEED)
    print('MC:',len(policy),'states',round(mc_sec,2),'sec',flush=True)
    dp_eval=evaluate(world,dp.policy,episodes=500,seed=2042)
    mc_eval=evaluate(world,policy,episodes=500,seed=2042)
    rows=[]
    for i in range(0,EPISODES,500):
        samples=mc.history[i:i+500]
        rows.append({'episodes':i+len(samples),
                     'win_rate':sum(x[2] for x in samples)/len(samples),
                     'mean_reward':sum(x[1] for x in samples)/len(samples)})
    with (RESULTS/'entrenamiento_v0_6.csv').open('w',encoding='utf-8',newline='') as handle:
        writer=csv.DictWriter(handle,fieldnames=['episodes','win_rate','mean_reward']);writer.writeheader();writer.writerows(rows)
    summary={
       'version':'0.6.0','seed':SEED,'monte_carlo_episodes':EPISODES,'test_episodes':500,
       'state_nominal':world.total_nominal_states(),'state_reachable':len(reachable),
       'state_charging':sum(x.enemy_charging for x in reachable),
       'dp_train_seconds':round(dp_sec,3),'mc_train_seconds':round(mc_sec,3),
       'dp_iterations':len(dp.deltas),'dp_policy_states':len(dp.policy),
       'mc_policy_states':len(policy),
       'value_iteration':vars(dp_eval),
       'monte_carlo':vars(mc_eval),
       'example_run':[
          {'zone':step.state.zone.label,'form':step.state.form_name,
           'charged':step.state.enemy_charging,'action':step.action.value,'reward':step.reward}
          for step in sample_adventure(world,dp.policy,seed=4).steps
       ],
    }
    (RESULTS/'validacion_v0_6.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    print('DP evaluation:',dp_eval,flush=True)
    print('MC evaluation:',mc_eval,flush=True)
    print('Example DP actions:',[x['action'] for x in summary['example_run']],flush=True)
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(9,4.5))
        ax.plot([r['episodes'] for r in rows],[r['win_rate']*100 for r in rows])
        ax.set(xlabel='Episodios de entrenamiento',ylabel='Victorias por bloque de 500 (%)',
               title='Aprendizaje de Monte Carlo (v0.6)')
        ax.set_ylim(0,105)
        fig.tight_layout();fig.savefig(RESULTS/'entrenamiento_v0_6.png',dpi=150);plt.close(fig)
        fig, ax=plt.subplots(figsize=(7,4.3))
        bars=ax.bar(['Programación Dinámica','Monte Carlo'],[dp_eval.win_rate*100,mc_eval.win_rate*100])
        for b,v in zip(bars,[dp_eval.win_rate*100,mc_eval.win_rate*100]):
            ax.text(b.get_x()+b.get_width()/2,b.get_height()+1,f'{v:.1f}%',ha='center')
        ax.set(ylabel='Victorias (%)',ylim=(0,108),title='Evaluación de políticas · 500 aventuras')
        fig.tight_layout();fig.savefig(RESULTS/'comparacion_v0_6.png',dpi=150);plt.close(fig)
    except ImportError:
        print('matplotlib no disponible, gráficos opcionales omitidos')

if __name__=='__main__':main()
