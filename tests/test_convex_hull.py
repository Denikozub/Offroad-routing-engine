import unittest

from offroad_routing.osm_data.convex_hull import build_convex_hull

polygon0 = ((0, 0), (1, 1), (0, 0))
polygon1 = ((0, 0), (0, 1), (1, 1), (0, 0))
polygon2 = ((0, 0), (1, 1), (2, 0), (2, 3), (1, 2), (0, 3), (0, 0))


class TestConvexHull(unittest.TestCase):

    def test_incorrect(self):
        with self.assertRaises(Exception):
            build_convex_hull(polygon0[:-1])

    def test_simple(self):
        self.assertEqual(set(build_convex_hull(polygon0)[0]), set(polygon0))
        self.assertEqual(len(build_convex_hull(polygon0)[0]), len(polygon0))
        self.assertEqual(set(build_convex_hull(polygon0)[1]), {0, 1})
        self.assertIs(build_convex_hull(polygon0)[2], None)

    def test_convex(self):
        self.assertEqual(set(build_convex_hull(polygon1)[0]), set(polygon1))
        self.assertEqual(len(build_convex_hull(polygon1)[0]), len(polygon1))
        self.assertEqual(set(build_convex_hull(polygon1)[1]), {0, 1, 2})
        self.assertEqual(len(build_convex_hull(polygon1)[2]), len(polygon1) - 2)

    def test_non_convex(self):
        self.assertNotEqual(set(build_convex_hull(polygon2)[0]), set(polygon2))
        self.assertEqual(len(build_convex_hull(polygon2)[0]), len(polygon2) - 2)
        self.assertEqual(set(build_convex_hull(polygon2)[1]), {0, 2, 3, 5})
        self.assertEqual(len(build_convex_hull(polygon2)[2]), len(polygon2) - 2 - 2)

    def test_exception(self):
        with self.assertRaises(Exception):
            build_convex_hull(((0, 0),))
        with self.assertRaises(Exception):
            build_convex_hull(((0, 0), (0, 0)))
        with self.assertRaises(Exception):
            build_convex_hull(((0, 0), (1, 1), (2, 2)))


if __name__ == '__main__':
    unittest.main()
