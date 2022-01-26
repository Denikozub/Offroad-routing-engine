import unittest

from offroad_routing import AStar
from offroad_routing import GpxTrack
from offroad_routing import VisibilityGraph


class TestAstar(unittest.TestCase):
    def test_astar(self):
        vgraph = VisibilityGraph()
        vgraph.load_geometry("../maps/user_area.npy")
        pathfinder = AStar(vgraph)
        path = pathfinder.find(
            (34.02, 59.01), (34.12, 59.09), default_weight=10, heuristic_multiplier=10)
        track = GpxTrack(path)
        track.visualize()
