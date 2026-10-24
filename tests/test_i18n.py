import unittest
from mint_island.i18n import _, i18n

class TestI18n(unittest.TestCase):
    def test_default_translations(self):
        # Save original lang
        orig_lang = i18n.current_lang

        # Test Indonesian
        i18n.set_language("id")
        self.assertEqual(_("Settings"), "Pengaturan")
        self.assertEqual(_("Power Mode"), "Mode Daya")

        # Test English
        i18n.set_language("en")
        self.assertEqual(_("Settings"), "Settings")
        self.assertEqual(_("Power Mode"), "Power Mode")

        # Fallback test
        self.assertEqual(_("Non-existent translation key"), "Non-existent translation key")

        # Restore
        i18n.set_language(orig_lang)

if __name__ == "__main__":
    unittest.main()
