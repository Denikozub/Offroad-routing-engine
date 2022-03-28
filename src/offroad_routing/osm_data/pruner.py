from math import fabs

from offroad_routing.geometry.algorithms import compare_points
from offroad_routing.geometry.convex_hull import build_convex_hull
from offroad_routing.osm_data.parser import OsmParser
from pandas import DataFrame
from rdp import rdp
from shapely.geometry import mapping


class Pruner(OsmParser):

    def __init__(self):
        super().__init__()

    def __remove_inner_polygons(self):
        polygon_number = self.polygons.shape[0]
        for i in range(polygon_number):
            if self.polygons.loc[i, "geometry"] is None:
                continue
            polygon = self.polygons.loc[i, "geometry"]
            for j in range(1, len(polygon)):
                point = polygon[j][0]
                for k in range(i + 1, polygon_number):
                    if self.polygons.loc[k, "geometry"] is None:
                        if k == polygon_number - 1:
                            self.polygons.loc[i, "tag"].append(None)
                        continue
                    new_point = self.polygons.loc[k, "geometry"][0][0]
                    if compare_points(point, new_point):
                        self.polygons.loc[i, "tag"].append(
                            self.polygons.loc[k, "tag"])
                        self.polygons.loc[k, "geometry"] = None
                    elif k == polygon_number - 1:
                        self.polygons.loc[i, "tag"].append(None)
        self.polygons = self.polygons[self.polygons['geometry'].notna()]
        self.polygons = self.polygons.reset_index().drop(columns='index')

    @staticmethod
    def __compare_polygons(p1, p2):
        outer1, outer2 = p1[0], p2[0]
        return outer1 == outer2 or outer1 == tuple(reversed(outer2))

    def __remove_equal_polygons(self):
        to_delete = list()
        for p1 in self.polygons.geometry:
            for p2 in self.polygons.geometry:
                if (p1 is not p2) and self.__compare_polygons(p1, p2) and p1 not in to_delete and p2 not in to_delete:
                    to_delete.append(p2)
        self.polygons = self.polygons[~self.polygons.geometry.isin(to_delete)]

    @staticmethod
    def __compare_bbox(obj, bbox_comp, bbox_size):
        if bbox_comp is not None:
            bounds = obj.bounds
            bounds_size = (fabs(bounds[2] - bounds[0]),
                           fabs(bounds[3] - bounds[1]))
            if bounds_size[0] == 0 or bounds_size[1] == 0:
                return None
            if bbox_size[0] / bounds_size[0] >= bbox_comp and bbox_size[1] / bounds_size[1] >= bbox_comp:
                return None
        return obj

    @staticmethod
    def __polygon_coords(polygon, epsilon):
        if polygon is None:
            return None
        coordinates = mapping(polygon)['coordinates']
        polygons = list()
        for polygon in coordinates:
            polygons.append(tuple([tuple(point) for point in polygon] if epsilon is None or epsilon == 0 else
                                  [tuple(point) for point in rdp(polygon, epsilon=epsilon)]))
        return tuple(polygons) if len(polygons[0]) >= 3 else None

    @staticmethod
    def __linestring_coords(linestring, epsilon):
        if linestring is None:
            return None
        coordinates = mapping(linestring)['coordinates']
        points = [pair[0] for pair in coordinates]
        points.append(coordinates[-1][1])
        return tuple(tuple(point) for point in points) if epsilon is None or epsilon == 0 else \
            tuple(tuple(point) for point in rdp(points, epsilon=epsilon))

    def prune_geometry(self, epsilon_polygon=None, epsilon_polyline=None, bbox_comp=15, *, remove_inner=False):
        """
        Transform retrieved map data:

        1. Transform geometry to tuple of points.
        2. Run Ramer-Douglas-Peucker (RDP) to geometry.
        3. Get rid of small objects with bbox_comp parameter.
        4. Add data about convex hull for polygons.

        Default RDP parameters will be computed for the given area to provide best performance.

        :param Optional[float] epsilon_polygon: RDP parameter for polygons
        :param Optional[float] epsilon_polyline: RDP parameter for polylines
        :param Optional[int] bbox_comp: scale polygon comparison parameter (to size of map bbox)
        :param bool remove_inner: remove inner polygons for other polygons
        """

        for param in {epsilon_polygon, epsilon_polyline, bbox_comp}:
            assert param is None or param >= 0

        # auto-compute parameters
        if epsilon_polygon is None:
            epsilon_polygon = (
                self.bbox_size[0] ** 2 + self.bbox_size[1] ** 2) ** 0.5 / bbox_comp / 5

        if epsilon_polyline is None:
            epsilon_polyline = (
                self.bbox_size[0] ** 2 + self.bbox_size[1] ** 2) ** 0.5 / bbox_comp / 10

        # compare to bounding box
        self.polygons.geometry = \
            self.polygons.geometry.apply(self.__compare_bbox, args=[
                                         bbox_comp, self.bbox_size])
        self.polygons = DataFrame(
            self.polygons[self.polygons['geometry'].notna()])

        # shapely.geometry.Polygon to tuple of points
        self.polygons.geometry = self.polygons.geometry.apply(
            self.__polygon_coords, args=[epsilon_polygon])
        self.polygons = self.polygons[self.polygons['geometry'].notna()]

        # remove equal polygons
        self.__remove_equal_polygons()
        self.polygons = self.polygons.reset_index().drop(columns='index')

        # remove polygons which are inner for other polygons
        if remove_inner:
            self.__remove_inner_polygons()

        # add info about convex hull
        if self.polygons.shape[0] > 0:
            self.polygons = self.polygons.join(DataFrame(self.polygons.geometry)
                                               .apply(lambda x: build_convex_hull(x[0][0]), axis=1,
                                                      result_type='expand')
                                               .rename(
                columns={0: 'convex_hull', 1: 'convex_hull_points', 2: 'angles'}))

        # compare to bounding box
        self.multilinestrings.geometry = \
            self.multilinestrings.geometry.apply(self.__compare_bbox, args=[
                                                 bbox_comp, self.bbox_size])
        self.multilinestrings = DataFrame(self.multilinestrings[self.multilinestrings['geometry'].notna()]
                                          .reset_index().drop(columns='index'))

        # shapely.geometry.MultiLineString to tuple of points and simplify
        self.multilinestrings.geometry = self.multilinestrings.geometry.apply(self.__linestring_coords,
                                                                              args=[epsilon_polyline])

        self.multilinestrings = self.multilinestrings.to_records(index=False)
        self.polygons = self.polygons.to_records(index=False)
