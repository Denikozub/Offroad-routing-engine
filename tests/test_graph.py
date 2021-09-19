import unittest

from visibility.visibility_graph import VisibilityGraph


class TestGraph(unittest.TestCase):

    def test_graph_precompute(self):
        try:
            filename = "../maps/user_area.osm.pbf"
            bbox = [34, 59, 34.2, 59.1]
            vgraph = VisibilityGraph()
            vgraph.compute_geometry(bbox=bbox, filename=filename)
            vgraph.prune_geometry(epsilon_polygon=0.003,
                                  epsilon_linestring=0.001,
                                  bbox_comp=10,
                                  remove_inner=False)
        except Exception:
            self.fail()

    def test_graph_build(self):
        try:
            vgraph = VisibilityGraph()
            vgraph.load_geometry("../maps/user_area.h5")
            vgraph.build_graph(inside_percent=1,
                               multiprocessing=False,
                               graph=False,
                               map_plot=False)
        except Exception:
            self.fail()


if __name__ == '__main__':
    unittest.main()
