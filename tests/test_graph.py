import unittest

from offroad_routing import VisibilityGraph


class TestGraphBuild(unittest.TestCase):
    def test_inside_1(self):
        vgraph = VisibilityGraph()
        vgraph.load_geometry("../maps/user_area.npy")
        vgraph.build_graph(inside_percent=1, multiprocessing=False)

    def test_inside_0(self):
        vgraph = VisibilityGraph()
        vgraph.load_geometry("../maps/user_area.npy")
        vgraph.build_graph(inside_percent=0, multiprocessing=False)
