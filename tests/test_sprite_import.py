"""El importador tiene pruebas sin imágenes de terceros."""
import importlib.util
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('import_digidex_sprites', ROOT / 'scripts' / 'import_digidex_sprites.py')
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class TestSpriteImport(unittest.TestCase):
    def test_requires_permission(self):
        with TemporaryDirectory() as td:
            with self.assertRaises(PermissionError):
                MODULE.copy_authorized_assets(Path(td), Path(td) / 'out', 'x5', False)

    def test_copies_only_expected_files(self):
        with TemporaryDirectory() as td:
            base = Path(td)
            origin = base / 'digidex' / 'resources' / 'img' / 'sprites' / 'x5'
            origin.mkdir(parents=True)
            for species in MODULE.NAMES:
                (origin / f'{species}.png').write_bytes(b'PNG-fixture-' + species.encode())
            (origin / 'extra.png').write_bytes(b'excluded')
            target = base / 'assets' / 'digimon'
            result = MODULE.copy_authorized_assets(base / 'digidex', target, 'x5', True)
            self.assertEqual(set(result), {p.stem for p in target.glob('*.png')})
            self.assertFalse((target / 'extra.png').exists())
            self.assertEqual(len(result), 7)

    def test_missing_file_causes_no_partial_install(self):
        with TemporaryDirectory() as td:
            base = Path(td)
            origin = base / 'digidex' / 'resources' / 'img' / 'sprites' / 'x5'
            origin.mkdir(parents=True)
            (origin / 'agumon.png').write_bytes(b'test')
            target = base / 'out'
            with self.assertRaises(FileNotFoundError):
                MODULE.copy_authorized_assets(base / 'digidex', target, 'x5', True)
            self.assertFalse(target.exists())


if __name__ == '__main__':
    unittest.main()
