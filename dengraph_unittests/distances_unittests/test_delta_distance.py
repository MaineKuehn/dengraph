import unittest

from dengraph.distances.delta_distance import DeltaDistance


class TestDeltaDistance(unittest.TestCase):
    def test_mean_iterator(self):
        distance = DeltaDistance()
        self.assertEqual(4.5, distance.mean(range(10)))

    def test_mean_args(self):
        distance = DeltaDistance()
        self.assertEqual(4.5, distance.mean(0, 1, 2, 3, 4, 5, 6, 7, 8, 9))

    def test_mean_exception(self):
        distance = DeltaDistance()
        with self.assertRaises(ValueError):
            distance.mean()

    def test_mean_exception_with_default(self):
        distance = DeltaDistance()
        self.assertIsNone(distance.mean(default=None))

    def test_median_iterator(self):
        distance = DeltaDistance()
        self.assertEqual(6, distance.median(range(10, 0, -1)))
        self.assertEqual(6, distance.median(range(10, 1, -1)))

    def test_median_args(self):
        distance = DeltaDistance()
        self.assertEqual(6, distance.median(10, 9, 8, 7, 6, 5, 4, 3, 2, 1))
        self.assertEqual(6, distance.median(10, 9, 8, 7, 6, 5, 4, 3, 2))

    def test_median_exception(self):
        distance = DeltaDistance()
        with self.assertRaises(ValueError):
            distance.median()

    def test_median_exception_with_default(self):
        distance = DeltaDistance()
        self.assertIsNone(distance.median(default=None))
