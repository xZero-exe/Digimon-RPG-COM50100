"""Integración de mixer real, controles y recuperación sin dispositivo de sonido."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]


@unittest.skipUnless(importlib.util.find_spec('pygame'),'Requiere Pygame')
class AudioRenderTests(unittest.TestCase):
    def test_real_audio_pipeline_and_device_failure(self):
        with tempfile.TemporaryDirectory() as temp:
            for suffix,options in (('normal',[]),('sin_dispositivo',['--no-audio'])):
                output=Path(temp)/suffix
                run=subprocess.run([sys.executable,str(ROOT/'scripts/validar_audio_v018.py'),
                    '--headless','--output',str(output),*options],cwd=ROOT,
                    capture_output=True,text=True,timeout=90)
                self.assertEqual(run.returncode,0,run.stdout+run.stderr)
                report=json.loads((output/'validacion.json').read_text(encoding='utf-8'))
                self.assertEqual(report['status'],'PASS')
                if options:
                    self.assertFalse(report['audio_available'])
                    self.assertIn('device_failure_is_non_fatal',report['checks'])
                else:
                    self.assertTrue(report['audio_available'])
                    self.assertIn('unmute_does_not_replay_consumed_cues',report['checks'])
                    self.assertIn('pause_freezes_clock_and_audio',report['checks'])
