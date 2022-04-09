import unittest

from offroad_routing import Geometry


class TestGeometry(unittest.TestCase):
    def test_geometry(self):
        filename = "../maps/user_area.osm.pbf"
        bbox = [34, 59, 34.2, 59.1]
        geom = Geometry.parse(filename=filename, bbox=bbox)
        geom.cut_bbox([34.01, 59.01, 34.19, 59.09], inplace=True)
        geom.simplify_roads(100, inplace=True)
        geom = geom.minimum_spanning_tree()
        geom = geom.select_road_type({'unclassified'}, exclude=True)
        geom.simplify_polygons(10, inplace=True)
        geom.to_networkx()
