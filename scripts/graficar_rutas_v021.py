"""Figura científica desde las curvas guardadas (matplotlib opcional)."""
from pathlib import Path
import json
from generar_informe_v019 import create_chart
ROOT=Path(__file__).resolve().parents[1]
if __name__=='__main__':
    out=ROOT/'docs/figuras_v021';out.mkdir(exist_ok=True,parents=True)
    create_chart(json.loads((ROOT/'resultados/convergencia_v021/resumen_v021.json').read_text()),out/'aprendizaje_v021.png')
