"""El diario observa el mismo episodio del MDP; nunca lo vuelve a simular."""
import unittest
from pathlib import Path
from random import Random
from digimon_rl.adventure_summary import summarize
from digimon_rl.assets_catalog import HERO_SPRITES, ENEMY_SPRITES
from digimon_rl.digidex import load_entries, rpg_facts
from digimon_rl.domain import Action, Ending, GameState
from digimon_rl.environment import DigitalWorld
from digimon_rl.policy_io import load_policy
from digimon_rl.presentation import GamePresentation, Screen
from digimon_rl.session import AdventureController, ControlMode, ENEMIES, ENEMY_SKILLS

ROOT=Path(__file__).resolve().parents[1]

class JournalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.world=DigitalWorld()
        cls.dp=load_policy(ROOT/'politicas/dp.json',cls.world)

    def controller(self,seed=42,max_steps=80):
        return AdventureController(self.world,self.dp,{},seed=seed,max_steps=max_steps)

    def test_recording_preserves_exact_mdp_trajectories(self):
        # Incluye victoria, derrota y diferentes resultados aleatorios.
        outcomes=set()
        for seed in range(40,70):
            expected=self.world.episode(lambda s,l,r:self.dp[s],Random(seed))
            c=self.controller(seed)
            while not c.finished:c.advance()
            self.assertEqual(tuple(r.step for r in c.decisions),expected.steps)
            self.assertEqual(c.state,expected.final_state)
            self.assertEqual(c.reward,expected.total_reward)
            outcomes.add(c.outcome)
        self.assertIn('VICTORIA',outcomes)
        self.assertIn('DERROTA',outcomes)

    def test_ledger_does_not_truncate_with_message_history(self):
        c=self.controller()
        while not c.finished:c.advance()
        self.assertGreater(c.turn,12)
        self.assertEqual(len(c.history),12)
        self.assertEqual(len(c.decisions),c.turn)
        self.assertTrue(all(r.driver==ControlMode.DYNAMIC_PROGRAMMING and not r.fallback for r in c.decisions))

    def test_summary_matches_rewards_and_discounted_return(self):
        c=self.controller()
        while not c.finished:c.advance()
        data=summarize(c,.9)
        expected=self.world.episode(lambda s,l,r:self.dp[s],Random(42),gamma=.9)
        self.assertEqual(data.reward,expected.total_reward)
        self.assertAlmostEqual(data.discounted_return,expected.discounted_return)
        self.assertEqual(data.route[0],self.world.start_state().zone)
        self.assertEqual(data.forms,('Agumon','Greymon','MetalGreymon','WarGreymon'))
        self.assertEqual(data.victories,5)
        self.assertTrue(data.complete)

    def test_summary_is_readonly_and_repeatable(self):
        c=self.controller();c.advance()
        before=(c.state,c.rng.getstate(),c.turn,c.reward,tuple(c.decisions))
        a=summarize(c)
        self.assertEqual(a,summarize(c))
        self.assertEqual(before,(c.state,c.rng.getstate(),c.turn,c.reward,tuple(c.decisions)))

    def test_terminal_resources_are_labelled_before_final_turn(self):
        c=self.controller()
        while not c.finished:c.advance()
        data=summarize(c)
        self.assertEqual(data.last_observed,c.decisions[-1].step.state)
        self.assertEqual(data.resource_label,'Antes del turno final')

    def test_limit_is_distinct_from_defeat_and_has_current_resources(self):
        c=self.controller(max_steps=1);c.advance();data=summarize(c)
        self.assertEqual(data.outcome,'LIMITE DE TURNOS')
        self.assertEqual(data.resource_label,'Recursos actuales')
        self.assertIsInstance(data.last_observed,GameState)
        self.assertTrue(data.complete)

    def test_reset_clears_ledger_and_updates_reproducible_seed(self):
        c=self.controller();c.advance();c.reset(ControlMode.MANUAL)
        self.assertEqual(c.decisions,[])
        self.assertEqual(summarize(c).seed,43)
        self.assertEqual(summarize(c).turns,0)
        self.assertTrue(summarize(c).complete)

    def test_illegal_or_missing_action_is_not_recorded(self):
        c=self.controller();c.reset(ControlMode.MANUAL)
        before=c.rng.getstate()
        for action in (None,Action.HEAL):
            with self.assertRaises(ValueError):c.advance(action)
        self.assertEqual(c.decisions,[])
        self.assertEqual(c.rng.getstate(),before)

    def test_automatic_fallback_is_identified(self):
        c=AdventureController(self.world,{},{});c.advance()
        self.assertTrue(c.decisions[0].fallback)
        self.assertEqual(summarize(c).fallback_actions,1)
        self.assertEqual(summarize(c).moments[0].driver,'Respaldo')

    def test_explicit_action_is_recorded_as_manual(self):
        c=self.controller();c.advance(Action.ROUTE_FOREST)
        self.assertEqual(c.decisions[0].driver,ControlMode.MANUAL)
        self.assertFalse(c.decisions[0].fallback)

    def test_partial_external_state_is_not_presented_as_complete(self):
        c=self.controller();c.state=Ending.LOSS
        self.assertFalse(summarize(c).complete)

    def test_moments_reference_actual_pre_action_states(self):
        c=self.controller()
        while not c.finished:c.advance()
        for moment in summarize(c).moments:
            step=c.decisions[moment.index].step
            self.assertIn(step.action,self.world.actions(step.state))
            self.assertTrue(moment.detail)

    def test_digidex_has_exact_game_roster_and_sources(self):
        rows=load_entries()
        self.assertEqual({r.species for r in rows},set(HERO_SPRITES.values())|set(ENEMY_SPRITES.values()))
        self.assertEqual(len(rows),11)
        for row in rows:
            self.assertTrue(row.source_url.startswith('https://digimon.net/reference_en/detail.php?directory_name='))
            self.assertEqual(len(rpg_facts(row)),6)
            self.assertTrue(row.moves)
            if row.zone is not None:
                self.assertEqual(row.name,ENEMIES[row.zone])
                self.assertIn(ENEMY_SKILLS[row.zone],row.moves)

    def test_classic_variant_sources_and_english_moves(self):
        entries={r.species:r for r in load_entries()}
        self.assertTrue(entries['greymon'].source_url.endswith('=greymon-first'))
        self.assertTrue(entries['metalgreymon'].source_url.endswith('=metalgreymon-v'))
        self.assertEqual(entries['metalgreymon'].attribute,'Vaccine')
        self.assertEqual(entries['agumon'].moves,('Pepper Breath',))
        self.assertEqual(entries['guardromon'].moves,('Destruction Grenade',))

    def test_new_auxiliary_screens_preserve_origin(self):
        ui=GamePresentation()
        for origin in (Screen.TITLE,Screen.GAME):
            for screen in (Screen.DIGIDEX,Screen.SUMMARY):
                ui.screen=origin;ui.open(screen);ui.close()
                self.assertEqual(ui.screen,origin)

    def test_invalid_discount_rejected(self):
        for gamma in (0,1,-1):
            with self.assertRaises(ValueError):summarize(self.controller(),gamma)

if __name__=='__main__':unittest.main()
