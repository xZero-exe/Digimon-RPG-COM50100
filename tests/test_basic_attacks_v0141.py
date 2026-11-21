"""Evita que un ataque legal vuelva a quedar sin atlas de animación."""
from dataclasses import replace
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from digimon_rl.combat_visuals import CombatAnimation, ALL_EFFECTS
from digimon_rl.domain import Action, GameState, Step, Zone
from digimon_rl.environment import DigitalWorld

ROOT=Path(__file__).resolve().parents[1]


class OffensiveCoverageTests(unittest.TestCase):
    def test_every_offensive_action_uses_png_for_all_forms(self):
        for form in range(4):
            state=GameState(Zone.FOREST,6,6,2,form,True,True)
            after=replace(state,enemy_hp=1,hp=5)
            for action in (Action.ATTACK,Action.POWER_ATTACK,Action.TECHNIQUE,Action.INTERRUPT):
                self.assertIn(action,DigitalWorld().actions(state))
                beat=CombatAnimation.from_step(Step(state,action,0,after)).beats[0]
                self.assertIn(beat.effect,ALL_EFFECTS)
                self.assertTrue((ROOT/'assets/effects'/f'{beat.effect}.png').is_file())

    def test_basic_actions_are_visually_distinct_from_named_techniques(self):
        state=GameState(Zone.FOREST,6,6,2,0,True,True)
        after=replace(state,enemy_hp=1)
        effects=[CombatAnimation.from_step(Step(state,a,0,after)).beats[0].effect
                 for a in (Action.ATTACK,Action.POWER_ATTACK,Action.TECHNIQUE,Action.INTERRUPT)]
        self.assertEqual(len(set(effects)),4)


@unittest.skipUnless(importlib.util.find_spec('pygame'),'Requiere Pygame')
class BasicRenderTests(unittest.TestCase):
    def test_real_frames_all_forms_and_full_gallery(self):
        with tempfile.TemporaryDirectory() as temp:
            run=subprocess.run([sys.executable,str(ROOT/'scripts/validar_basicos_v0141.py'),
                                '--headless','--output',temp],cwd=ROOT,
                               capture_output=True,text=True,timeout=60)
            self.assertEqual(run.returncode,0,run.stdout+run.stderr)
            report=json.loads((Path(temp)/'validacion.json').read_text(encoding='utf-8'))
            self.assertEqual(report['status'],'PASS')
            self.assertEqual(len(report['cases']),12)
            self.assertEqual(len(report['screenshots']),61)
