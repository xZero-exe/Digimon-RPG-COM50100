"""Carga y reproducción real SDL en subproceso, separada de los dobles de GUI."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]


@unittest.skipUnless(importlib.util.find_spec('pygame'),'Requiere Pygame')
class EffectRenderTests(unittest.TestCase):
    def test_all_assets_and_real_input_integration(self):
        with tempfile.TemporaryDirectory() as temp:
            run=subprocess.run([sys.executable,str(ROOT/'scripts/validar_efectos_v014.py'),
                                '--headless','--output',temp],cwd=ROOT,
                               capture_output=True,text=True,timeout=60)
            self.assertEqual(run.returncode,0,run.stdout+run.stderr)
            data=json.loads((Path(temp)/'validacion.json').read_text(encoding='utf-8'))
            self.assertEqual(data['status'],'PASS')
            self.assertEqual(len(data['screenshots']),50)
