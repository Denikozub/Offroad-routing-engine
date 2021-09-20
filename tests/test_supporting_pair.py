import unittest

from offroad_routing.geometry.supporting_pair import find_supporting_pair
from offroad_routing.geometry.convex_hull import build_convex_hull

polygon1 = ((0, 1), (2, 0), (4, 0), (6, 2), (0, 1))
polygon1, _, angles1 = build_convex_hull(polygon1)
polygon2 = ((0, 1), (2, 0), (6, 2), (0, 1))
polygon2, _, angles3 = build_convex_hull(polygon2)
point1 = (4, -4)
point2 = (6, 1)


class TestSupportingPair(unittest.TestCase):
    def test_supporting_pair_1(self):
        pair1 = find_supporting_pair(point1, polygon1, 0, angles1)
        pair2 = find_supporting_pair(point2, polygon1, 0, angles1)
        self.assertIn(pair1[0][0], ((0, 1), (6, 2)))
        self.assertIn(pair1[1][0], ((0, 1), (6, 2)))
        self.assertIn(pair2[0][0], ((4, 0), (6, 2)))
        self.assertIn(pair2[1][0], ((4, 0), (6, 2)))
        self.assertIs(find_supporting_pair((4, 1), polygon1, 0, angles1), None)

    def test_supporting_pair_2(self):
        pair1 = find_supporting_pair(point1, polygon2, 0, angles3)
        pair2 = find_supporting_pair(point2, polygon2, 0, angles3)
        self.assertIn(pair1[0][0], ((0, 1), (6, 2)))
        self.assertIn(pair1[1][0], ((0, 1), (6, 2)))
        self.assertIn(pair2[0][0], ((2, 0), (6, 2)))
        self.assertIn(pair2[1][0], ((2, 0), (6, 2)))
        self.assertIs(find_supporting_pair((4, 1), polygon2, 0, angles1), None)

    def test_supporting_pair_3(self):
        self.assertIs(find_supporting_pair((0, 0), ((0, 0), (0, 0)), 0, None), None)
        pair = find_supporting_pair((0, 0), ((-1, 0), (1, 0), (-1, 0)), 0, None)
        self.assertIn(pair[0][0], ((-1, 0), (1, 0)))
        self.assertIn(pair[1][0], ((-1, 0), (1, 0)))


if __name__ == '__main__':
    unittest.main()
