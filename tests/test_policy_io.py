import json
import tempfile
import unittest
from pathlib import Path

from digimon_rl.domain import Action, GameState, Zone
from digimon_rl.environment import DigitalWorld
from digimon_rl.policy_io import load_policy, save_policy


class TestPolicyIO(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.world = DigitalWorld()
        # Test unitario de la serialización; el entrenamiento se prueba aparte.
        cls.policy = {cls.world.start_state(): Action.ROUTE_FOREST,
                      GameState(Zone.SWAMP, 6, 3, 0, 1, True, xp=2): Action.TRAIN}

    def test_round_trip(self):
        with tempfile.TemporaryDirectory() as dirname:
            path = Path(dirname) / "policy.json"
            save_policy(path, self.policy, algorithm="value_iteration")
            reloaded = load_policy(path, self.world)
            self.assertEqual(reloaded, self.policy)

    def test_reject_undefined_action(self):
        with tempfile.TemporaryDirectory() as dirname:
            path = Path(dirname) / "policy.json"
            save_policy(path, self.policy, algorithm="value_iteration")
            data = json.loads(path.read_text(encoding="utf-8"))
            data["actions"][0][1] = "inventado"
            path.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaises(ValueError):
                load_policy(path, self.world)

    def test_reject_wrong_format(self):
        with tempfile.TemporaryDirectory() as dirname:
            path = Path(dirname) / "policy.json"
            save_policy(path, self.policy, algorithm="value_iteration")
            data = json.loads(path.read_text(encoding="utf-8"))
            data["format_version"] = 999
            path.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaises(ValueError):
                load_policy(path, self.world)


if __name__ == "__main__":
    unittest.main()
