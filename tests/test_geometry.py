import unittest

from offroad_routing import VisibilityGraph


class TestGraphBuild(unittest.TestCase):
    def test_rm_inner(self):
        vgraph = VisibilityGraph()
        vgraph.compute_geometry(bbox=[34, 59, 34.2, 59.1], filename="../maps/user_area.osm.pbf")
        vgraph.prune_geometry(epsilon_polygon=0.003, epsilon_polyline=0.001,
                              bbox_comp=10, remove_inner=True)

    def test_leave_inner(self):
        vgraph = VisibilityGraph()
        vgraph.compute_geometry(bbox=[34.05, 59.03, 34.15, 59.07], filename="../maps/user_area.osm.pbf")
        vgraph.prune_geometry(epsilon_polygon=0.03, epsilon_polyline=0.01,
                              bbox_comp=None, remove_inner=False)
