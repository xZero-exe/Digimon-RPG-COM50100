"""Prueba de integración aislada para no heredar los dobles pygame de otros tests."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(importlib.util.find_spec('pygame'), 'Requiere el extra game de Pygame')
class SDLIntegrationTests(unittest.TestCase):
    def test_real_render_navigation_and_clicks(self):
        with tempfile.TemporaryDirectory() as temp:
            result = subprocess.run([sys.executable, str(ROOT/'scripts/validar_interfaz_v013.py'),
                                     '--headless', '--output', temp],
                                    cwd=ROOT, capture_output=True, text=True, timeout=60)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            report = json.loads((Path(temp)/'validacion.json').read_text(encoding='utf-8'))
            self.assertEqual(report['status'], 'PASS')
            self.assertGreaterEqual(len(report['checks']), 7)
            self.assertEqual({row['mode'] for row in report['episodes']}, {'dp','mc'})
            for file in report['screenshots']:
                self.assertGreater((Path(temp)/file).stat().st_size, 1000)
