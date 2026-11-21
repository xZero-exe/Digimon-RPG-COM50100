"""Pruebas para XP, mejora RPG y la propiedad de Markov."""
import unittest
from tempfile import TemporaryDirectory
from pathlib import Path
from digimon_rl.domain import Action, GameState, Zone, Ending
from digimon_rl.environment import DigitalWorld
from digimon_rl.policy_io import load_policy, save_policy

class TestProgression(unittest.TestCase):
    def setUp(self): self.world=DigitalWorld()

    def test_start_without_xp(self):
        s=self.world.start_state()
        self.assertEqual(s.xp,0)
        self.assertFalse(s.trained)
        self.assertNotIn(Action.TRAIN,self.world.actions(s))

    def test_xp_reward_on_victory_and_cap(self):
        for xp in (0,1,2):
            s=GameState(Zone.FOREST,6,6,1,3,True,xp=xp)
            outcomes=self.world.transitions(s,Action.ATTACK)
            for t in outcomes:
                if isinstance(t.next_state,GameState) and t.next_state.enemy_hp==0:
                    self.assertEqual(t.next_state.xp,min(2,xp+1))

    def test_training_is_optional_costs_resources_and_buffs(self):
        s=GameState(Zone.SWAMP,5,3,0,1,True,xp=2)
        self.assertIn(Action.ADVANCE,self.world.actions(s))
        self.assertIn(Action.TRAIN,self.world.actions(s))
        out=self.world.transitions(s,Action.TRAIN)
        self.assertEqual(len(out),1)
        self.assertEqual(out[0].probability,1)
        trained=out[0].next_state
        self.assertTrue(trained.trained)
        self.assertEqual(trained.xp,0)
        self.assertEqual(trained.energy,2)
        self.assertEqual(trained.hp,5)
        self.assertEqual(trained.zone,Zone.SWAMP)
        self.assertNotIn(Action.TRAIN,self.world.actions(trained))
        self.assertEqual(out[0].reward,-3)

    def test_training_needs_energy(self):
        s=GameState(Zone.SWAMP,5,0,0,1,True,xp=2)
        self.assertNotIn(Action.TRAIN,self.world.actions(s))
        with self.assertRaises(ValueError):self.world.transitions(s,Action.TRAIN)

    def test_buff_increases_damage_not_fake_reward(self):
        untrained=GameState(Zone.SWAMP,6,6,3,0,True)
        trained=GameState(Zone.SWAMP,6,6,3,0,True,trained=True)
        def maximum_hit(state):
            results=self.world.transitions(state,Action.ATTACK)
            return max(state.enemy_hp-t.next_state.enemy_hp for t in results if isinstance(t.next_state,GameState))
        self.assertEqual(maximum_hit(trained)-maximum_hit(untrained),1)

    def test_progression_persists_during_exploration(self):
        s=GameState(Zone.SWAMP,6,3,0,1,True,xp=1,trained=True)
        for t in self.world.transitions(s,Action.ADVANCE):
            if isinstance(t.next_state,GameState):
                self.assertEqual(t.next_state.xp,1)
                self.assertTrue(t.next_state.trained)

    def test_policy_version_round_trip_with_experience(self):
        s=GameState(Zone.SWAMP,6,3,0,1,True,xp=2)
        with TemporaryDirectory() as root:
            p=Path(root)/'policy.json'
            save_policy(p,{s:Action.TRAIN},algorithm='test')
            self.assertEqual(load_policy(p,self.world),{s:Action.TRAIN})

    def test_invalid_xp_and_old_policy_rejected(self):
        import json
        s=GameState(Zone.SWAMP,6,3,0,1,True,xp=2)
        with TemporaryDirectory() as root:
            p=Path(root)/'policy.json'
            save_policy(p,{s:Action.TRAIN},algorithm='test')
            data=json.loads(p.read_text())
            data['actions'][0][0][-2]=50
            p.write_text(json.dumps(data))
            with self.assertRaises(ValueError):load_policy(p,self.world)
            data['actions'][0][0][-2]=2;data['format_version']=4
            p.write_text(json.dumps(data))
            with self.assertRaises(ValueError):load_policy(p,self.world)

if __name__=='__main__': unittest.main()
