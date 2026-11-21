"""Regresiones de presentación: la animación interpreta un Step sin resolverlo otra vez."""
from dataclasses import replace
import unittest
from digimon_rl.combat_visuals import CombatAnimation, ALL_EFFECTS, ENEMY_EFFECTS
from digimon_rl.domain import Action, Ending, GameState, Step, Zone


class CombatVisualTests(unittest.TestCase):
    def setUp(self):
        self.state = GameState(Zone.FORTRESS, 6, 6, 6, 2, True, True)

    def sequence(self, action, after, state=None):
        return CombatAnimation.from_step(Step(state or self.state, action, 0, after))

    def test_thirteen_distinct_assets(self):
        self.assertEqual(len(ALL_EFFECTS), 13)
        self.assertEqual(len(set(ALL_EFFECTS)), 13)
        self.assertEqual(set(ENEMY_EFFECTS), set(Zone)-{Zone.VILLAGE,Zone.REFUGE})

    def test_technique_matches_form_before_transition(self):
        for level, effect in enumerate(ALL_EFFECTS[:4]):
            s = replace(self.state, evolved=level, enemy_charging=False)
            seq = self.sequence(Action.TECHNIQUE, replace(s,enemy_hp=2),s)
            self.assertEqual(seq.beats[0].effect,effect)

    def test_missed_attack_still_has_enemy_counterattack(self):
        seq = self.sequence(Action.TECHNIQUE,replace(self.state,hp=4))
        self.assertEqual(seq.beats[0].result,'SIN DAÑO')
        self.assertEqual(seq.beats[1].actor,'enemy')
        self.assertEqual(seq.beats[1].result,'IMPACTO')
        self.assertTrue(seq.beats[1].charged)

    def test_cancelled_attack_has_no_enemy_projectile(self):
        s=replace(self.state,evolved=1)
        seq=self.sequence(Action.TECHNIQUE,replace(s,enemy_hp=2),s)
        self.assertEqual([b.actor for b in seq.beats],['hero','status'])
        self.assertEqual(seq.beats[1].result,'INTERRUMPIDO')

    def test_interruption_and_final_hit(self):
        seq=self.sequence(Action.INTERRUPT,replace(self.state,enemy_hp=5))
        self.assertEqual(seq.beats[1].actor,'status')
        final=self.sequence(Action.TECHNIQUE,Ending.WIN)
        self.assertEqual(len(final.beats),1)
        self.assertEqual(final.beats[0].result,'GOLPE FINAL')

    def test_defeat_does_not_invent_hero_hit_or_miss(self):
        seq=self.sequence(Action.ATTACK,Ending.LOSS)
        self.assertEqual(seq.beats[0].result,'ATAQUE')
        self.assertEqual(seq.beats[-1].result,'IMPACTO')

    def test_healing_uses_expected_health_not_net_difference(self):
        s=replace(self.state,hp=2)
        seq=self.sequence(Action.HEAL,replace(s,hp=4,potion=False),s)
        self.assertEqual(seq.beats[1].result,'IMPACTO')

    def test_timing_boundaries_and_skip(self):
        seq=self.sequence(Action.ATTACK,replace(self.state,enemy_hp=5))
        step=seq.step
        self.assertEqual(seq.current[0].actor,'hero')
        seq.update(640)
        self.assertEqual(seq.current[0].actor,'enemy')
        seq.update(-10)
        self.assertEqual(seq.elapsed_ms,640)
        seq.finish()
        self.assertFalse(seq.active)
        self.assertIsNone(seq.current)
        self.assertIs(seq.step,step)

    def test_exploration_has_no_combat_sequence(self):
        s=replace(self.state,zone=Zone.VILLAGE,enemy_hp=0)
        self.assertIsNone(self.sequence(Action.ROUTE_FOREST,self.state,s))

    def test_evolution_visual_uses_new_form_after_charge(self):
        seq=self.sequence(Action.DIGIVOLVE,replace(self.state,evolved=3))
        self.assertEqual(seq.display_state.evolved,2)
        seq.update(400)
        self.assertEqual(seq.display_state.evolved,3)
