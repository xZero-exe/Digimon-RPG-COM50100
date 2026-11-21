"""Topología y progreso proyectados desde las reglas del MDP existente."""
from dataclasses import replace
import unittest
from digimon_rl.domain import Action, GameState, Zone
from digimon_rl.environment import DigitalWorld
from digimon_rl.world_map import MAP_EDGES, MAP_POSITIONS, MAP_ROUTES, WorldMapView


class WorldMapTests(unittest.TestCase):
    def setUp(self):
        self.world = DigitalWorld()

    def view(self,state,history=(),visited=(),choose=True):
        return WorldMapView.build(state,history,visited,self.world.actions(state),can_choose=choose)

    def test_drawn_connections_match_actual_exploration_destinations(self):
        actual = set()
        for zone in Zone:
            state = replace(self.world.start_state(),zone=zone)
            for action in self.world.actions(state):
                for transition in self.world.transitions(state,action):
                    if isinstance(transition.next_state,GameState):
                        actual.add((zone,transition.next_state.zone))
            for destination in self.view(state).destinations:
                self.assertIn(destination.action,self.world.actions(state))
                self.assertEqual({t.next_state.zone for t in self.world.transitions(state,destination.action)},
                                 {destination.zone})
        self.assertEqual(actual,MAP_EDGES)
        self.assertEqual(len(MAP_ROUTES),14)
        self.assertEqual(set(MAP_POSITIONS),set(Zone))

    def test_combat_has_no_clickable_destination_in_any_region_or_form(self):
        for zone in tuple(Zone)[1:]:
            for form in range(4):
                state = GameState(zone,6,6,2,form,True,True)
                self.assertEqual(self.view(state).destinations,())

    def test_initial_and_swamp_branching_keep_the_existing_actions(self):
        start = self.view(self.world.start_state())
        self.assertEqual({d.action for d in start.destinations},{Action.ROUTE_FOREST,Action.ROUTE_CAVE})
        swamp = self.view(replace(self.world.start_state(),zone=Zone.SWAMP))
        self.assertEqual({d.zone:d.action for d in swamp.destinations},
                         {Zone.RUINS:Action.ADVANCE,Zone.TOWER:Action.ROUTE_TOWER})
        self.assertNotIn(Action.SCAVENGE,{d.action for d in swamp.destinations})

    def test_traveled_routes_come_from_ordered_history_not_visited_membership(self):
        start = self.world.start_state()
        forest = replace(start,zone=Zone.FOREST,enemy_hp=2)
        cleared = replace(forest,enemy_hp=0)
        swamp = replace(start,zone=Zone.SWAMP,enemy_hp=3)
        view = self.view(swamp,(start,forest,cleared,swamp),set(Zone))
        self.assertEqual(view.traveled,frozenset({(Zone.VILLAGE,Zone.FOREST),(Zone.FOREST,Zone.SWAMP)}))
        self.assertIn(Zone.FOREST,view.cleared)
        self.assertNotIn(Zone.SWAMP,view.cleared)
        self.assertNotIn((Zone.VILLAGE,Zone.CAVE),view.traveled)

    def test_read_only_view_distinguishes_possible_routes_without_enabling_input(self):
        state = self.world.start_state()
        view = self.view(state,choose=False)
        self.assertFalse(view.can_choose)
        self.assertEqual(view.status(Zone.FOREST),'RUTA POSIBLE')
        self.assertEqual(view.status(Zone.FORTRESS),'SIN VISITAR')
        self.assertEqual(view.status(Zone.VILLAGE),'ACTUAL')

    def test_fortress_has_no_new_outgoing_destination(self):
        state = replace(self.world.start_state(),zone=Zone.FORTRESS)
        self.assertIn(Action.ADVANCE,self.world.actions(state))
        self.assertEqual(self.view(state).destinations,())
