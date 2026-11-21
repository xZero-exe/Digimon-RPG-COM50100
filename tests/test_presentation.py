import unittest

from digimon_rl.domain import Action, Ending, GameState, Zone
from digimon_rl.presentation import GamePresentation, MODE_DESCRIPTIONS, Screen, STORY
from digimon_rl.session import ControlMode


class PresentationTests(unittest.TestCase):
    def setUp(self):
        self.ui = GamePresentation()
        self.aldea = GameState(Zone.VILLAGE, 6, 2, 0, False, True)

    def test_starts_in_title_and_selects_mode_without_touching_mdp(self):
        self.assertEqual(self.ui.screen, Screen.TITLE)
        self.assertEqual(self.ui.start(ControlMode.MONTE_CARLO), STORY[Zone.VILLAGE])
        self.assertEqual(self.ui.screen, Screen.GAME)
        self.assertEqual(len(MODE_DESCRIPTIONS), 3)

    def test_help_returns_to_correct_screen(self):
        self.ui.open(Screen.HELP)
        self.assertEqual(self.ui.screen, Screen.HELP)
        self.ui.close()
        self.assertEqual(self.ui.screen, Screen.TITLE)
        self.ui.start(ControlMode.MANUAL)
        self.ui.open(Screen.HELP)
        self.ui.close()
        self.assertEqual(self.ui.screen, Screen.GAME)

    def test_pause_only_works_during_game(self):
        self.ui.open(Screen.PAUSE)
        self.assertEqual(self.ui.screen, Screen.TITLE)
        self.ui.start(ControlMode.DYNAMIC_PROGRAMMING)
        self.ui.open(Screen.PAUSE)
        self.assertEqual(self.ui.screen, Screen.PAUSE)
        self.ui.close()
        self.assertEqual(self.ui.screen, Screen.GAME)

    def test_region_and_digivolution_are_narrative_only(self):
        bosque = GameState(Zone.FOREST, 6, 2, 2, False, True)
        title = self.ui.on_transition(self.aldea, Action.ROUTE_FOREST, bosque)
        self.assertEqual(title.title, "BOSQUE BINARIO")
        evolved = GameState(Zone.FOREST, 6, 0, 2, True, True)
        title = self.ui.on_transition(bosque, Action.DIGIVOLVE, evolved)
        self.assertIn("DIGIEVOLUCION", title.title)

    def test_ending_and_defeated_enemy(self):
        bosque = GameState(Zone.FOREST, 4, 2, 1, False, True)
        won = GameState(Zone.FOREST, 4, 2, 0, False, True)
        self.assertEqual(self.ui.on_transition(bosque, Action.ATTACK, won).title, "COMBATE SUPERADO")
        self.assertEqual(self.ui.on_transition(bosque, Action.ATTACK, Ending.LOSS).accent, "red")
        self.assertEqual(self.ui.on_transition(bosque, Action.ATTACK, Ending.WIN).accent, "green")

    def test_no_notice_when_no_milestone(self):
        bosque = GameState(Zone.FOREST, 6, 2, 2, False, True)
        hit = GameState(Zone.FOREST, 5, 2, 1, False, True)
        self.assertIsNone(self.ui.on_transition(bosque, Action.ATTACK, hit))
        self.ui.title()
        self.assertIsNone(self.ui.notice)
        self.assertEqual(self.ui.screen, Screen.TITLE)


if __name__ == "__main__":
    unittest.main()
