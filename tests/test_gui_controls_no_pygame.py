"""Comprueba eventos y navegación sin abrir pantalla ni depender de SDL.

Estas pruebas NO reemplazan la validación de renderizado con Pygame instalado.
"""
import sys
import types
import unittest
from unittest.mock import patch

from digimon_rl.environment import DigitalWorld
from digimon_rl.presentation import Screen
from digimon_rl.session import AdventureController, ControlMode


class GUIControllerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        fake = types.ModuleType("pygame")
        symbols = [
            'K_ESCAPE','K_RETURN','K_SPACE','K_F1','K_F2','K_F3','K_h','K_c',
            'K_p','K_m','K_r','K_a','K_PLUS','K_EQUALS','K_KP_PLUS',
            'K_MINUS','K_KP_MINUS','K_t','K_LEFT','K_RIGHT',
        ]
        symbols += [f'K_{i}' for i in range(1,8)]
        for n, name in enumerate(symbols, start=100):
            setattr(fake, name, n)
        # K_1...K_6 deben ser consecutivos: el teclado traduce a índices.
        cls.keys = fake
        with patch.dict(sys.modules, {"pygame": fake}):
            from digimon_rl.gui.app import RPGApp
            cls.RPGApp = RPGApp

    def setUp(self):
        self.controller = AdventureController(DigitalWorld(), {}, {}, seed=42)
        self.app = self.RPGApp(self.controller)

    def test_start_manual_and_choose_first_action(self):
        self.assertEqual(self.app.presentation.screen, Screen.TITLE)
        self.app._on_key(self.keys.K_F3)
        self.assertEqual(self.app.presentation.screen, Screen.GAME)
        self.assertEqual(self.controller.mode, ControlMode.MANUAL)
        self.app._on_key(self.keys.K_1)
        self.assertEqual(self.controller.turn, 1)

    def test_start_value_iteration_and_advance(self):
        self.app._on_key(self.keys.K_F1)
        self.assertEqual(self.controller.mode, ControlMode.DYNAMIC_PROGRAMMING)
        self.app._on_key(self.keys.K_SPACE)  # descarta mensaje de bienvenida
        self.app._on_key(self.keys.K_SPACE)  # ejecuta la acción recomendada
        self.assertEqual(self.controller.turn, 1)
        self.assertTrue(self.controller.history[-1])

    def test_help_from_title_and_pause_from_game(self):
        self.app._on_key(self.keys.K_h)
        self.assertEqual(self.app.presentation.screen, Screen.HELP)
        self.app._on_key(self.keys.K_ESCAPE)
        self.assertEqual(self.app.presentation.screen, Screen.TITLE)
        self.app._on_key(self.keys.K_F2)
        self.app._on_key(self.keys.K_p)
        self.assertEqual(self.app.presentation.screen, Screen.PAUSE)
        self.app._on_key(self.keys.K_ESCAPE)
        self.assertEqual(self.app.presentation.screen, Screen.GAME)

    def test_menu_return_stops_auto(self):
        self.app._on_key(self.keys.K_F2)
        self.app._on_key(self.keys.K_a)
        self.assertTrue(self.app.auto)
        self.app._on_key(self.keys.K_m)
        self.assertEqual(self.app.presentation.screen, Screen.TITLE)
        self.assertFalse(self.app.auto)

    def test_switching_algorithm_resets_episode(self):
        self.app._on_key(self.keys.K_F1)
        self.app._on_key(self.keys.K_SPACE)
        self.app._on_key(self.keys.K_SPACE)
        self.assertEqual(self.controller.turn, 1)
        self.app._on_key(self.keys.K_F2)
        self.assertEqual(self.controller.mode, ControlMode.MONTE_CARLO)
        self.assertEqual(self.controller.turn, 0)


if __name__ == '__main__':
    unittest.main()

class AnalysisScreenKeyboardTests(GUIControllerTests):
    def test_analysis_stops_autoplay_and_preserves_state(self):
        self.app._on_key(self.keys.K_F1)
        self.app._on_key(self.keys.K_a)
        self.assertTrue(self.app.auto)
        before = self.controller.state
        self.app._on_key(self.keys.K_t)
        self.assertEqual(self.app.presentation.screen, Screen.ANALYSIS)
        self.assertFalse(self.app.auto)
        self.app._on_key(self.keys.K_ESCAPE)
        self.assertEqual(self.app.presentation.screen, Screen.GAME)
        self.assertEqual(self.controller.state, before)

    def test_analysis_navigates_history_without_playing(self):
        self.app._on_key(self.keys.K_F1)
        self.app._command('next')
        self.app._command('next')
        self.assertEqual(self.controller.turn, 2)
        self.app._on_key(self.keys.K_t)
        end = self.app.inspection_index
        self.assertGreaterEqual(end, 2)
        self.app._on_key(self.keys.K_LEFT)
        self.assertEqual(self.app.inspection_index, end-1)
        self.app._on_key(self.keys.K_RIGHT)
        self.assertEqual(self.app.inspection_index, end)
        self.assertEqual(self.controller.turn, 2)
