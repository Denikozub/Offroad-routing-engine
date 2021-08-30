import unittest
from geometry.algorithms import *


class TestPointDistance(unittest.TestCase):
    def test_distance_1(self):
        distance = point_distance((38.68869, 55.388), (38.76534, 55.36447))
        self.assertGreater(distance, 5.45)
        self.assertLess(distance, 5.55)

    def test_distance_2(self):
        distance = point_distance((-80.7055, 47.085), (-86.792, 50.48556))
        self.assertGreater(distance, 584)
        self.assertLess(distance, 586)


class TestCrossProduct(unittest.TestCase):
    def test_value(self):
        self.assertAlmostEqual(cross_product((9, 2), (-2, 5)), 49)
        self.assertAlmostEqual(cross_product((-3, 10), (4, -2)), -34)

    def test_sign(self):
        self.assertEqual(cross_product((1, 1), (2, 2)), 0)
        self.assertGreater(cross_product((0, 1), (-1, 0)), 0)
        self.assertLess(cross_product((0, 1), (1, 0)), 0)


class TestTurn(unittest.TestCase):
    def test_sign(self):
        self.assertEqual(turn((0, 0), (0, 1), (0, 2)), 0)
        self.assertLess(turn((0, 0), (0, 1), (1, 1)), 0)
        self.assertGreater(turn((0, 0), (0, 1), (-1, 1)), 0)


class TestPolarAngle(unittest.TestCase):
    def test_angle(self):
        self.assertAlmostEqual(polar_angle((0, 0), (1, 1)), pi / 4)
        self.assertAlmostEqual(polar_angle((0, 0), (-1, -1)), 5 * pi / 4)
        self.assertAlmostEqual(polar_angle((4, 8), (5, 7)), 7 * pi / 4)
        self.assertAlmostEqual(polar_angle((-3, 6), (-4, 7)), 3 * pi / 4)

    def test_axis(self):
        self.assertAlmostEqual(polar_angle((0, 0), (1, 0)), 0)
        self.assertAlmostEqual(polar_angle((0, 0), (-1, 0)), pi)
        self.assertAlmostEqual(polar_angle((7, 5), (7, 6)), pi / 2)
        self.assertAlmostEqual(polar_angle((11, -5), (11, -6)), 3 * pi / 2)


class TestPointInSector(unittest.TestCase):
    def test_in(self):
        self.assertTrue(point_in_sector((5, 5), (1, 7), (1, 1), (7, 1)))

    def test_out(self):
        self.assertFalse(point_in_sector((5, 5), (-7, -1), (1, 1), (-1, -7)))

    def test_border(self):
        self.assertFalse(point_in_sector((0, 0), (5, 4), (0, 0), (9, -8)))
        self.assertFalse(point_in_sector((0, 10), (0, 5), (0, 0), (5, 0)))


class TestSegmentsIntersect(unittest.TestCase):
    def test_intersect(self):
        self.assertTrue(segments_intersect((-1, 0), (1, 0), (0, 1), (0, -1)))
        self.assertTrue(segments_intersect((1, 2), (-1, -2), (2, 1), (-2, -1)))

    def test_not_intersect(self):
        self.assertFalse(segments_intersect((-1, -1), (0, 0), (0, 1), (1, 0)))
        self.assertFalse(segments_intersect((0, 0), (0, 1), (1, 0), (1, 1)))

    def test_border(self):
        self.assertFalse(segments_intersect((0, 0), (0, 1), (-1, 1), (1, 1)))
        self.assertFalse(segments_intersect((1, 1), (3, 3), (1, 1), (3, 3)))


class TestRayIntersectsSegment(unittest.TestCase):
    def test_intersect(self):
        self.assertTrue(ray_intersects_segment((-1, 0), (1, 0), (0, 1), (0, -1)))
        self.assertTrue(ray_intersects_segment((1, 2), (-1, -2), (2, 1), (-2, -1)))
        self.assertTrue(ray_intersects_segment((-1, -1), (0, 0), (0, 1), (1, 0)))
        self.assertTrue(ray_intersects_segment((-1, 0), (1, 0), (2, 2), (2, -2)))

    def test_not_intersect(self):
        self.assertFalse(ray_intersects_segment((0, 0), (0, -1), (-1, 1), (1, 1)))
        self.assertFalse(ray_intersects_segment((0, 0), (0, 1), (1, 0), (1, 1)))
        self.assertFalse(ray_intersects_segment((0, 0), (0, 1), (2, 2), (2, 3)))

    def test_border(self):
        self.assertTrue(ray_intersects_segment((0, 0), (0, 1), (-1, 0), (1, 0), True))
        self.assertTrue(ray_intersects_segment((0, 0), (0, 1), (0, 2), (2, 2), True))
        self.assertFalse(ray_intersects_segment((0, 0), (0, 1), (-1, 0), (1, 0), False))
        self.assertFalse(ray_intersects_segment((0, 0), (0, 1), (0, 2), (2, 2), False))


if __name__ == '__main__':
    unittest.main()
