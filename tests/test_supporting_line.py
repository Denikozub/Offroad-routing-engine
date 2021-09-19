import unittest

from offroad_routing.geometry.supporting_line import find_supporting_line

polygon = ((-1, 0), (2, 3), (4, 1), (5, 2), (6, 0), (5, 5), (2, 5), (-1, 0))
point1 = (2, 1)
point2 = (2, 2.5)


class TestSupportingPair(unittest.TestCase):
    def test_supporting_line_1(self):
        line = find_supporting_line(point1, polygon, 0)
        self.assertEqual(len(line), 5)
        self.assertIn(line[0][0], {(-1, 0), (6, 0)})
        self.assertIn(line[2][0], {(2, 5), (5, 5)})
        self.assertIn(line[4][0], {(-1, 0), (6, 0)})

    def test_supporting_line_2(self):
        line = find_supporting_line(point2, polygon, 0)
        self.assertEqual(len(line), 3)
        self.assertIn(line[0][0], {(-1, 0), (4, 1)})
        self.assertEqual(line[1][0], (2, 3))
        self.assertIn(line[2][0], {(-1, 0), (4, 1)})


if __name__ == '__main__':
    unittest.main()
