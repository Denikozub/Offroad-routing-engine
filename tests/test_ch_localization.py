import unittest

from offroad_routing.geometry.ch_localization import *
from offroad_routing.osm_data.convex_hull import build_convex_hull


polygon1 = ((0, 0), (1, -1), (3, -1), (6, 1), (5, 3), (1, 3), (0, 0))
polygon1, _, angles1 = build_convex_hull(polygon1)
polygon2 = ((-1, -1), (6, -1), (6, 6), (-1, -1))
polygon2, _, angles2 = build_convex_hull(polygon2)
points_in = ((2, 1), (5, 1), (1, 0), (2, 0), (3, 0),
             (4, 0), (3, 1), (4, 1), (3, 2), (4, 2), (5, 2))
points_out = ((-1, 2), (3, 4), (5, -5), (10, -1), (-5, -5))
points_on = ((2, -1), (3, 3))


class TestLocalizeConvexLinear(unittest.TestCase):
    def test_polygon1(self):
        for p in points_in:
            self.assertTrue(localize_convex_linear(p, polygon1))
        for p in points_out:
            self.assertFalse(localize_convex_linear(p, polygon1))
        for p in points_on:
            self.assertFalse(localize_convex_linear(p, polygon1))

    def test_polygon2(self):
        for p in points_in:
            self.assertTrue(localize_convex_linear(p, polygon2))
        for p in points_out:
            self.assertFalse(localize_convex_linear(p, polygon2))
        for p in points_on:
            self.assertFalse(localize_convex_linear(p, polygon2))

    def test_exception(self):
        with self.assertRaises(Exception):
            localize_convex_linear((0, 0), ((0, 0),))
        with self.assertRaises(Exception):
            localize_convex_linear((0, 0), ((0, 0), (0, 0)))
        with self.assertRaises(Exception):
            localize_convex_linear((0, 0), ((0, 0), (1, 1), (2, 2)))


class TestLocalizeConvex(unittest.TestCase):
    def test_polygon1(self):
        for p in points_in:
            self.assertTrue(localize_convex(p, polygon1, angles1)[0])
        for p in points_out:
            self.assertFalse(localize_convex(p, polygon1, angles1)[0])
        for p in points_on:
            self.assertFalse(localize_convex(p, polygon1, angles1)[0])

    def test_polygon2(self):
        for p in points_in:
            self.assertTrue(localize_convex(p, polygon2, angles2)[0])
        for p in points_out:
            self.assertFalse(localize_convex(p, polygon2, angles2)[0])
        for p in points_on:
            self.assertFalse(localize_convex(p, polygon2, angles2)[0])

    def test_exception(self):
        with self.assertRaises(Exception):
            localize_convex((0, 0), ((0, 0),), None)
        with self.assertRaises(Exception):
            localize_convex((0, 0), ((0, 0), (0, 0)), None)
        with self.assertRaises(Exception):
            localize_convex((0, 0), ((0, 0), (1, 1), (2, 2)), None)
        with self.assertRaises(Exception):
            localize_convex(
                (0, 0), ((0, 0), (0, 1), (1, 1), (1, 0), (0, 0)), None)


if __name__ == '__main__':
    unittest.main()
