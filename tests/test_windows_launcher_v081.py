"""Pruebas estaticas de los prerrequisitos del instalador Windows."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class WindowsLauncherTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.script = (ROOT / "JUGAR_WINDOWS.bat").read_text(encoding="utf-8")

    def test_prerrequisitos_antes_de_pip(self):
        s = self.script
        for marker in ['if not exist "pyproject.toml" goto FALTA_EXTRAER',
                       'if not exist "src\\digimon_rl\\play.py" goto FALTA_EXTRAER',
                       'if not exist "politicas\\dp.json" goto FALTA_ARCHIVOS',
                       'if not exist "politicas\\mc.json" goto FALTA_ARCHIVOS']:
            self.assertIn(marker, s)
        self.assertLess(s.index('if not exist "pyproject.toml"'),
                        s.index('-m pip install -e'))

    def test_env_aislado_y_paths_explicitos(self):
        s = self.script
        self.assertIn('%PYTHON_CMD% -m venv ".venv"', s)
        self.assertIn('".venv\\Scripts\\python.exe" -m pip install -e ".[game]"', s)
        self.assertIn('".venv\\Scripts\\python.exe" -m digimon_rl.play --policies "politicas" --assets "assets"', s)

    def test_mensaje_si_no_se_extrae(self):
        s = self.script
        self.assertIn(':FALTA_EXTRAER', s)
        self.assertIn('Extraer todo', s)
        self.assertIn('%CD%', s)

    def test_contenido_suficiente_en_la_carpeta(self):
        for relative in ['pyproject.toml', 'src/digimon_rl/play.py',
                         'politicas/dp.json', 'politicas/mc.json',
                         'assets/digimon/agumon.png', 'assets/digimon/wargreymon.png']:
            with self.subTest(relative=relative):
                self.assertTrue((ROOT / relative).is_file())


if __name__ == '__main__':
    unittest.main()
