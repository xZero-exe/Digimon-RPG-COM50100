"""Regresión de encuadre, carga de recursos y composición en SDL real."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(importlib.util.find_spec('pygame'), 'Requiere Pygame')
class BackgroundIntegrationTests(unittest.TestCase):
    def test_all_scenes_aspect_fallback_cache_and_game_state(self):
        with tempfile.TemporaryDirectory() as temp:
            run = subprocess.run([sys.executable, str(ROOT/'scripts/validar_fondos_v015.py'),
                                  '--headless', '--output', temp], cwd=ROOT,
                                 capture_output=True, text=True, timeout=60)
            self.assertEqual(run.returncode, 0, run.stdout+run.stderr)
            report = json.loads((Path(temp)/'validacion.json').read_text(encoding='utf-8'))
            self.assertEqual(report['status'], 'PASS')
            self.assertEqual(len(report['backgrounds']), 9)
            self.assertEqual(len(report['screenshots']), 43)
            self.assertIn('cover_preserves_aspect', report['checks'])
            self.assertIn('render_preserves_state_and_rng', report['checks'])
