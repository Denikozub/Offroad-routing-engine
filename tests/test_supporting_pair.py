import unittest

from geometry.supporting_pair import find_supporting_pair, find_supporting_pair_cutoff, find_supporting_pair_array
from geometry.convex_hull import build_convex_hull

polygon = ((0, 1), (2, 0), (6, 1), (5, 5), (1, 4), (0, 1))
polygon, _, angles = build_convex_hull(polygon)
point1 = (4, -4)
point2 = (2, 5)


class TestSupportingPair(unittest.TestCase):
    def test_supporting_pair(self):
        pair1 = find_supporting_pair(point1, polygon, 0, angles)
        pair2 = find_supporting_pair(point2, polygon, 0, angles)
        self.assertIn(pair1[0][0], ((0, 1), (6, 1)))
        self.assertIn(pair1[1][0], ((0, 1), (6, 1)))
        self.assertIn(pair2[0][0], ((1, 4), (5, 5)))
        self.assertIn(pair2[1][0], ((1, 4), (5, 5)))

    def test_supporting_pair_cutoff(self):
        pair1 = find_supporting_pair_cutoff(point1, polygon, 0)
        pair2 = find_supporting_pair_cutoff(point2, polygon, 0)
        self.assertIn(pair1[0][0], ((0, 1), (6, 1)))
        self.assertIn(pair1[1][0], ((0, 1), (6, 1)))
        self.assertIn(pair2[0][0], ((1, 4), (5, 5)))
        self.assertIn(pair2[1][0], ((1, 4), (5, 5)))

    def test_supporting_pair_array(self):
        pair1 = find_supporting_pair_array(point1, polygon, 0)
        pair2 = find_supporting_pair_array(point2, polygon, 0)
        self.assertIn(pair1[0][0], ((0, 1), (6, 1)))
        self.assertIn(pair1[1][0], ((0, 1), (6, 1)))
        self.assertIn(pair2[0][0], ((1, 4), (5, 5)))
        self.assertIn(pair2[1][0], ((1, 4), (5, 5)))


if __name__ == '__main__':
    unittest.main()
