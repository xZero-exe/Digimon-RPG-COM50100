"""Decisiones opcionales finitas y comportamiento visible de los guardianes."""
from dataclasses import replace
import unittest
from digimon_rl.domain import Action,Ending,GameState,Zone
from digimon_rl.environment import DigitalWorld
from digimon_rl.world_map import MAP_EDGES,MAP_POSITIONS
from digimon_rl.combat_visuals import CombatAnimation
from digimon_rl.domain import Step


class OptionalRouteTests(unittest.TestCase):
    def setUp(self):self.world=DigitalWorld()
    def clear(self,zone,**kwargs):return replace(self.world.start_state(),zone=zone,**kwargs)

    def test_refuge_is_optional_and_only_after_initial_combat(self):
        for z in (Zone.FOREST,Zone.CAVE):
            self.assertIn(Action.ROUTE_REFUGE,self.world.actions(self.clear(z)))
            self.assertNotIn(Action.ROUTE_REFUGE,self.world.actions(self.clear(z,enemy_hp=2)))
        self.assertNotIn(Action.ROUTE_REFUGE,self.world.actions(self.world.start_state()))

    def test_refuge_recovers_resources_and_costs_reward_without_farming(self):
        before=self.clear(Zone.FOREST,hp=2,energy=1,potion=False)
        t,=self.world.transitions(before,Action.ROUTE_REFUGE)
        self.assertEqual(t.probability,1)
        self.assertEqual((t.next_state.zone,t.next_state.hp,t.next_state.energy,t.next_state.potion),
                         (Zone.REFUGE,4,2,True))
        self.assertLess(t.reward,0)
        self.assertNotIn(Action.ROUTE_REFUGE,self.world.actions(t.next_state))
        self.assertNotIn(Action.SCAVENGE,self.world.actions(t.next_state))
        self.assertEqual({o.next_state.zone for o in self.world.transitions(t.next_state,Action.ADVANCE) if isinstance(o.next_state,GameState)},{Zone.SWAMP})

    def test_refuge_caps_resources(self):
        t,=self.world.transitions(self.clear(Zone.CAVE,hp=6,energy=6),Action.ROUTE_REFUGE)
        self.assertEqual((t.next_state.hp,t.next_state.energy),(6,6))

    def test_new_region_ids_do_not_unlock_late_evolutions(self):
        for zone in (Zone.REFUGE,Zone.ABYSS):
            state=self.clear(zone,energy=6,evolved=2,enemy_hp=2)
            self.assertFalse(self.world.can_digivolve(state))
        self.assertTrue(self.world.can_digivolve(self.clear(Zone.ABYSS,energy=2,evolved=1,enemy_hp=6)))

    def test_abyss_can_be_skipped_from_both_sources(self):
        for z in (Zone.RUINS,Zone.TOWER):
            state=self.clear(z)
            self.assertIn(Action.ADVANCE,self.world.actions(state))
            t,=self.world.transitions(state,Action.ROUTE_ABYSS)
            self.assertEqual((t.next_state.zone,t.next_state.enemy_hp),(Zone.ABYSS,6))
            self.assertEqual((t.next_state.hp,t.next_state.energy),(state.hp,state.energy))

    def test_armor_opens_during_visible_charge(self):
        for zone,armor in [(Zone.TOWER,1),(Zone.ABYSS,2)]:
            state=self.clear(zone,enemy_hp=6)
            self.assertEqual(self.world.enemy_armor(state),armor)
            self.assertEqual(self.world.enemy_armor(replace(state,enemy_charging=True)),0)

    def test_guardian_prize_is_only_on_defeat_and_not_on_a_miss(self):
        state=self.clear(Zone.ABYSS,enemy_hp=1,evolved=2,energy=1,potion=False)
        outcomes=self.world.transitions(state,Action.ATTACK)
        killed=[t.next_state for t in outcomes if isinstance(t.next_state,GameState) and t.next_state.enemy_hp==0]
        missed=[t.next_state for t in outcomes if isinstance(t.next_state,GameState) and t.next_state.enemy_hp==1]
        self.assertTrue(killed);self.assertTrue(missed)
        self.assertTrue(all(s.data_core and s.energy==3 for s in killed))
        self.assertTrue(all(not s.data_core and s.energy==1 for s in missed))
        self.assertAlmostEqual(sum(t.probability for t in outcomes),1)

    def test_new_paths_form_a_directed_acyclic_graph(self):
        visited=set();active=set()
        def visit(z):
            self.assertNotIn(z,active,'Ciclo de curación/recompensa en el mapa')
            if z in visited:return
            active.add(z)
            for a,b in MAP_EDGES:
                if a==z:visit(b)
            active.remove(z);visited.add(z)
        visit(Zone.VILLAGE)
        self.assertEqual(visited,set(Zone))
        self.assertEqual(len(MAP_EDGES),14)
        self.assertEqual(set(MAP_POSITIONS),set(Zone))

    def test_guardian_combat_animation_uses_available_pixel_effect(self):
        before=self.clear(Zone.ABYSS,enemy_hp=6,evolved=1,energy=3,enemy_charging=True)
        t=next(t for t in self.world.transitions(before,Action.GUARD) if isinstance(t.next_state,GameState))
        seq=CombatAnimation.from_step(Step(before,Action.GUARD,t.reward,t.next_state))
        self.assertTrue(any(b.effect=='giga_destroyer' for b in seq.beats))
        self.assertTrue(any(b.title=='Destruction Grenade' for b in seq.beats))
if __name__=='__main__':unittest.main()
