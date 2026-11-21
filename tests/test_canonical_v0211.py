"""Regresión: el catálogo actual solo contiene los Digimon aprobados."""
from pathlib import Path
import hashlib,json,unittest
from digimon_rl.assets_catalog import HERO_SPRITES,ENEMY_SPRITES,SPRITE_NAMES,DIGIDEX_NAMES
from digimon_rl.domain import Zone
from digimon_rl.session import ENEMIES,ENEMY_SKILLS
from digimon_rl.combat_visuals import ENEMY_EFFECTS
ROOT=Path(__file__).resolve().parents[1]

class CanonicalCatalogTests(unittest.TestCase):
    def test_all_playable_and_enemy_species_are_the_approved_digimon(self):
        approved={'agumon','greymon','metalgreymon','wargreymon','betamon','goblimon','ogremon','devimon','andromon','piedmon','guardromon'}
        self.assertEqual(set(SPRITE_NAMES),approved)
        self.assertEqual(set(HERO_SPRITES.values())|set(ENEMY_SPRITES.values()),approved)
        self.assertEqual(set(DIGIDEX_NAMES),approved)

    def test_guardromon_has_canonical_identity_move_and_missile_visual(self):
        self.assertEqual(ENEMIES[Zone.ABYSS],'Guardromon')
        self.assertEqual(ENEMY_SPRITES[Zone.ABYSS],'guardromon')
        self.assertEqual(ENEMY_SKILLS[Zone.ABYSS],'Destruction Grenade')
        self.assertEqual(ENEMY_EFFECTS[Zone.ABYSS],'giga_destroyer')

    def test_real_guardromon_asset_matches_manifest_and_replaces_invented_asset(self):
        entry=json.loads((ROOT/'assets/DIGIDEX_MANIFEST.json').read_text())['characters']['guardromon']
        data=(ROOT/entry['local_path']).read_bytes()
        self.assertEqual(data[:8],b'\x89PNG\r\n\x1a\n')
        self.assertEqual(hashlib.sha256(data).hexdigest(),entry['sha256'])
        self.assertIn('digimon.net/reference_en/',entry['canonical_reference'])
        self.assertEqual((ROOT/'assets/demo/digimon/guardromon.png').read_bytes(),data)
        self.assertFalse(any(p.name=='abyss_guardian.png' for p in (ROOT/'assets').rglob('*.png')))
if __name__=='__main__':unittest.main()
