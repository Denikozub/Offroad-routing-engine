from parsers.get_coord import get_coordinates
from geometry.convex_hull import convex_hull
from pandas import DataFrame, HDFStore
from math import fabs


class OsmParser:

    def __init__(self):
        self.polygons = None
        self.multilinestrings = None
        self.multipolygons = None
        self.bbox_size = None

    def compute_geometry(self, filename, bbox):
        """
        parse OSM file area in bbox to retrieve information about roads and surface
        :param filename: .osm.pbf format
        :param bbox: None of in format min_lon, min_lat, max_lon, max_lat
        :return: None
        """

        if type(filename) != str:
            raise TypeError("wrong filename type")

        iter(bbox)

        from pyrosm import OSM

        # parsing OMS map with pyrosm
        osm = OSM(filename, bounding_box=bbox)
        natural = osm.get_natural()  # Additional attributes: natural.tags.unique()
        natural = natural.loc[:, ['natural', 'geometry']]

        # splitting polygon and linestring data
        self.polygons = DataFrame(natural.loc[natural.geometry.type == 'Polygon'])
        self.multipolygons = DataFrame(natural.loc[natural.geometry.type == 'MultiPolygon'])
        self.multilinestrings = DataFrame(natural.loc[natural.geometry.type == 'MultiLineString']) \
            .rename(columns={'natural': 'surface'})
        natural.drop(natural.index, inplace=True)

        # getting road network data with pyrosm
        roads = osm.get_network()
        if roads is not None:
            roads = DataFrame(roads.loc[:, ['surface', 'geometry']].loc[roads.geometry.type == 'MultiLineString'])
            self.multilinestrings = self.multilinestrings.append(roads)
        roads.drop(roads.index, inplace=True)

        # bounding box size
        self.bbox_size = None if bbox is None else (fabs(bbox[2] - bbox[0]), fabs(bbox[3] - bbox[1]))

    def build_dataframe(self, epsilon_polygon=None, epsilon_linestring=None, bbox_comp=20):
        """
        transform retrieved data:
            transform geometry to tuple of points
            run Ramer-Douglas-Peucker to geometry
            get rid of small polygons with bbox_comp parameter
            add data about convex hull for polygons
        :param epsilon_polygon: None or Ramer-Douglas-Peucker algorithm parameter for polygons
        :param epsilon_linestring: None or Ramer-Douglas-Peucker algorithm parameter for linestrings
        :param bbox_comp: bbox_comp: None or int or float - scale polygon comparison parameter (to size of map bbox)
        :return: None
        """

        for param in {epsilon_polygon, epsilon_linestring, bbox_comp}:
            if param is not None:

                if type(param) not in {float, int}:
                    raise TypeError("wrong ", str(param), " type")

                if param < 0:
                    raise ValueError("wrong ", str(param), " value")

        if epsilon_polygon is None:
            epsilon_polygon = (self.bbox_size[0] ** 2 + self.bbox_size[1] ** 2) ** 0.5 / bbox_comp / 4

        if epsilon_linestring is None:
            epsilon_linestring = (self.bbox_size[0] ** 2 + self.bbox_size[1] ** 2) ** 0.5 / bbox_comp / 8

        # polygon coordinates
        self.polygons.geometry = \
            self.polygons.geometry.apply(get_coordinates, args=[epsilon_polygon, bbox_comp, self.bbox_size, True])

        # multipolygon coordinates
        for i in range(self.multipolygons.shape[0]):
            natural = self.multipolygons.natural.iloc[i]
            for polygon in self.multipolygons.geometry.iloc[i].geoms:
                self.polygons = self.polygons.append({'geometry': get_coordinates(polygon, epsilon_polygon,
                                                                                  bbox_comp, self.bbox_size, True),
                                                      'natural': natural}, ignore_index=True)
        self.multipolygons.drop(self.multipolygons.index, inplace=True)

        # delete None elements
        self.polygons = self.polygons[self.polygons['geometry'].notna()]
        self.polygons = self.polygons.reset_index().drop(columns='index')

        # add info about convex hull
        self.polygons = self.polygons.join(DataFrame(self.polygons.geometry)
                                           .apply(lambda x: convex_hull(x[0]), axis=1, result_type='expand')
                                           .rename(columns={0: 'convex_hull', 1: 'convex_hull_points', 2: 'angles'}))

        # linestring coordinates
        self.multilinestrings.geometry = self.multilinestrings.geometry\
            .apply(get_coordinates, args=[epsilon_linestring, bbox_comp, self.bbox_size, False])

        # delete None elements
        self.multilinestrings = self.multilinestrings[self.multilinestrings['geometry'].notna()]
        self.multilinestrings = self.multilinestrings.reset_index().drop(columns='index')

    def save_geometry(self, filename):
        """
        save computed data to filename
        :param filename: standard filename requirements
        :return: None
        """

        if type(filename) != str:
            raise TypeError("wrong filename type")

        store = HDFStore(filename)
        store["polygons"] = self.polygons
        store["multilinestrings"] = self.multilinestrings

    def load_geometry(self, filename):
        """
        load saved data from filename
        :param filename: standard filename requirements
        :return: None
        """

        if type(filename) != str:
            raise TypeError("wrong filename type")

        store = HDFStore(filename)
        self.polygons = store["polygons"]
        self.multilinestrings = store["multilinestrings"]
