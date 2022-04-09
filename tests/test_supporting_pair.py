import unittest

from offroad_routing.osm_data.convex_hull import build_convex_hull
from offroad_routing.visibility.supporting_pair import find_supporting_pair
from offroad_routing.visibility.supporting_pair import find_supporting_pair_semiplanes

polygon1 = ((0, 1), (2, 0), (4, 0), (6, 2), (0, 1))
polygon1, _, angles1 = build_convex_hull(polygon1)
polygon2 = ((0, 1), (2, 0), (6, 2), (0, 1))
polygon2, _, angles2 = build_convex_hull(polygon2)
point1 = (4, -4)
point2 = (6, 1)


class TestSupportingPair(unittest.TestCase):
    def test_polygon1(self):
        pair1 = find_supporting_pair(point1, polygon1, angles1)
        pair2 = find_supporting_pair(point2, polygon1, angles1)
        self.assertIn(pair1[0], {0, 1})
        self.assertIn(pair1[1], {0, 1})
        self.assertIn(pair2[0], {0, 3})
        self.assertIn(pair2[1], {0, 3})
        self.assertIs(find_supporting_pair((4, 1), polygon1, angles1), None)
        self.assertIs(find_supporting_pair(
            (4, 0.5), polygon1, angles1), None)
        self.assertIs(find_supporting_pair((3, 1), polygon1, angles1), None)
        self.assertIs(find_supporting_pair(
            (3, 0.5), polygon1, angles1), None)
        self.assertIs(find_supporting_pair((2, 1), polygon1, angles1), None)
        self.assertIs(find_supporting_pair(
            (2, 0.5), polygon1, angles1), None)
        self.assertIs(find_supporting_pair((1, 1), polygon1, angles1), None)

    def test_polygon2(self):
        pair1 = find_supporting_pair(point1, polygon2, angles2)
        pair2 = find_supporting_pair(point2, polygon2, angles2)
        self.assertIn(pair1[0], {0, 2})
        self.assertIn(pair1[1], {0, 2})
        self.assertIn(pair2[0], {1, 2})
        self.assertIn(pair2[1], {1, 2})
        self.assertIs(find_supporting_pair((3, 1), polygon2, angles2), None)
        self.assertIs(find_supporting_pair((2, 1), polygon2, angles2), None)
        self.assertIs(find_supporting_pair(
            (2.5, 1), polygon2, angles2), None)
        self.assertIs(find_supporting_pair((1, 1), polygon2, angles2), None)

    def test_special(self):
        pair = find_supporting_pair(
            (0, 0), ((-1, 0), (1, 0), (-1, 0)), None)
        self.assertIn(pair[0], {0, 1})
        self.assertIn(pair[1], {0, 1})

    def test_exception(self):
        with self.assertRaises(Exception):
            find_supporting_pair((0, 0), ((0, 0),), None)
        with self.assertRaises(Exception):
            find_supporting_pair((0, 0), ((0, 0), (0, 0)), None)
        with self.assertRaises(Exception):
            find_supporting_pair((0, 0), ((0, 0), (1, 1), (2, 2)), None)
        with self.assertRaises(Exception):
            find_supporting_pair(
                (0, 0), ((0, 0), (0, 1), (1, 1), (1, 0), (0, 0)), None)


class TestSupportingPairSemiplanes(unittest.TestCase):

    def test_polygon1(self):
        pair1 = find_supporting_pair_semiplanes(point1, polygon1)
        pair2 = find_supporting_pair_semiplanes(point2, polygon1)
        self.assertIn(pair1[0], {0, 1})
        self.assertIn(pair1[1], {0, 1})
        self.assertIn(pair2[0], {0, 3})
        self.assertIn(pair2[1], {0, 3})
        self.assertIs(find_supporting_pair_semiplanes((4, 1), polygon1), None)

    def test_polygon2(self):
        pair1 = find_supporting_pair_semiplanes(point1, polygon2)
        pair2 = find_supporting_pair_semiplanes(point2, polygon2)
        self.assertIn(pair1[0], {0, 2})
        self.assertIn(pair1[1], {0, 2})
        self.assertIn(pair2[0], {1, 2})
        self.assertIn(pair2[1], {1, 2})
        self.assertIs(find_supporting_pair_semiplanes((4, 1), polygon2), None)

    def test_special(self):
        pair = find_supporting_pair_semiplanes(
            (0, 0), ((-1, 0), (1, 0), (-1, 0)))
        self.assertIn(pair[0], {0, 1})
        self.assertIn(pair[1], {0, 1})

    def test_exception(self):
        with self.assertRaises(Exception):
            find_supporting_pair_semiplanes((0, 0), ((0, 0),))
        with self.assertRaises(Exception):
            find_supporting_pair_semiplanes((0, 0), ((0, 0), (0, 0)))
        with self.assertRaises(Exception):
            find_supporting_pair_semiplanes(
                (0, 0), ((0, 0), (1, 1), (2, 2)))


if __name__ == '__main__':
    unittest.main()
