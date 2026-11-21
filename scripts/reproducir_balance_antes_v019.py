"""Reproduce la evaluación histórica usando su motor y políticas archivados.

No modifica el juego actual ni entrena. 3 semillas x 1000 partidas por método.
"""
from pathlib import Path
from collections import Counter
from random import Random
import argparse
import json
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'referencia_v019'))
from digimon_rl.environment import DigitalWorld
from digimon_rl.policy_io import load_policy
from digimon_rl.domain import Zone


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'resultados/balance_v020/antes_v019_reproducido.json')
    args=parser.parse_args();world=DigitalWorld();result={}
    for name in ('dp','mc'):
        policy=load_policy(ROOT/f'politicas/historico_v019/{name}.json',world);rows=[]
        for seed in (2042,3042,4042):
            rng=Random(seed);forms=Counter();boss=war=fallback=0
            for _ in range(1000):
                def choose(state,legal,_rng):
                    nonlocal fallback
                    if state not in policy:fallback+=1
                    return policy.get(state,legal[0])
                run=world.episode(choose,rng)
                boss+=any(s.state.zone==Zone.FORTRESS for s in run.steps)
                war+=any(s.state.evolved==3 for s in run.steps)
                if run.won:forms[run.steps[-1].state.form_name]+=1
            rows.append({'seed':seed,'episodes':1000,'wins':sum(forms.values()),'boss_reached':boss,
                         'used_wargreymon':war,'winning_form':dict(forms),'fallback_actions':fallback})
        result[name]=rows
    expected=json.loads((ROOT/'resultados/balance_v020/antes_v019.json').read_text())
    assert result==expected,'La reproducción difiere del registro histórico'
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2))
    print('PASS: las seis evaluaciones coinciden exactamente con la referencia v0.19')
if __name__=='__main__':main()
