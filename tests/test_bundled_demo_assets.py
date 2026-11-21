"""Pruebas de los assets que efectivamente viajan en el ZIP."""
import struct
import unittest
from pathlib import Path

from digimon_rl.assets_catalog import BACKGROUND_NAMES, SPRITE_NAMES, DIGIDEX_NAMES

ROOT = Path(__file__).resolve().parents[1]


class TestBundledDemoAssets(unittest.TestCase):
    def test_all_seven_sprites_in_package(self):
        for name in SPRITE_NAMES:
            with self.subTest(name=name):
                self._check_png(ROOT / 'assets' / 'demo' / 'digimon' / f'{name}.png')

    def test_all_six_backgrounds_in_package(self):
        for name in BACKGROUND_NAMES.values():
            with self.subTest(name=name):
                self._check_png(ROOT / 'assets' / 'demo' / 'backgrounds' / f'{name}.png')

    def test_all_seven_user_supplied_digidex_sprites_bundled(self):
        import json
        from digimon_rl.assets_catalog import resolve_asset
        metadata = json.loads((ROOT / "assets" / "DIGIDEX_MANIFEST.json").read_text(encoding="utf-8"))
        for name in DIGIDEX_NAMES:
            with self.subTest(name=name):
                target = ROOT / "assets" / "digimon" / f"{name}.png"
                self.assertTrue(target.is_file())
                self.assertEqual(resolve_asset(ROOT / "assets", "digimon", name), target)
                self.assertEqual(metadata["characters"][name]["sha256"], __import__("hashlib").sha256(target.read_bytes()).hexdigest())

    @staticmethod
    def _check_png(path):
        assert path.is_file(), f'Falta PNG de demostración: {path}'
        with path.open('rb') as f:
            header=f.read(24)
        assert header[:8] == b'\x89PNG\r\n\x1a\n', f'PNG inválido: {path}'
        w,h=struct.unpack('>II',header[16:24])
        assert w >= 100 and h >= 100, f'Dimensiones inválidas {path}: {w}x{h}'


if __name__ == '__main__':
    unittest.main()
