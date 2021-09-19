import unittest

from offroad_routing.geometry.ch_localization import *
from offroad_routing.geometry.convex_hull import build_convex_hull


polygon = ((0, 0), (1, -1), (3, -1), (6, 1), (5, 3), (1, 3), (0, 0))
ch, _, angles = build_convex_hull(polygon)
p1 = (2, 1)
p2 = (5, 1)
p3 = (-1, 2)
p4 = (3, 4)
p5 = (2, -1)
p6 = (3, 3)


class TestLocalizeConvexLinear(unittest.TestCase):
    def test_in(self):
        self.assertTrue(localize_convex_linear(p1, polygon))
        self.assertTrue(localize_convex_linear(p2, polygon))

    def test_out(self):
        self.assertFalse(localize_convex_linear(p3, polygon))
        self.assertFalse(localize_convex_linear(p4, polygon))

    def test_border(self):
        self.assertFalse(localize_convex_linear(p5, polygon))
        self.assertFalse(localize_convex_linear(p6, polygon))


class TestLocalizeConvex(unittest.TestCase):
    def test_in(self):
        self.assertTrue(localize_convex(p1, ch, angles)[0])
        self.assertTrue(localize_convex(p2, ch, angles)[0])

    def test_out(self):
        self.assertFalse(localize_convex(p3, ch, angles)[0])
        self.assertFalse(localize_convex(p4, ch, angles)[0])

    def test_border(self):
        self.assertFalse(localize_convex(p5, ch, angles)[0])
        self.assertFalse(localize_convex(p6, ch, angles)[0])


if __name__ == '__main__':
    unittest.main()
