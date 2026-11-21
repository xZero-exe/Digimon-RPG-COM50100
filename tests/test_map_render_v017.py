"""Regresión SDL del mapa: rutas, progreso, clics y ausencia del recurso gráfico."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]


@unittest.skipUnless(importlib.util.find_spec('pygame'),'Requiere Pygame')
class WorldMapRenderTests(unittest.TestCase):
    def test_real_map_input_and_progress(self):
        with tempfile.TemporaryDirectory() as temp:
            run=subprocess.run([sys.executable,str(ROOT/'scripts/validar_mapa_v017.py'),
                                '--headless','--output',temp],cwd=ROOT,capture_output=True,text=True,timeout=60)
            self.assertEqual(run.returncode,0,run.stdout+run.stderr)
            report=json.loads((Path(temp)/'validacion.json').read_text(encoding='utf-8'))
            self.assertEqual(report['status'],'PASS')
            self.assertEqual(len(report['routes']),14)
            self.assertIn('stale_double_click_ignored',report['checks'])
            self.assertIn('four_resolutions_and_route_clicks',report['checks'])
            self.assertIn('fallback_remains_playable',report['checks'])
