from pyrosm import OSM
from shapely.geometry import mapping, MultiPolygon, Polygon, MultiLineString
from geometry import dist, box_width, box_length, point_in_ch, inner_diag
from scipy.spatial import ConvexHull
from segment_visibility import SegmentVisibility
from find_pair import *
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import rdp


class VisibilityGraph:

    def __init__(self, filename, bbox):
        osm = OSM(filename, bounding_box=bbox)
        natural = osm.get_natural(extra_attributes=['nodes'])  # Additional attributes: natural.tags.unique()
        self.polygons = pd.DataFrame(natural.loc[:, ['natural', 'geometry']].loc[natural.geometry.type == 'Polygon'])
        self.multipolygons = pd.DataFrame(natural.loc[:, ['natural', 'geometry']].loc[natural.geometry.type == 'MultiPolygon'])
        self.multilinestrings = pd.DataFrame(natural.loc[:, ['natural', 'geometry']].loc[natural.geometry.type == 'MultiLineString']).head(0)
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
        coordinates = mapping(obj)['coordinates'][0]
        return coordinates if epsilon is None or epsilon <= 0 else rdp.rdp(coordinates, epsilon=epsilon)
    
    @staticmethod
    def __convex_hull(polygon):
        if len(polygon) <= 4:
            return polygon
        ch = ConvexHull(polygon)
        return ch.points[ch.vertices]
        # return mapping(Polygon(polygon).convex_hull)['coordinates'][0] if len(polygon) >= 5 else polygon

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
        if not ellipse:
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
    
    @staticmethod
    def __add_inside_poly(point_number, polygon, polygon_number):
        n = len(polygon) - 1
        edges_inside = list()
        for i in range(n):
            if i == point_number or not inner_diag(point_number, i, polygon, n):
                continue
            edges_inside.append((polygon[i], polygon_number, i))
        return edges_inside
    
    def incident_vertices(self, point_data, pair_func=find_pair_array, line_func=find_line_brute_force):
        point = point_data[0]
        point_polygon_number = point_data[1]
        point_polygon_point_number = point_data[2]
        visible_vertices = SegmentVisibility()
        polygon_count = self.polygons.shape[0]
        for i in range(polygon_count):
            polygon = self.polygons.iloc[i]
            if point_polygon_number is not None and i == point_polygon_number:
                line = line_func(point, polygon.geometry, i, point_polygon_point_number)
                if line is not None:
                    visible_vertices.add_line(line)
                # edges_inside = self.__add_inside_poly(point_polygon_point_number, polygon.geometry, i)
            elif not point_in_ch(point, polygon.convex_hull):
                pair = pair_func(point, polygon.convex_hull, i)
                if pair is not None:
                    visible_vertices.add_pair(pair)
            else:
                line = line_func(point, polygon.geometry, i)
                if line is not None:
                    visible_vertices.add_line(line)
        multilinestring_count = self.multilinestrings.shape[0]
        for i in range(multilinestring_count):
            visible_vertices.add_line(self.multilinestrings.geometry[i])
        visible_edges = visible_vertices.get_edges(point)
        # if point_polygon_number is not None:
            # visible_edges.extend(edges_inside)
        return visible_edges 

    def build_graph(self, plot=False, crs='EPSG:4326'):
        G = nx.Graph(crs=crs)
        max_poly_len = 10000  # for graph indexing
        if plot:
            fig = plt.figure()
        polygon_count = self.polygons.shape[0]
        for i in range(polygon_count):
            polygon = self.polygons.geometry[i]
            point_count = len(polygon) - 1
            for j in range(point_count):
                point = polygon[j]
                px, py = point
                point_data = (point, i, j)
                point_index = i * max_poly_len + j
                G.add_node(point_index, x=px, y=py)
                vertices = self.incident_vertices(point_data)
                if vertices is None:
                    continue
                for vertice in vertices:
                    vx, vy = vertice[0]
                    vertex_index = vertice[1] * max_poly_len + vertice[2]
                    G.add_node(vertex_index, x=vx, y=vy)
                    G.add_edge(point_index, vertex_index)
                    if plot:
                        plt.plot([px, vx], [py, vy])
        return G, fig if plot else G

