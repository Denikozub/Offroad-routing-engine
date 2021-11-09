import unittest

from offroad_routing import VisibilityGraph


class TestGraph(unittest.TestCase):
    def test_graph(self):
        vgraph = VisibilityGraph()
        vgraph.load_geometry("maps/user_area.npy")
        vgraph.build_graph(inside_percent=1, multiprocessing=False)
