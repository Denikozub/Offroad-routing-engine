from parsers.osm_parser import OsmParser
from parsers.coord_filter import get_coordinates
from geometry.convex_hull import convex_hull
from geometry.algorithm import compare_points
from pandas import DataFrame
from typing import Optional


class Pruner(OsmParser):

    def __init__(self):
        super().__init__()
    
    def prune(self, epsilon_polygon: Optional[float] = None, epsilon_linestring: Optional[float] = None,
              bbox_comp: Optional[int] = 15, remove_inner: bool = False) -> None:
        """
        Transform retrieved data:
            transform geometry to tuple of points
            run Ramer-Douglas-Peucker to geometry
            get rid of small objects with bbox_comp parameter
            add data about convex hull for polygons
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
        
        # polygon coordinates
        self.polygons.geometry = \
            self.polygons.geometry.apply(get_coordinates, args=[epsilon_polygon, bbox_comp, self.bbox_size, True])

        # delete None elements
        self.polygons = self.polygons[self.polygons['geometry'].notna()]
        self.polygons = self.polygons.reset_index().drop(columns='index')
        
        # delete inner polygons
        if remove_inner:
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

        # add info about convex hull
        if self.polygons.shape[0] > 0:
            self.polygons = self.polygons.join(DataFrame(self.polygons.geometry)
                                               .apply(lambda x: convex_hull(x[0][0]), axis=1, result_type='expand')
                                               .rename(columns={0: 'convex_hull', 1: 'convex_hull_points', 2: 'angles'}))

        # multilinestring coordinates
        self.multilinestrings.geometry = self.multilinestrings.geometry\
            .apply(get_coordinates, args=[epsilon_linestring, bbox_comp, self.bbox_size, False])

        # delete None elements
        self.multilinestrings = self.multilinestrings[self.multilinestrings['geometry'].notna()]
        self.multilinestrings = self.multilinestrings.reset_index().drop(columns='index')
