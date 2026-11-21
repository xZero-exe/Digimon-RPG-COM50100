"""Recalcula políticas y mide el balance v0.20; solo VI y MC del curso.

Uso: python scripts/entrenar_balance_v020.py --episodes 60000
Las evaluaciones son greedy, con tres semillas y 1000 partidas por semilla.
No obliga a elegir una digievolución ni añade premios por usar WarGreymon.
"""
from __future__ import annotations
import argparse
from collections import Counter
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
from random import Random
import sys
from time import perf_counter
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from digimon_rl.agents import MonteCarloAgent,ValueIterationAgent
from digimon_rl.domain import Action,GameState,Zone
from digimon_rl.environment import DigitalWorld
from digimon_rl.experiments import evaluate
from digimon_rl.inspector import export_analysis
from digimon_rl.policy_io import save_policy


def form_metrics(world,policy,seed,episodes=1000):
    rng=Random(seed);forms=Counter();boss=war=fallback=losses=truncated=0
    for _ in range(episodes):
        def choose(s,legal,_rng):
            nonlocal fallback
            if s not in policy:fallback+=1
            return policy.get(s,legal[0])
        run=world.episode(choose,rng)
        boss+=any(x.state.zone==Zone.FORTRESS for x in run.steps)
        war+=any(x.state.evolved==3 for x in run.steps)
        if run.won:forms[run.steps[-1].state.form_name]+=1
        elif run.truncated:truncated+=1
        else:losses+=1
    return {'seed':seed,'episodes':episodes,'wins':sum(forms.values()),'losses':losses,
            'truncated':truncated,'boss_reached':boss,'used_wargreymon':war,
            'winning_form':dict(forms),'fallback_actions':fallback}


def main():
    if DigitalWorld.RULES_VERSION != "v0.20-balance-piedmon":
        raise SystemExit("Herramienta histórica v0.20: usa la correspondiente v0.21 para estas reglas.")
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--episodes',type=int,default=60000)
    args=parser.parse_args()
    if args.episodes<1:parser.error('episodes debe ser positivo')
    out=ROOT/'resultados/balance_v020';out.mkdir(parents=True,exist_ok=True)
    world=DigitalWorld();start=perf_counter()
    dp=ValueIterationAgent(world).train()
    print('DP:',len(dp.policy),'estados;',len(dp.deltas),'iteraciones; delta',dp.deltas[-1],flush=True)
    mc=MonteCarloAgent(world,gamma=.95,epsilon=.15,seed=42)
    for count in range(0,args.episodes,10000):
        mc.train(min(10000,args.episodes-count))
        print('MC:',len(mc.history),'episodios;',mc.visited_states,'estados',flush=True)
    mc_policy=mc.deterministic_policy()
    dp_file,mc_file=ROOT/'politicas/dp.json',ROOT/'politicas/mc.json'
    save_policy(dp_file,dp.policy,algorithm='value_iteration',gamma=.95)
    save_policy(mc_file,mc_policy,algorithm='monte_carlo_first_visit_on_policy_epsilon_greedy',gamma=.95,episodes=args.episodes,seed=42)
    export_analysis(ROOT/'politicas/analisis_v010.json.gz',dp.values,mc.q,mc.counts,dp_file,mc_file,
                    episodes=args.episodes,gamma=.95,truncated=mc.truncated_episodes)
    result={'rules_version':world.RULES_VERSION,'reachable_states':len(dp.policy),
            'nominal_states_with_terminals':world.total_nominal_states(),
            'settings':{'train_seed':42,'train_episodes':args.episodes,'gamma':.95,'epsilon':.15,
                        'evaluation_seeds':[2042,3042,4042],'evaluation_episodes_per_seed':1000,'max_steps':80},
            'training':{'complete':mc.completed_episodes,'truncated':mc.truncated_episodes,
                        'mc_states':mc.visited_states,'mc_pairs':mc.visited_pairs,
                        'dp_iterations':len(dp.deltas),'dp_last_delta':dp.deltas[-1],
                        'elapsed_seconds':perf_counter()-start},
            'policy_sha256':{n:hashlib.sha256(p.read_bytes()).hexdigest() for n,p in [('dp',dp_file),('mc',mc_file)]},
            'evaluation':{},'form_metrics':{},'boss_decisions':[]}
    for name,policy in [('dp',dp.policy),('mc',mc_policy)]:
        result['evaluation'][name]=[asdict(evaluate(world,policy,episodes=1000,seed=seed)) for seed in (2042,3042,4042)]
        result['form_metrics'][name]=[form_metrics(world,policy,seed) for seed in (2042,3042,4042)]
        print(name,result['form_metrics'][name],flush=True)
    for hp,en,foe,core in [(6,5,9,True),(6,6,9,False),(6,2,1,False)]:
        state=GameState(Zone.FORTRESS,hp,en,foe,2,True,data_core=core,xp=2)
        result['boss_decisions'].append({'hp':hp,'energy':en,'enemy_hp':foe,'core':core,
                                        'dp':dp.policy.get(state).value if state in dp.policy else None,
                                        'mc':mc_policy.get(state).value if state in mc_policy else None})
    (out/'despues_v020.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    (out/'delta_dp.csv').write_text('iteration,delta\n'+''.join(f'{i},{d:.14g}\n' for i,d in enumerate(dp.deltas,1)))
    print('Guardado:',out,flush=True)
if __name__=='__main__':main()
