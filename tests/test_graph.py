import unittest

from offroad_routing import Geometry
from offroad_routing import VisibilityGraph


class TestGraph(unittest.TestCase):
    def test_graph(self):
        geom = Geometry.load('user_area', '../maps')
        vgraph = VisibilityGraph(*geom.export(remove_inner=True))
        vgraph.build(inside_percent=1, multiprocessing=False)
