"""Valida el balance y sus resultados sin reentrenar ni certificar Windows."""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import platform
from statistics import mean,stdev
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'referencia_v020'))
from digimon_rl.domain import Action,Ending,GameState,Zone
from digimon_rl.environment import DigitalWorld
from digimon_rl.inspector import PolicyInspector
from digimon_rl.policy_io import load_policy


def audit():
    world=DigitalWorld();directory=ROOT/'resultados/balance_v020'
    data=json.loads((directory/'despues_v020.json').read_text())
    for name,digest in json.loads((directory/'fuentes_sha256.json').read_text()).items():
        assert hashlib.sha256((ROOT/'referencia_v020'/Path(name).relative_to('src') if name.startswith('src/') else ROOT/'politicas/historico_v020'/Path(name).name).read_bytes()).hexdigest()==digest,('Fuente modificada',name)
    assert data['rules_version']==world.RULES_VERSION
    dp_file,mc_file=ROOT/'politicas/historico_v020/dp.json',ROOT/'politicas/historico_v020/mc.json'
    policies={'dp':load_policy(dp_file,world),'mc':load_policy(mc_file,world)}
    for key,file in [('dp',dp_file),('mc',mc_file)]:
        assert hashlib.sha256(file.read_bytes()).hexdigest()==data['policy_sha256'][key]
    assert len(policies['dp'])==data['reachable_states']==60649
    assert world.total_nominal_states()==data['nominal_states_with_terminals']==564482
    assert data['training']['complete']+data['training']['truncated']==data['settings']['train_episodes']
    assert len(policies['mc'])==data['training']['mc_states']
    assert data['training']['dp_last_delta']<1e-8
    inspector=PolicyInspector.from_export(world,policies['dp'],policies['mc'],ROOT/'politicas/historico_v020/analisis_v010.json.gz',dp_file,mc_file)
    assert inspector.episodes==data['settings']['train_episodes']
    try:load_policy(ROOT/'politicas/historico_v019/dp.json',world)
    except ValueError as error:assert 'Reglas del MDP incompatibles' in str(error)
    else:raise AssertionError('Se aceptó una política antigua')
    for name in ('dp','mc'):
        for row,evaluation in zip(data['form_metrics'][name],data['evaluation'][name]):
            assert row['episodes']==row['wins']+row['losses']+row['truncated']==1000
            assert row['wins']==sum(row['winning_form'].values())==evaluation['wins']
            assert row['used_wargreymon']<=row['boss_reached']<=row['episodes']
            assert evaluation['fallback_actions']==row['fallback_actions']
    state=GameState(Zone.FORTRESS,6,5,9,2,True,data_core=True,xp=2)
    assert policies['dp'][state]==Action.DIGIVOLVE
    assert not any(t.next_state==Ending.WIN for t in world.transitions(state,Action.TECHNIQUE))
    wounded=GameState(Zone.FORTRESS,6,2,1,2,True,data_core=False,xp=2)
    assert policies['dp'][wounded]!=Action.DIGIVOLVE
    curves=ROOT/'resultados/convergencia_v020'
    summary=json.loads((curves/'resumen_v020.json').read_text())
    assert summary['rules_version']==world.RULES_VERSION and summary['release']=='0.20'
    assert summary['settings']['reachable_states']==len(policies['dp'])
    assert summary['settings']['train_seeds']==[41,42,43,44,45]
    columns={'mc_win_mean':'mc_win_rate','mc_win_sd':'mc_win_rate','dp_win_mean':'dp_win_rate',
             'mc_coverage_mean':'mc_state_coverage','mc_coverage_sd':'mc_state_coverage',
             'fallback_mean':'mc_fallback_action_rate','mc_return_mean':'mc_discounted_return',
             'dp_return_mean':'dp_discounted_return'}
    with (curves/'curvas_resumen.csv').open(newline='') as f:rows=list(csv.DictReader(f))
    assert len(rows)==5
    for row,group in zip(rows,summary['by_checkpoint']):
        assert int(row['checkpoint'])==group['checkpoint']
        raw=[r for r in summary['per_seed'] if r['checkpoint']==group['checkpoint']]
        assert len(raw)==int(row['n_seeds'])==5
        for column,key in columns.items():
            statistic='std' if column.endswith('_sd') else 'mean'
            expected=stdev(r[key] for r in raw) if statistic=='std' else mean(r[key] for r in raw)
            assert math.isclose(float(row[column]),expected,abs_tol=1e-12)
            assert math.isclose(group[key][statistic],expected,abs_tol=1e-12)
    return {'status':'PASS','historical_scope':'v0.20','rules_version':world.RULES_VERSION,'platform':platform.platform(),
            'reachable_states':len(policies['dp']),'checks':['model_source_hashes','policy_hashes','new_rules_reject_old_policies',
            'inspector_matches_policies','full_boss_survives_giga','evolution_use_is_not_forced',
            'evaluation_forms_match_wins','new_curves_match_raw_seeds'],
            'native_windows_acceptance':'pending'}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,default=ROOT/'resultados/balance_v020/verificacion.json')
    args=p.parse_args();result=audit();args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2))
    print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
