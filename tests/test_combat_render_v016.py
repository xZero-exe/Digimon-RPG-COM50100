"""Comprueba controles y composición del feedback con un proceso SDL aislado."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(importlib.util.find_spec('pygame'),'Requiere Pygame')
class CombatFeedbackRenderTests(unittest.TestCase):
    def test_feedback_controls_and_cases_in_real_sdl(self):
        with tempfile.TemporaryDirectory() as temp:
            run = subprocess.run([sys.executable,str(ROOT/'scripts/validar_combate_v016.py'),
                                  '--headless','--output',temp],cwd=ROOT,capture_output=True,text=True,timeout=60)
            self.assertEqual(run.returncode,0,run.stdout+run.stderr)
            report = json.loads((Path(temp)/'validacion.json').read_text(encoding='utf-8'))
            self.assertEqual(report['status'],'PASS')
            cases = {row['case']:row for row in report['cases']}
            self.assertIn('+3 PS',cases['pocion']['notices'])
            self.assertIn('-3 PS',cases['pocion']['notices'])
            self.assertIn('CANCELADO',cases['interrupcion']['notices'])
            self.assertIn('FALLÓ',cases['interrupcion_fallida']['notices'])
            self.assertIn('SIN DAÑO',cases['armadura']['notices'])
            self.assertIn('instant_mode_resolves_exactly_one_identical_turn',report['checks'])
            self.assertIn('pause_freezes_animation',report['checks'])
