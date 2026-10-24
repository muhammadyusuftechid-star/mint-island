import unittest
from mint_island.license import LicenseManager

class TestLicenseManager(unittest.TestCase):
    def setUp(self):
        self.lm = LicenseManager()

    def test_machine_id(self):
        mid = self.lm.get_machine_id()
        self.assertIsInstance(mid, str)
        self.assertGreater(len(mid), 0)

    def test_verify_dev_key(self):
        self.assertTrue(self.lm.verify_offline_checksum("ISL-DEV-MYKEY123456"))
        self.assertFalse(self.lm.verify_offline_checksum("INVALID-KEY-123"))

    def test_is_pro_community(self):
        self.assertTrue(self.lm.is_pro())

if __name__ == "__main__":
    unittest.main()
