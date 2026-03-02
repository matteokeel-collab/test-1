import unittest

from fish_auto import BiteDetector, parse_region


class FishAutoTest(unittest.TestCase):
    def test_parse_region(self) -> None:
        self.assertEqual(parse_region("10,20,30,40"), (10, 20, 40, 60))

    def test_parse_region_invalid(self) -> None:
        with self.assertRaises(Exception):
            parse_region("10,20,0,40")

    def test_bite_detector_triggers_after_baseline(self) -> None:
        detector = BiteDetector(window=5, threshold_delta=10)
        for _ in range(5):
            self.assertFalse(detector.update(100))
        self.assertTrue(detector.update(120))


if __name__ == "__main__":
    unittest.main()
