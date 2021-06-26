from parsers.osm_parser import OsmParser
from parsers.coord_filter import get_coordinates
from geometry.convex_hull import convex_hull
from pandas import DataFrame


class DfBuilder(OsmParser):

    def __init__(self):
        super().__init__()
    
    def build_dataframe(self, epsilon_polygon=None, epsilon_linestring=None, bbox_comp=15):
        """
        transform retrieved data:
            transform geometry to tuple of points
            run Ramer-Douglas-Peucker to geometry
            get rid of small objects with bbox_comp parameter
            add data about convex hull for polygons
        Default parameters will be computed for the given area to provide best performance.
        :param epsilon_polygon: None or Ramer-Douglas-Peucker algorithm parameter for polygons
        :param epsilon_linestring: None or Ramer-Douglas-Peucker algorithm parameter for multilinestrings
        :param bbox_comp: None or int or float - scale polygon comparison parameter (to size of map bbox)
        :return: None
        """

        for param in {epsilon_polygon, epsilon_linestring, bbox_comp}:
            if param is not None:

                if type(param) not in {float, int}:
                    raise TypeError("wrong ", str(param), " type")

                if param < 0:
                    raise ValueError("wrong ", str(param), " value")

        if epsilon_polygon is None:
            epsilon_polygon = (self.bbox_size[0] ** 2 + self.bbox_size[1] ** 2) ** 0.5 / bbox_comp / 5

        if epsilon_linestring is None:
            epsilon_linestring = (self.bbox_size[0] ** 2 + self.bbox_size[1] ** 2) ** 0.5 / bbox_comp / 10
        
        # polygon coordinates
        self.polygons.geometry = \
            self.polygons.geometry.apply(get_coordinates, args=[epsilon_polygon, bbox_comp, self.bbox_size, True])

        # delete None elements
        self.polygons = self.polygons[self.polygons['geometry'].notna()]
        self.polygons = self.polygons.reset_index().drop(columns='index')

        # add info about convex hull
        if (self.polygons.shape[0] > 0):
            self.polygons = self.polygons.join(DataFrame(self.polygons.geometry)
                                               .apply(lambda x: convex_hull(x[0][0]), axis=1, result_type='expand')
                                               .rename(columns={0: 'convex_hull', 1: 'convex_hull_points', 2: 'angles'}))

        # multilinestring coordinates
        self.multilinestrings.geometry = self.multilinestrings.geometry\
            .apply(get_coordinates, args=[epsilon_linestring, bbox_comp, self.bbox_size, False])

        # delete None elements
        self.multilinestrings = self.multilinestrings[self.multilinestrings['geometry'].notna()]
        self.multilinestrings = self.multilinestrings.reset_index().drop(columns='index')

