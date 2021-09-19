from typing import Optional

from pandas import DataFrame

from offroad_routing.geometry.algorithms import compare_points
from offroad_routing.geometry.convex_hull import build_convex_hull
from offroad_routing.osm_data.coord_filter import get_coordinates
from offroad_routing.osm_data.parser import OsmParser


class Pruner(OsmParser):

    def __init__(self):
        super().__init__()

    def __remove_inner_polygons(self):
        polygon_number = self.polygons.shape[0]
        for i in range(polygon_number):
            if self.polygons.geometry.iloc[i] is None:
                continue
            self.polygons.tag.iloc[i] = [self.polygons.tag.iloc[i]]
            polygon = self.polygons.geometry.iloc[i]
            for j in range(1, len(polygon)):
                point = polygon[j][0]
                for k in range(i + 1, polygon_number):
                    if self.polygons.geometry.iloc[k] is None:
                        if k == polygon_number - 1:
                            self.polygons.tag.iloc[i].append(None)
                        continue
                    new_point = self.polygons.geometry.iloc[k][0][0]
                    if compare_points(point, new_point):
                        self.polygons.tag.iloc[i].append(self.polygons.tag.iloc[k])
                        self.polygons.geometry.iloc[k] = None
                    elif k == polygon_number - 1:
                        self.polygons.tag.iloc[i].append(None)
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

    def prune_geometry(self, epsilon_polygon: Optional[float] = None, epsilon_linestring: Optional[float] = None,
                       bbox_comp: Optional[int] = 15, remove_inner: bool = False) -> None:
        """
        Transform retrieved data:
        transform geometry to tuple of points,
        run Ramer-Douglas-Peucker to geometry,
        get rid of small objects with bbox_comp parameter,
        add data about convex hull for polygons.
        Default parameters will be computed for the given area to provide best performance.

        :param epsilon_polygon: Ramer-Douglas-Peucker algorithm parameter for polygons
        :param epsilon_linestring: Ramer-Douglas-Peucker algorithm parameter for multilinestrings
        :param bbox_comp: scale polygon comparison parameter (to size of map bbox)
        :param remove_inner: inner polygons for other polygons should be removed (True) or not (False)
        """

        for param in {epsilon_polygon, epsilon_linestring, bbox_comp}:
            assert param is None or param >= 0

        if epsilon_polygon is None:
            epsilon_polygon = (self.bbox_size[0] ** 2 + self.bbox_size[1] ** 2) ** 0.5 / bbox_comp / 5

        if epsilon_linestring is None:
            epsilon_linestring = (self.bbox_size[0] ** 2 + self.bbox_size[1] ** 2) ** 0.5 / bbox_comp / 10

        self.polygons.geometry = \
            self.polygons.geometry.apply(get_coordinates, args=[epsilon_polygon, bbox_comp, self.bbox_size, True])

        self.polygons = self.polygons[self.polygons['geometry'].notna()]
        self.__remove_equal_polygons()
        self.polygons = self.polygons.reset_index().drop(columns='index')

        if remove_inner:
            self.__remove_inner_polygons()

        # add info about convex hull
        if self.polygons.shape[0] > 0:
            self.polygons = self.polygons.join(DataFrame(self.polygons.geometry)
                                               .apply(lambda x: build_convex_hull(x[0][0]), axis=1, result_type='expand')
                                               .rename(columns={0: 'convex_hull', 1: 'convex_hull_points', 2: 'angles'}))

        self.multilinestrings.geometry = self.multilinestrings.geometry\
            .apply(get_coordinates, args=[epsilon_linestring, bbox_comp, self.bbox_size, False])

        self.multilinestrings = self.multilinestrings[self.multilinestrings['geometry'].notna()]
        self.multilinestrings = self.multilinestrings.reset_index().drop(columns='index')
