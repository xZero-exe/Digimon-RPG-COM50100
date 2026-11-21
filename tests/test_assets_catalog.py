import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from digimon_rl.assets_catalog import (BACKGROUND_NAMES, ENEMY_SPRITES,
                                       HERO_SPRITES, SOURCE_PREFIX, SPRITE_NAMES,
                                       find_asset_root, resolve_asset)
from digimon_rl.domain import Zone


class TestAssetCatalog(unittest.TestCase):
    def test_full_species_mapping(self):
        self.assertEqual(set(ENEMY_SPRITES), set(Zone) - {Zone.VILLAGE,Zone.REFUGE})
        self.assertEqual(set(ENEMY_SPRITES.values()) | set(HERO_SPRITES.values()), set(SPRITE_NAMES))
        self.assertEqual(set(BACKGROUND_NAMES), set(Zone))

    def test_digidex_paths_use_x5(self):
        self.assertEqual(str(SOURCE_PREFIX).replace('\\', '/'), 'resources/img/sprites/x5')
        self.assertEqual(len(SPRITE_NAMES), 11)

    def test_asset_precedence_and_demo_fallback(self):
        with TemporaryDirectory() as td:
            root = Path(td)
            demo = root / 'demo' / 'digimon' / 'agumon.png'
            demo.parent.mkdir(parents=True)
            demo.write_bytes(b'demo')
            self.assertEqual(resolve_asset(root, 'digimon', 'agumon'), demo)
            custom = root / 'digimon' / 'agumon.png'
            custom.parent.mkdir(parents=True)
            custom.write_bytes(b'authorized custom')
            self.assertEqual(resolve_asset(root, 'digimon', 'agumon'), custom)

    def test_asset_root_override(self):
        with TemporaryDirectory() as td:
            self.assertEqual(find_asset_root(Path(td)), Path(td).resolve())


if __name__ == '__main__':
    unittest.main()
