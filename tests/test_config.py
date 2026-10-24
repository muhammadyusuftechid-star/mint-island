import unittest
from mint_island.config import ConfigManager, DEFAULT_CONFIG

class TestConfigManager(unittest.TestCase):
    def setUp(self):
        self.cm = ConfigManager()

    def test_default_config_structure(self):
        self.assertIn("general", DEFAULT_CONFIG)
        self.assertIn("modules", DEFAULT_CONFIG)
        self.assertIn("appearance", DEFAULT_CONFIG)
        self.assertTrue(DEFAULT_CONFIG["general"]["enabled"])
        self.assertTrue(DEFAULT_CONFIG["appearance"]["compact_micro_pill"])

    def test_deep_merge(self):
        base = {
            "a": 1,
            "sub": {"x": 10, "y": 20}
        }
        override = {
            "sub": {"y": 99, "z": 30},
            "b": 2
        }
        merged = self.cm._deep_merge(base, override)
        self.assertEqual(merged["a"], 1)
        self.assertEqual(merged["b"], 2)
        self.assertEqual(merged["sub"]["x"], 10)
        self.assertEqual(merged["sub"]["y"], 99)
        self.assertEqual(merged["sub"]["z"], 30)

    def test_get_with_fallback(self):
        val = self.cm.get("appearance", "non_existent_key", default=42)
        self.assertEqual(val, 42)

if __name__ == "__main__":
    unittest.main()
