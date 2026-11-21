"""Verificaciones del equilibrio evolutivo y del MDP de v0.5."""
import unittest
from digimon_rl.domain import Action, GameState, Zone, Ending
from digimon_rl.environment import DigitalWorld
from digimon_rl.policy_io import save_policy, load_policy
from pathlib import Path
from tempfile import TemporaryDirectory
import json


class TestAdvancedDigivolution(unittest.TestCase):
    def setUp(self):
        self.world = DigitalWorld()

    def test_four_stages_present(self):
        self.assertEqual(self.world.FORM_NAMES,
                         ("Agumon", "Greymon", "MetalGreymon", "WarGreymon"))
        self.assertEqual(self.world.total_nominal_states(), 725762)
        self.assertGreater(len(self.world.reachable_states()), 9493)

    def test_evolution_requires_energy_region_and_battle(self):
        world = self.world
        cases = [
            (Zone.FOREST, 0, 2, True),
            (Zone.FOREST, 1, 6, False),
            (Zone.RUINS, 1, 2, True),
            (Zone.RUINS, 2, 6, False),
            (Zone.FORTRESS, 2, 1, False),
            (Zone.FORTRESS, 2, 3, True),
            (Zone.FORTRESS, 3, 6, False),
        ]
        for zone, form, energy, expected in cases:
            with self.subTest(zone=zone, form=form, energy=energy):
                state = GameState(zone,6,energy,3,form,True)
                self.assertEqual(Action.DIGIVOLVE in world.actions(state), expected)
                self.assertEqual(world.can_digivolve(state), expected)
        cleared = GameState(Zone.FORTRESS,6,6,0,2,True)
        self.assertNotIn(Action.DIGIVOLVE,world.actions(cleared))

    def test_evolution_is_one_stage_and_energy_is_spent(self):
        for current, target, zone, cost in ((0,1,Zone.FOREST,2),
                                            (1,2,Zone.RUINS,2),
                                            (2,3,Zone.FORTRESS,2)):
            state=GameState(zone,6,6,3,current,True)
            transitions=self.world.transitions(state,Action.DIGIVOLVE)
            self.assertAlmostEqual(sum(t.probability for t in transitions), 1)
            for t in transitions:
                if isinstance(t.next_state,GameState):
                    self.assertEqual(t.next_state.evolved,target)
                    self.assertEqual(t.next_state.energy,6-cost)

    def test_attack_damage_scales_with_stage(self):
        expected=(1,2,3,5)
        for form, damage in enumerate(expected):
            state=GameState(Zone.FOREST,6,6,2,form,True)
            results=self.world.transitions(state,Action.ATTACK)
            self.assertTrue(any((isinstance(t.next_state,GameState) and
                                 t.next_state.enemy_hp == max(0,2-damage)) or
                                (isinstance(t.next_state,GameState) and
                                 t.next_state.enemy_hp==0) for t in results),
                            msg=f"Sin impactos correctos para {form}")

    def test_boss_strategy_can_use_mega_form(self):
        boss=GameState(Zone.FORTRESS,6,6,6,2,True)
        self.assertIn(Action.DIGIVOLVE, self.world.actions(boss))
        after=self.world.transitions(boss,Action.DIGIVOLVE)
        self.assertTrue(all(isinstance(t.next_state, GameState) and
                            t.next_state.form_name == 'WarGreymon' for t in after))
        self.assertEqual(GameState(Zone.FORTRESS,6,6,6,3,True).form_name,
                         "WarGreymon")

    def test_policy_format_is_versioned(self):
        state=self.world.start_state()
        with TemporaryDirectory() as td:
            f=Path(td)/"new.json"
            save_policy(f,{state:Action.ROUTE_FOREST},algorithm="test")
            self.assertEqual(load_policy(f,self.world),{state:Action.ROUTE_FOREST})
            data=json.loads(f.read_text())
            data['format_version']=1
            f.write_text(json.dumps(data))
            with self.assertRaises(ValueError):
                load_policy(f,self.world)


if __name__=='__main__':
    unittest.main()
