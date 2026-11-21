"""Verifica la continuidad de v0.21.1 y los cambios documentales de publicación."""
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
METADATA_PATHS={'assets/DIGIDEX_MANIFEST.json','assets/PLANTILLA_CREDITOS.md','assets/digimon/LEEME.txt'}

def main():
    data=json.loads((ROOT/'resultados/diario_v022/continuidad_v0211.json').read_text(encoding='utf-8'))
    publication=ROOT/'resultados/publicacion_v022/cambios_documentales.json'
    changes=json.loads(publication.read_text(encoding='utf-8'))['approved_metadata_changes'] if publication.exists() else []
    approved={row['path']:row for row in changes}
    if set(approved)-METADATA_PATHS:
        raise SystemExit('El registro de publicación contiene cambios fuera de las fichas documentales.')
    failures=[];accepted=[];unchanged=0
    for row in data['files']:
        path=ROOT/row['path']
        digest=hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None
        if digest==row['sha256']:
            unchanged+=1
        elif row['path'] in approved and approved[row['path']]['baseline_sha256']==row['sha256'] and approved[row['path']]['publication_sha256']==digest:
            accepted.append(row['path'])
        else:
            failures.append(row['path'])
    result={'status':'FAIL' if failures else 'PASS','files_checked':len(data['files']),
            'baseline':data['baseline'],'rules_version':data['rules_version'],
            'byte_identical':unchanged,'documented_credit_metadata_changes':accepted,'differences':failures}
    print(json.dumps(result,ensure_ascii=False,indent=2))
    if failures:raise SystemExit(1)
if __name__=='__main__':main()
