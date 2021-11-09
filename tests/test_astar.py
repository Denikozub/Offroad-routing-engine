import unittest

from offroad_routing import VisibilityGraph, AStar, GpxTrack


class TestGraphBuild(unittest.TestCase):
    def test_astar_1(self):
        vgraph = VisibilityGraph()
        vgraph.load_geometry("../maps/user_area.npy")
        pathfinder = AStar(vgraph)
        path = pathfinder.find((34.02, 59.01), (34.12, 59.09), default_weight=10, heuristic_multiplier=10)
        track = GpxTrack(path)
        track.visualize()

    def test_astar_2(self):
        vgraph = VisibilityGraph()
        vgraph.load_geometry("../maps/user_area.npy")
        pathfinder = AStar(vgraph)
        path = pathfinder.find((39, 88), (12, 64), default_weight=1, heuristic_multiplier=1)
        track = GpxTrack(path)
        track.visualize()
