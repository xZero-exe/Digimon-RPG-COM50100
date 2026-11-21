"""Regresiones de sincronización, persistencia y recursos sonoros originales."""
from array import array
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
import wave
from digimon_rl.audio_events import SoundCue, SoundTimeline, combat_cues
from digimon_rl.audio_settings import AudioSettings
from digimon_rl.combat_visuals import ALL_EFFECTS, CombatAnimation
from digimon_rl.domain import Action, GameState, Step, Zone
from digimon_rl.environment import DigitalWorld
from digimon_rl.region_transition import RegionTransition

ROOT=Path(__file__).resolve().parents[1]


class AudioEventTests(unittest.TestCase):
    def test_every_attack_and_support_sound_is_bundled_playable_pcm(self):
        root=ROOT/'assets/audio'
        manifest=json.loads((root/'manifest_v018.json').read_text())
        names={Path(row['file']).stem for row in manifest['files']}
        self.assertTrue(set(ALL_EFFECTS)<names)
        self.assertTrue({'ui','heal','guard','evolve','impact','no_hit','cancel','travel','victory','loss'}<=names)
        for row in manifest['files']:
            path=root/row['file']
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),row['sha256'])
            with wave.open(str(path),'rb') as wav:
                self.assertEqual((wav.getnchannels(),wav.getsampwidth(),wav.getframerate()),(1,2,22050))
                self.assertTrue(.03<wav.getnframes()/22050<1)
                samples=array('h');samples.frombytes(wav.readframes(wav.getnframes()))
                self.assertGreater(max(abs(v) for v in samples),500)
                self.assertLess(max(abs(v) for v in samples),.73*32767)

    def test_timeline_consumes_once_and_never_replays_after_rewind(self):
        track=SoundTimeline((SoundCue(40,'basic_attack'),SoundCue(384,'impact')))
        self.assertEqual(track.advance(20),())
        self.assertEqual([c.name for c in track.advance(50)],['basic_attack'])
        self.assertEqual(track.advance(50),())
        self.assertEqual([c.name for c in track.advance(400)],['impact'])
        self.assertEqual(track.advance(0),())

    def test_lag_and_skip_do_not_produce_a_burst_of_old_sounds(self):
        track=SoundTimeline(tuple(SoundCue(t,'ui') for t in (40,384,680,1024)))
        self.assertEqual(track.advance(2000),())
        track=SoundTimeline((SoundCue(40,'basic_attack'),SoundCue(384,'impact')))
        track.discard();self.assertEqual(track.advance(500),())

    def test_cancelled_counterattack_has_no_enemy_sound(self):
        world=DigitalWorld();state=GameState(Zone.SWAMP,5,3,3,0,True,True)
        outcome=next(t for t in world.transitions(state,Action.INTERRUPT)
                     if isinstance(t.next_state,GameState) and t.next_state.enemy_hp==2)
        seq=CombatAnimation.from_step(Step(state,Action.INTERRUPT,outcome.reward,outcome.next_state))
        names=[cue.name for cue in combat_cues(seq)]
        self.assertIn('interrupt_strike',names);self.assertIn('cancel',names)
        self.assertNotIn('haouken',names)

    def test_no_damage_and_unknown_damage_do_not_claim_an_impact(self):
        state=GameState(Zone.FORTRESS,6,3,6,0,True)
        after=replace(state,hp=3)
        seq=CombatAnimation.from_step(Step(state,Action.ATTACK,-13,after))
        own=[c.name for c in combat_cues(seq) if c.time_ms<640]
        self.assertIn('no_hit',own);self.assertNotIn('impact',own)


class AudioPreferenceTests(unittest.TestCase):
    def test_preferences_round_trip_and_invalid_files_recover_defaults(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/'config/audio.json'
            self.assertEqual(AudioSettings.load(p),AudioSettings())
            self.assertTrue(AudioSettings(.7,True).save(p))
            self.assertEqual(AudioSettings.load(p),AudioSettings(.7,True))
            for value in ('bad json','[]','{"volume":NaN,"muted":"yes"}'):
                p.write_text(value);self.assertEqual(AudioSettings.load(p),AudioSettings())
            p.write_text('{"volume":9,"muted":false}')
            self.assertEqual(AudioSettings.load(p).volume,1.)

    def test_failed_save_does_not_raise_or_create_game_state(self):
        with tempfile.TemporaryDirectory() as temp:
            blocker=Path(temp)/'file';blocker.write_text('occupied')
            self.assertFalse(AudioSettings().save(blocker/'audio.json'))


class RegionTransitionTests(unittest.TestCase):
    def test_only_zone_changes_create_a_transition_and_timing_is_bounded(self):
        world=DigitalWorld();before=world.start_state()
        outcome=world.transitions(before,Action.ROUTE_CAVE)[0]
        step=Step(before,Action.ROUTE_CAVE,outcome.reward,outcome.next_state)
        seq=RegionTransition.from_step(step)
        self.assertEqual(seq.display_state,before);self.assertEqual(seq.opacity,0)
        seq.update(-100);self.assertEqual(seq.elapsed_ms,0)
        seq.update(280);self.assertEqual(seq.display_state,step.next_state)
        self.assertGreater(seq.opacity,200)
        seq.finish();self.assertFalse(seq.active);self.assertEqual(seq.opacity,0)
        self.assertEqual(step.state,before)
        self.assertIsNone(RegionTransition.from_step(Step(before,Action.ATTACK,0,before)))
