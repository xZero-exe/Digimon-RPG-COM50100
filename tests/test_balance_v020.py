"""Regresiones del balance: incentivo real, sin bloquear formas menores."""
from dataclasses import replace
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from digimon_rl.domain import Action,Ending,GameState,Zone
from digimon_rl.environment import DigitalWorld
from digimon_rl.policy_io import load_policy,save_policy


class BossBalanceTests(unittest.TestCase):
    def setUp(self):
        self.world=DigitalWorld()
        self.boss=GameState(Zone.FORTRESS,6,6,9,2,True,data_core=True)

    def test_final_boss_has_more_endurance_than_other_enemies(self):
        self.assertEqual(self.world.ENEMY_HP[Zone.FORTRESS],9)
        self.assertTrue(all(hp<9 for z,hp in self.world.ENEMY_HP.items() if z!=Zone.FORTRESS))

    def test_full_boss_survives_metalgreymon_even_with_core_and_training(self):
        for trained in (False,True):
            state=replace(self.boss,trained=trained)
            outcomes=self.world.transitions(state,Action.TECHNIQUE)
            self.assertFalse(any(t.next_state==Ending.WIN for t in outcomes))
            self.assertTrue(any(isinstance(t.next_state,GameState) and t.next_state.enemy_hp<9 for t in outcomes))

    def test_wargreymon_can_finish_full_boss_with_core_but_can_miss(self):
        state=replace(self.boss,evolved=3,energy=3)
        results=self.world.transitions(state,Action.TECHNIQUE)
        self.assertAlmostEqual(sum(t.probability for t in results if t.next_state==Ending.WIN),.85)
        self.assertTrue(any(isinstance(t.next_state,GameState) and t.next_state.enemy_hp==9 for t in results))

    def test_without_core_terra_force_does_not_always_finish_full_boss(self):
        results=self.world.transitions(replace(self.boss,evolved=3,data_core=False),Action.TECHNIQUE)
        self.assertFalse(any(t.next_state==Ending.WIN for t in results))

    def test_wargreymon_evolution_requires_and_spends_two_energy(self):
        self.assertNotIn(Action.DIGIVOLVE,self.world.actions(replace(self.boss,energy=1)))
        state=replace(self.boss,energy=2)
        for t in self.world.transitions(state,Action.DIGIVOLVE):
            self.assertIsInstance(t.next_state,GameState)
            self.assertEqual(t.next_state.evolved,3)
            self.assertEqual(t.next_state.energy,0)
            self.assertEqual(t.next_state.enemy_hp,state.enemy_hp)
            self.assertGreater(t.next_state.hp,0)

    def test_wargreymon_reduces_more_damage_but_is_not_invulnerable(self):
        for charged,expected in [(False,{2:2,3:1}),(True,{2:4,3:3})]:
            for form in (2,3):
                state=replace(self.boss,evolved=form,enemy_charging=charged)
                after=[t.next_state for t in self.world.transitions(state,Action.POWER_ATTACK)
                       if isinstance(t.next_state,GameState) and t.next_state.enemy_hp==9 and t.next_state.hp<6]
                self.assertTrue(after)
                self.assertEqual({6-s.hp for s in after},{expected[form]})

    def test_wounded_boss_still_can_be_defeated_without_final_evolution(self):
        state=replace(self.boss,enemy_hp=1,energy=0,data_core=False)
        self.assertIn(Action.ATTACK,self.world.actions(state))
        self.assertTrue(any(t.next_state==Ending.WIN for t in self.world.transitions(state,Action.ATTACK)))

    def test_old_rules_are_rejected_even_if_state_format_matches(self):
        with TemporaryDirectory() as folder:
            p=Path(folder)/'old.json'
            save_policy(p,{self.world.start_state():Action.ROUTE_FOREST},algorithm='test')
            value=json.loads(p.read_text());value['rules_version']='v0.9-tecnicas-por-forma'
            p.write_text(json.dumps(value))
            with self.assertRaisesRegex(ValueError,'Reglas del MDP incompatibles'):load_policy(p,self.world)

if __name__=='__main__':unittest.main()
