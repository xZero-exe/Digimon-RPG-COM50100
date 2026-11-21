"""Auditoría del informe histórico v0.19, con Python estándar.

Valida fuentes numéricas y estructura Word; no entrena, publica ni certifica Windows.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import platform
import re
from statistics import mean,stdev
import sys
from xml.etree import ElementTree as ET
import zipfile

ROOT=Path(__file__).resolve().parents[1]
NS={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
    'm':'http://schemas.openxmlformats.org/officeDocument/2006/math'}


def audit(root: Path) -> dict:
    evidence=json.loads((root/'resultados/evidencia_informe_v019.json').read_text(encoding='utf-8'))
    for name,expected in evidence['sources'].items():
        path=(root/"politicas/historico_v019"/Path(name).name
              if name.startswith("politicas/") and (root/"politicas/historico_v019").is_dir() else root/name)
        assert path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest()==expected,('Fuente modificada',name)
    data=json.loads((root/'resultados/convergencia_v011/resumen_v011.json').read_text(encoding='utf-8'))
    settings=data['settings'];groups=data['by_checkpoint']
    assert settings['train_seeds']==[41,42,43,44,45]
    assert settings['checkpoints']==[500,2000,5000,10000,20000]
    assert settings['reachable_states']==48553 and settings['evaluation_episodes_per_seed_method_checkpoint']==200
    assert evidence['checkpoint_max']==20000 and evidence['play_policy_mc_episodes']==60000
    mapping={'mc_win_mean':'mc_win_rate','mc_win_sd':'mc_win_rate','dp_win_mean':'dp_win_rate',
             'mc_coverage_mean':'mc_state_coverage','mc_coverage_sd':'mc_state_coverage',
             'fallback_mean':'mc_fallback_action_rate','mc_return_mean':'mc_discounted_return',
             'dp_return_mean':'dp_discounted_return'}
    with (root/'resultados/convergencia_v011/curvas_resumen.csv').open(encoding='utf-8',newline='') as stream:
        rows=list(csv.DictReader(stream))
    assert len(rows)==5
    for row,group in zip(rows,groups):
        cp=int(row['checkpoint']);assert cp==group['checkpoint'] and int(row['n_seeds'])==5
        raw=[v for v in data['per_seed'] if v['checkpoint']==cp]
        assert len(raw)==5 and {v['seed'] for v in raw}==set(settings['train_seeds'])
        for column,metric in mapping.items():
            statistic='std' if column.endswith('_sd') else 'mean'
            value=stdev(v[metric] for v in raw) if statistic=='std' else mean(v[metric] for v in raw)
            assert math.isclose(float(row[column]),value,abs_tol=1e-12),(cp,column)
            assert math.isclose(group[metric][statistic],value,abs_tol=1e-12),(cp,metric)
    policies={name:json.loads(((root/'politicas/historico_v019' if (root/'politicas/historico_v019').is_dir() else root/'politicas')/f'{name}.json').read_text()) for name in ('dp','mc')}
    assert policies['dp']['rules_version']==policies['mc']['rules_version']=='v0.9-tecnicas-por-forma'
    assert policies['dp']['gamma']==policies['mc']['gamma']==.95
    assert policies['mc']['episodes']==60000 and policies['mc']['seed']==42
    assert len(policies['dp']['actions'])==48553 and len(policies['mc']['actions'])==16369
    doc=root/'docs/Informe_Final_Digimon_RPG_v019.docx'
    with zipfile.ZipFile(doc) as archive:
        tree=ET.fromstring(archive.read('word/document.xml'))
    def cell_text(cell):
        return ''.join(n.text or '' for n in cell.findall('.//w:t',NS))
    def compact(value):
        return re.sub(r'\s+','',value)
    tables=tree.findall('.//w:tbl',NS)
    curve_table=next(t for t in tables if compact(cell_text(t.findall('w:tr',NS)[0].findall('w:tc',NS)[0]))=='EpisodiosMC')
    fmt=lambda value,digits=1:f'{100*float(value):.{digits}f}'.replace('.',',')
    for word_row,row in zip(curve_table.findall('w:tr',NS)[1:],rows):
        actual=[compact(cell_text(c)) for c in word_row.findall('w:tc',NS)]
        expected=[f"{int(row['checkpoint']):,}".replace(',','.'),
                  fmt(row['mc_win_mean'])+'±'+fmt(row['mc_win_sd'])+'%',
                  fmt(row['dp_win_mean'])+'%',fmt(row['mc_coverage_mean'])+'%',
                  fmt(row['fallback_mean'],2)+'%']
        assert actual==expected,('Tabla de curvas del informe',actual,expected)
    assert len(curve_table.findall('w:tr',NS))==6
    policy_table=next(t for t in tables if cell_text(t.findall('w:tr',NS)[0].findall('w:tc',NS)[0])=='Política guardada')
    historical=json.loads((root/'resultados/validacion_v0_9.json').read_text())
    for word_row,key,label in zip(policy_table.findall('w:tr',NS)[1:],('dp','mc'),('Value Iteration','Monte Carlo')):
        value=historical[key]
        actual=[compact(cell_text(c)) for c in word_row.findall('w:tc',NS)]
        expected=[compact(label),f"{value['trained_policy_states']:,}".replace(',','.'),
                  f"{value['wins']}/500({value['win_rate']:.1%})".replace('.',','),
                  f"{value['mean_discounted_return']:.2f}".replace('.',',')]
        assert actual==expected,('Tabla de políticas guardadas',actual,expected)
    paragraphs=tree.findall('.//w:body/w:p',NS)
    # Utiliza nodos de texto para no confundir fórmulas ni propiedades OOXML.
    text=[''.join(n.text or '' for n in p.findall('.//w:t',NS)) for p in paragraphs]
    headings={''.join(n.text or '' for n in p.findall('.//w:t',NS))
              for p in paragraphs if p.find('.//w:pStyle',NS) is not None
              and p.find('.//w:pStyle',NS).get('{'+NS['w']+'}val','').startswith('Heading')}
    required={'Índice','Resumen','Estado del arte','Metodología','Resultados','Discusión','Conclusión','Referencias'}
    assert required<=headings,('Secciones faltantes',required-headings)
    assert any(p.find('.//w:pStyle',NS) is not None
               and p.find('.//w:pStyle',NS).get('{'+NS['w']+'}val')=='Title' for p in paragraphs)
    assert len(tree.findall('.//m:oMath',NS))>=3,'Faltan ecuaciones editables'
    assert len(tree.findall('.//w:drawing',NS))>=2,'Faltan figuras'
    flat='\n'.join(text)
    assert '0.19' in flat and '161 pruebas' in flat
    assert '20.000' in flat and '60.000' in flat
    for phrase in ('Lorem ipsum','TODO','INSERTAR AQUÍ'):
        assert phrase not in flat
    assert evidence['windows_native']=='pending' and evidence['repository_public_url'] is None
    return {'status':'PASS','report_scope':'historical_v019','platform':platform.platform(),
        'checks':['source_hashes','five_seeds_and_checkpoints','csv_json_raw_statistics_match','word_result_tables_match_sources',
                  'saved_policy_metadata','nine_required_report_parts','editable_equations',
                  'two_figures','two_experimental_protocols_distinguished'],
        'learning_data_changed':False,'training_performed':False,
        'pending':['Registro nativo y aceptación visual/sonora en Windows',
                   'URL del repositorio público y revisión de recursos según el aviso existente',
                   'Ensayo de exposición y revisión final del autor']}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'resultados/verificacion_entrega_v019.json')
    args=parser.parse_args()
    try:
        result=audit(ROOT)
    except Exception as exc:
        result={'status':'FAIL','error':repr(exc)}
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
        print(json.dumps(result,ensure_ascii=False,indent=2));sys.exit(1)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
