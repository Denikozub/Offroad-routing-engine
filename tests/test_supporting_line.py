import unittest

from offroad_routing.visibility.supporting_line import find_restriction_pair
from offroad_routing.visibility.supporting_line import find_supporting_line

polygon = ((-1, 0), (2, 3), (4, 1), (5, 2), (6, 0), (5, 5), (2, 5), (-1, 0))
point1 = (2, 1)
point2 = (2, 2.5)
point3 = (2, -1)
point4 = (3, 3)


class TestSupportingLine(unittest.TestCase):

    def test_point_1(self):
        line = find_supporting_line(point1, polygon, 0)
        self.assertEqual(len(line), 4)
        self.assertIn(line[0][0], {(-1, 0), (6, 0)})
        self.assertIn(line[1][0], {(2, 5), (5, 5)})
        self.assertIn(line[2][0], {(2, 5), (5, 5)})
        self.assertIn(line[3][0], {(-1, 0), (6, 0)})

    def test_point_2(self):
        line = find_supporting_line(point2, polygon, 0)
        self.assertEqual(len(line), 3)
        self.assertIn(line[0][0], {(-1, 0), (4, 1)})
        self.assertEqual(line[1][0], (2, 3))
        self.assertIn(line[2][0], {(-1, 0), (4, 1)})

    def test_point_3(self):
        line = find_supporting_line(point3, polygon, 0)
        self.assertEqual(len(line), 4)
        self.assertIn(line[0][0], {(-1, 0), (6, 0)})
        self.assertIn(line[1][0], {(2, 5), (5, 5)})
        self.assertIn(line[2][0], {(2, 5), (5, 5)})
        self.assertIn(line[3][0], {(-1, 0), (6, 0)})

    def test_point_4(self):
        self.assertIs(find_supporting_line(point4, polygon, 0), None)

    def test_exception(self):
        with self.assertRaises(Exception):
            find_supporting_line((0, 0), ((0, 0),), 0)
        with self.assertRaises(Exception):
            find_supporting_line((0, 0), ((0, 0), (0, 0)), 0)
        with self.assertRaises(Exception):
            find_supporting_line((0, 0), ((0, 0), (1, 1), (2, 2)), 0)


class TestRestrictionPair(unittest.TestCase):

    def test_point_1(self):
        pair = find_restriction_pair((-1, 0), polygon, 0)
        self.assertIn(pair[0], {(2, 5), (6, 0)})
        self.assertIn(pair[1], {(2, 5), (6, 0)})

    def test_point_2(self):
        pair = find_restriction_pair((2, 3), polygon, 1)
        self.assertIn(pair[0], {(-1, 0), (4, 1)})
        self.assertIn(pair[1], {(-1, 0), (4, 1)})

    def test_point_3(self):
        pair = find_restriction_pair((4, 1), polygon, 2)
        self.assertIn(pair[0], {(-1, 0), (6, 0)})
        self.assertIn(pair[1], {(-1, 0), (6, 0)})

    def test_point_4(self):
        pair = find_restriction_pair((2, 5), polygon, 6)
        self.assertIn(pair[0], {(-1, 0), (5, 5)})
        self.assertIn(pair[1], {(-1, 0), (5, 5)})

    def test_point_5(self):
        self.assertIs(find_restriction_pair(point4, polygon, 0), None)

    def test_exception(self):
        with self.assertRaises(Exception):
            find_supporting_line((0, 0), ((0, 0),), 0)
        with self.assertRaises(Exception):
            find_supporting_line((0, 0), ((0, 0), (0, 0)), 0)
        with self.assertRaises(Exception):
            find_supporting_line((0, 0), ((0, 0), (1, 1), (2, 2)), 0)


if __name__ == '__main__':
    unittest.main()
