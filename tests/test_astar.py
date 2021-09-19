import unittest
from os import remove

from offroad_routing.visibility.visibility_graph import VisibilityGraph
from offroad_routing.pathfinding.astar import AStar
from offroad_routing.pathfinding.gpx_track import GpxTrack


class TestAstar(unittest.TestCase):

    def test_astar(self):
        try:
            vgraph = VisibilityGraph()
            vgraph.load_geometry("../maps/user_area.h5")
            pathfinder = AStar(vgraph)
            path = pathfinder.find((34.02, 59.01), (34.12, 59.09), default_weight=10, heuristic_multiplier=10)
            self.assertTrue(path.path())
            track = GpxTrack(path)
            track.write_file("track.gpx")
            remove("track.gpx")
            track.visualize()
        except Exception:
            self.fail()


if __name__ == '__main__':
    unittest.main()
