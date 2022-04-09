import unittest

from offroad_routing import AStar
from offroad_routing import Geometry
from offroad_routing import GpxTrack
from offroad_routing import VisibilityGraph


class TestAstar(unittest.TestCase):
    def test_astar(self):
        geom = Geometry.load('user_area', '../maps')
        vgraph = VisibilityGraph(*geom.export(remove_inner=True))
        pathfinder = AStar(vgraph)
        path = pathfinder.find(
            (34.02, 59.01), (34.12, 59.09), default_surface='grass', heuristic_multiplier=10)
        track = GpxTrack(path)
        track.visualize()
