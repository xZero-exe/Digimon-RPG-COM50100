"""Pruebas de la ruta alternativa y del núcleo de datos como estado Markoviano."""
import unittest
from tempfile import TemporaryDirectory
from pathlib import Path
from digimon_rl.domain import GameState, Action, Zone, Ending
from digimon_rl.environment import DigitalWorld
from digimon_rl.policy_io import save_policy,load_policy

class TestV07Exploration(unittest.TestCase):
    def setUp(self):
        self.world = DigitalWorld()

    def test_swamp_branches(self):
        current = GameState(Zone.SWAMP, 6, 4, 0, 1, True)
        self.assertIn(Action.ROUTE_TOWER,self.world.actions(current))
        safe = self.world.transitions(current,Action.ADVANCE)
        risky = self.world.transitions(current,Action.ROUTE_TOWER)
        self.assertTrue(any(isinstance(x.next_state,GameState) and x.next_state.zone==Zone.RUINS for x in safe))
        self.assertTrue(any(isinstance(x.next_state,GameState) and x.next_state.zone==Zone.TOWER for x in risky))
        self.assertAlmostEqual(sum(t.probability for t in risky),1)

    def test_data_core_can_be_found_by_exploration(self):
        current=GameState(Zone.SWAMP,6,4,0,1,True)
        outcomes=self.world.transitions(current,Action.SCAVENGE)
        self.assertTrue(any(isinstance(t.next_state,GameState) and t.next_state.data_core for t in outcomes))
        self.assertTrue(any(isinstance(t.next_state,GameState) and not t.next_state.data_core for t in outcomes))

    def test_data_core_improves_damage_on_piedmon(self):
        normal=GameState(Zone.FORTRESS,6,6,6,1,True,False,False)
        enhanced=GameState(Zone.FORTRESS,6,6,6,1,True,False,True)
        def max_inflicted(s):
            transitions=self.world.transitions(s,Action.ATTACK)
            return max((s.enemy_hp-t.next_state.enemy_hp) for t in transitions if isinstance(t.next_state,GameState))
        self.assertGreater(max_inflicted(enhanced),max_inflicted(normal))

    def test_core_survives_combat_and_zone_changes(self):
        combat=GameState(Zone.TOWER,6,4,5,2,True,False,True)
        for t in self.world.transitions(combat,Action.GUARD):
            if isinstance(t.next_state,GameState): self.assertTrue(t.next_state.data_core)
        cleared=GameState(Zone.TOWER,6,4,0,2,True,False,True)
        for t in self.world.transitions(cleared,Action.ADVANCE):
            if isinstance(t.next_state,GameState): self.assertTrue(t.next_state.data_core)

    def test_versioned_policy_round_trip_data_core(self):
        current=GameState(Zone.SWAMP,6,4,0,1,True,False,True)
        with TemporaryDirectory() as td:
            p=Path(td)/'policy.json'
            save_policy(p,{current:Action.ROUTE_TOWER},algorithm='test')
            self.assertEqual(load_policy(p,self.world),{current:Action.ROUTE_TOWER})

    def test_old_policy_rejected(self):
        import json
        current=self.world.start_state()
        with TemporaryDirectory() as td:
            p=Path(td)/'policy.json'
            save_policy(p,{current:Action.ROUTE_FOREST},algorithm='test')
            data=json.loads(p.read_text());data['format_version']=3;p.write_text(json.dumps(data))
            with self.assertRaises(ValueError):load_policy(p,self.world)

if __name__=='__main__':unittest.main()
