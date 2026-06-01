import unittest

from reposkillopt_engine.version import bump, parse


class TestVersion(unittest.TestCase):
    def test_parse(self):
        self.assertEqual(parse("0.2.0"), (0, 2, 0))

    def test_bumps(self):
        self.assertEqual(bump("0.2.0", "minor"), "0.3.0")
        self.assertEqual(bump("0.2.3", "patch"), "0.2.4")
        self.assertEqual(bump("0.2.3", "major"), "1.0.0")

    def test_bad_inputs(self):
        with self.assertRaises(ValueError):
            parse("1.2")
        with self.assertRaises(ValueError):
            bump("0.1.0", "sideways")


if __name__ == "__main__":
    unittest.main()
