import unittest

from offroad_routing.visibility.inner_edges import find_inner_edges

polygon = (((1, 1), (7, 1), (4, 2), (6, 2), (6, 4), (8, 5), (2, 5), (4, 4), (1, 3), (4, 3), (1, 1)),)
point1 = (1, 1)
point2 = (7, 1)
point3 = (8, 5)
point4 = (6, 2)
point5 = (5, 3)
point6 = (3, 2)


class TestInnerEdges(unittest.TestCase):

    def test_point_1(self):
        edges = find_inner_edges(point1, 0, polygon, 0, 1, 0)
        self.assertEqual({point[0] for point in edges}, {(4, 2), (6, 4), (7, 1), (4, 3)})

    def test_point_2(self):
        edges = find_inner_edges(point2, 1, polygon, 0, 1, 0)
        self.assertEqual({point[0] for point in edges}, {(4, 2), (1, 1)})

    def test_point_3(self):
        edges = find_inner_edges(point3, 5, polygon, 0, 1, 0)
        self.assertEqual({point[0] for point in edges}, {(2, 5), (6, 4), (4, 4), (1, 3), (4, 3)})

    def test_point_4(self):
        edges = find_inner_edges(point4, 3, polygon, 0, 1, 0)
        self.assertEqual({point[0] for point in edges}, {(4, 2), (6, 4), (4, 4), (4, 3)})

    def test_point_5(self):
        edges = find_inner_edges(point5, None, polygon, 0, 1, 0)
        self.assertEqual({point[0] for point in edges}, {
                         (1, 1), (4, 2), (6, 2), (6, 4), (4, 4), (1, 3), (4, 3), (1, 1)})

    def test_point_6(self):
        edges = find_inner_edges(point6, None, polygon, 0, 1, 0)
        self.assertEqual({point[0] for point in edges}, {(1, 1), (7, 1), (4, 2), (6, 2), (6, 4), (4, 3)})

    def test_exception(self):
        with self.assertRaises(Exception):
            find_inner_edges((0, 0), None, ((0, 0),), 0, 1, 0)
        with self.assertRaises(Exception):
            find_inner_edges((0, 0), None, ((0, 0), (0, 0)), 0, 1, 0)
        with self.assertRaises(Exception):
            find_inner_edges((0, 0), None, ((0, 0), (1, 1), (2, 2)), 0, 1, 0)


if __name__ == '__main__':
    unittest.main()
