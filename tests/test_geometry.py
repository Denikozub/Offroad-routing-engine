import unittest

from offroad_routing import VisibilityGraph


class TestGeometry(unittest.TestCase):
    def test_geometry(self):
        vgraph = VisibilityGraph()
        vgraph.compute_geometry(
            bbox=[34, 59, 34.2, 59.1], filename="../maps/user_area.osm.pbf")
        vgraph.prune_geometry(epsilon_polygon=0.003, epsilon_polyline=0.001,
                              bbox_comp=10, remove_inner=True)
