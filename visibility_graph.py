from pyrosm import OSM
from shapely.geometry import mapping, MultiPolygon, Polygon, MultiLineString
from geometry import dist, box_width, box_length
from scipy.spatial import ConvexHull
import pandas as pd
import numpy as np
import rdp


class VisibilityGraph:

    def __init__(self, filename, bbox):
        osm = OSM(filename, bounding_box=bbox)
        natural = osm.get_natural(extra_attributes=['nodes'])  # Additional attributes: natural.tags.unique()
        self.polygons = pd.DataFrame(natural.loc[:, ['natural', 'geometry']].loc[natural.geometry.type == 'Polygon'])
        self.multipolygons = pd.DataFrame(natural.loc[:, ['natural', 'geometry']].loc[natural.geometry.type == 'MultiPolygon'])
        self.multilinestrings = pd.DataFrame(natural.loc[:, ['natural', 'geometry']].loc[natural.geometry.type == 'MultiLineString'])
        self.bbox_width = box_width(bbox)
        self.bbox_height = box_length(bbox)

    def __compare_bounds(self, bounds, bbox_comp):
        return bbox_comp is None or self.bbox_width / box_width(bounds) <= bbox_comp and self.bbox_height / box_length(bounds) <= bbox_comp

    def __check_bounds(self, obj, bbox_comp, type_obj):
        bounds = Polygon(obj).bounds if type_obj == 'polygon' else MultiLineString(obj).bounds
        return self.__compare_bounds(bounds, bbox_comp)
        
    def __get_bounds(self, polygon, bbox_comp):
        bounds = polygon.bounds
        if not self.__compare_bounds(bounds, bbox_comp):
            return None
        min_x, min_y, max_x, max_y = bounds
        return ((min_x, min_y), (min_x, max_y), (max_x, max_y), (max_x, max_y))

    def __get_coord(self, obj, epsilon, bbox_comp, type_obj):
        if not self.__check_bounds(obj, bbox_comp, type_obj):
            return None
        return mapping(obj)['coordinates'][0] if epsilon is None or epsilon <= 0 else rdp.rdp(mapping(obj)['coordinates'][0], epsilon=epsilon)
    
    @staticmethod
    def __convex_hull(polygon):
        ch = ConvexHull(polygon)
        return ch.points[ch.vertices]

    def build_dataframe(self, epsilon=None, bbox_comp=None, ellipse=False):
        if ellipse:
            self.polygons.geometry = self.polygons.geometry.apply(self.__get_bounds, args=[bbox_comp])
        else:
            self.polygons.geometry = self.polygons.geometry.apply(self.__get_coord, args=[epsilon, bbox_comp, 'polygon'])

        for i in range(self.multipolygons.shape[0]):
            natural = self.multipolygons.natural.iloc[i]
            for polygon in MultiPolygon(self.multipolygons.geometry.iloc[i]).geoms:
                if ellipse:
                    self.polygons = self.polygons.append({'geometry': self.__get_bounds(polygon, bbox_comp),
                                                          'natural': natural}, ignore_index=True)
                else:
                    self.polygons = self.polygons.append({'geometry': self.__get_coord(polygon, epsilon, bbox_comp, 'polygon'),
                                                          'natural': natural}, ignore_index=True)
        self.polygons.dropna(inplace=True)
        self.polygons = self.polygons.reset_index().drop(columns='index')
        self.polygons['convex_hull'] = self.polygons.geometry.apply(self.__convex_hull)

        self.multilinestrings.geometry = self.multilinestrings.geometry.apply(self.__get_coord, args=[epsilon, bbox_comp, 'multilinestring'])
        self.multilinestrings.dropna(inplace=True)
        self.multilinestrings = self.multilinestrings.reset_index().drop(columns='index')
        if bbox_comp is None:
            return
        for i in range(self.multilinestrings.shape[0]):
            line_geometry = self.multilinestrings.geometry[i]
            point1 = line_geometry[0]
            new_line = list()
            new_line.append(point1)
            for j in range(len(line_geometry) - 1):
                point2 = line_geometry[j + 1]
                if dist(point1, point2) < min(self.bbox_width, self.bbox_height) / bbox_comp:
                    continue
                new_line.append(point2)
                point1 = point2
            self.multilinestrings.geometry[i] = new_line
    
    def incident_vertices(self, point, pair_func=find_pair_array, line_func=find_line_brute_force):
        visible_vertices = SegmentVisibility()
        polygon_count = self.polygons.shape[0]
        for i in range(polygon_count):
            polygon = polygons[i]
            if not point_in_ch(polygon.geometry):
                pair = ch_pair_func(point, polygon.convex_hull)
                if pair is not None:
                    visible_vertices.add_pair(pair)
            else:
                line = line_func(point, polygon.geometry)
                if line is not None:
                    visible_vertices.add_line(line)
        multilinestring_count = self.multilinestrings.shape[0]
        for i in range(multilinestring_count):
            visible_vertices.add_line(multilinestrings.geometry[i])
                
