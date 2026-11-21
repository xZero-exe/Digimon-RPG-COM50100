"""Contrasta el feedback con resultados legales del MDP, incluyendo terminales."""
import unittest
from digimon_rl.combat_visuals import CombatAnimation
from digimon_rl.domain import Action, Ending, GameState, Step, Zone
from digimon_rl.environment import DigitalWorld


class CombatFeedbackTests(unittest.TestCase):
    def setUp(self):
        self.world = DigitalWorld()

    def sequence(self, state, action, predicate):
        outcome = next(t for t in self.world.transitions(state,action) if predicate(t.next_state))
        return CombatAnimation.from_step(Step(state,action,outcome.reward,outcome.next_state))

    def test_feedback_finishes_at_actual_resources_for_legal_outcomes(self):
        checked = 0
        for zone in self.world.ENEMY_HP:
            for form in range(4):
                for hp in (1,3,6):
                    for charged in (False,True):
                        state = GameState(zone,hp,6,self.world.ENEMY_HP[zone],form,True,charged)
                        for action in self.world.actions(state):
                            for outcome in self.world.transitions(state,action):
                                seq = CombatAnimation.from_step(Step(state,action,outcome.reward,outcome.next_state))
                                final = seq.feedback.sample(seq.beats,seq.duration_ms)
                                after = outcome.next_state
                                if isinstance(after,GameState):
                                    self.assertAlmostEqual(final.hero_hp,after.hp)
                                    self.assertAlmostEqual(final.enemy_hp,after.enemy_hp)
                                    self.assertAlmostEqual(final.energy,after.energy)
                                elif after == Ending.WIN:
                                    self.assertEqual(final.enemy_hp,0)
                                    self.assertEqual(final.hero_hp,state.hp)
                                else:
                                    self.assertEqual(final.hero_hp,0)
                                    self.assertIsNone(final.enemy_hp)
                                self.assertGreaterEqual(final.hero_hp,0)
                                self.assertLessEqual(final.hero_hp,6)
                                checked += 1
        self.assertGreater(checked,2000)

    def test_heal_and_counterattack_are_separate_when_net_health_is_zero(self):
        state = GameState(Zone.FOREST,2,3,2,0,True,True)
        seq = self.sequence(state,Action.HEAL,lambda s:isinstance(s,GameState) and s.hp==2)
        self.assertEqual(seq.feedback.hero_changes[0].amount,3)
        self.assertEqual(seq.feedback.enemy_changes[0].amount,-3)
        healed = seq.feedback.sample(seq.beats,640)
        self.assertEqual(healed.hero_hp,5)
        own_text = [n.text for n in seq.feedback.notices(seq.beats,450)]
        foe_text = [n.text for n in seq.feedback.notices(seq.beats,1150)]
        self.assertIn('+3 PS',own_text)
        self.assertIn('-3 PS',foe_text)
        self.assertEqual(seq.feedback.flash_for(seq.beats,450,'hero'),'heal')
        self.assertEqual(seq.feedback.flash_for(seq.beats,1100,'hero'),'damage')

    def test_effective_heal_is_capped_and_overkill_is_not_invented(self):
        state = GameState(Zone.FOREST,5,3,1,0,True)
        heal = self.sequence(state,Action.HEAL,lambda s:isinstance(s,GameState) and s.hp==6)
        self.assertEqual(heal.feedback.hero_changes[0].amount,1)
        hit = self.sequence(state,Action.POWER_ATTACK,lambda s:isinstance(s,GameState) and s.enemy_hp==0)
        damage = next(c for c in hit.feedback.hero_changes if c.target=='enemy')
        self.assertEqual(damage.amount,-1)
        self.assertEqual([b.actor for b in hit.beats],['hero'])

    def test_armor_does_not_claim_a_miss(self):
        state = GameState(Zone.FORTRESS,6,3,6,0,True)
        seq = self.sequence(state,Action.ATTACK,lambda s:isinstance(s,GameState))
        text = [n.text for n in seq.feedback.notices(seq.beats,450)]
        self.assertIn('SIN DAÑO',text)
        self.assertNotIn('FALLÓ',text)
        self.assertIsNone(seq.feedback.flash_for(seq.beats,450,'enemy'))

    def test_cancelled_counterattack_never_damages_player(self):
        state = GameState(Zone.SWAMP,5,3,3,0,True,True)
        seq = self.sequence(state,Action.INTERRUPT,lambda s:isinstance(s,GameState) and s.enemy_hp==2)
        self.assertEqual([b.actor for b in seq.beats],['hero','status'])
        self.assertEqual(seq.feedback.sample(seq.beats,seq.duration_ms).hero_hp,5)
        self.assertIn('CANCELADO',[n.text for n in seq.feedback.notices(seq.beats,850)])
        failed = self.sequence(state,Action.INTERRUPT,lambda s:isinstance(s,GameState) and s.enemy_hp==3)
        self.assertIn('FALLÓ',[n.text for n in failed.feedback.notices(failed.beats,450)])
        self.assertEqual(failed.beats[1].actor,'enemy')

    def test_loss_keeps_enemy_health_unknown_and_only_reports_effective_player_loss(self):
        state = GameState(Zone.FORTRESS,1,3,6,0,True)
        seq = self.sequence(state,Action.ATTACK,lambda s:s==Ending.LOSS)
        self.assertIsNone(next(c.amount for c in seq.feedback.hero_changes if c.target=='enemy'))
        self.assertEqual(seq.feedback.enemy_changes[0].amount,-1)
        self.assertFalse(any(n.target=='enemy' for n in seq.feedback.notices(seq.beats,450)))

    def test_tween_waits_for_impact_and_moves_monotonically(self):
        state = GameState(Zone.FOREST,6,3,2,0,True)
        seq = self.sequence(state,Action.ATTACK,lambda s:isinstance(s,GameState) and s.enemy_hp==1 and s.hp==5)
        samples = [seq.feedback.sample(seq.beats,t) for t in (0,383,430,500,640,1023,1100,1300)]
        self.assertEqual(samples[1].enemy_hp,2)
        self.assertGreater(samples[2].enemy_hp,1)
        self.assertLess(samples[2].enemy_hp,2)
        self.assertEqual(samples[4].enemy_hp,1)
        self.assertEqual(samples[5].hero_hp,6)
        self.assertEqual(samples[-1].hero_hp,5)
        self.assertTrue(all(a.enemy_hp>=b.enemy_hp for a,b in zip(samples,samples[1:])))

    def test_evolution_form_remains_visible_during_settle_and_terminal_loss(self):
        state = GameState(Zone.RUINS,1,6,4,1,True,True)
        seq = self.sequence(state,Action.DIGIVOLVE,lambda s:s==Ending.LOSS)
        seq.elapsed_ms = sum(b.duration_ms for b in seq.beats)+100
        self.assertTrue(seq.active)
        self.assertEqual(seq.display_state.evolved,2)
        self.assertEqual(seq.feedback.sample(seq.beats,seq.elapsed_ms).energy,4)
