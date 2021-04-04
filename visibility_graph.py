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
        return (min_x, min_y), (min_x, max_y), (max_x, max_y), (max_x, max_y)

    def __get_coord(self, obj, epsilon, bbox_comp, type_obj):
        if not self.__check_bounds(obj, bbox_comp, type_obj):
            return None
        coordinates = np.array(mapping(obj)['coordinates'][0])
        return coordinates if epsilon is None or epsilon <= 0 else rdp.rdp(coordinates, epsilon=epsilon)

    # method returns an array of coordinates of CH points and a list or their numbers in initial polygon
    @staticmethod
    def __convex_hull(polygon_df):
        polygon = polygon_df[0]
        if len(polygon) <= 4:
            return polygon, [i for i in range(len(polygon))]
        ch = ConvexHull(polygon)
        points = list(ch.vertices)
        points.append(points[0])
        vertices = ch.points[points]
        return vertices, points

    """
    epsilon is a parameter of Ramer-Douglas-Peucker algorithm
    bbox_comp is a scale object comparison parameter
    ellipse is a boolean parameter of ellipse approximation for speedup
    """
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
            self.polygons = self.polygons.join(pd.DataFrame(self.polygons.geometry).apply(self.__convex_hull, axis=1,
                    result_type='expand').rename(columns={0: 'convex_hull', 1: 'convex_hull_points'}))

        self.multilinestrings.geometry = self.multilinestrings.geometry.apply(self.__get_coord, args=[epsilon, bbox_comp, 'multilinestring'])
        self.multilinestrings.dropna(inplace=True)
        self.multilinestrings = self.multilinestrings.reset_index().drop(columns='index')
        if bbox_comp is None:
            return
        # bbox_comp length between linestring points comparison
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
            edges_inside.append((polygon[i], polygon_number, i, None, None))
        return edges_inside

    """
    point_data is a list where:
        0 element: point coordinates
        1 element: number of polygon where point belongs
        2 element: number of point in polygon
        3 element: number of linestring where point belongs
        4 element: number of point in linestring
    """
    def incident_vertices(self, point_data, pair_func=find_pair_array, line_func=find_line_brute_force):
        point = point_data[0]
        point_polygon_number = point_data[1]
        point_polygon_point_number = point_data[2]
        point_linestring_number = point_data[3]
        point_linestring_point_number = point_data[4]
        visible_vertices = SegmentVisibility()
        polygon_count = self.polygons.shape[0]
        edges_inside = list()
        for i in range(polygon_count):
            polygon = self.polygons.iloc[i]
            if point_polygon_number is not None and i == point_polygon_number:
                edges_inside = self.__add_inside_poly(point_polygon_point_number, polygon.geometry, i)
                convex_hull_point_count = len(polygon.convex_hull) - 1
                if convex_hull_point_count <= 2:
                    continue
                if point_polygon_point_number in polygon.convex_hull_points:  # point is a part of CH
                    position = polygon.convex_hull_points.index(point_polygon_point_number)
                    left = polygon.convex_hull_points[(position - 1) % convex_hull_point_count]
                    right = polygon.convex_hull_points[(position + 1) % convex_hull_point_count]
                    restriction_pair = (polygon.geometry[left], polygon.geometry[right])
                    visible_vertices.set_restriction_angle(restriction_pair, point, True)
                else:
                    restriction_pair = line_func(point, polygon.geometry, i, point_polygon_point_number)
                    visible_vertices.set_restriction_angle(restriction_pair, point, False)
            elif not point_in_ch(point, polygon.convex_hull):  # point inside CH
                pair = pair_func(point, polygon.convex_hull, i)
                visible_vertices.add_pair(pair)
            else:
                line = line_func(point, polygon.geometry, i)
                visible_vertices.add_line(line)
        multilinestring_count = self.multilinestrings.shape[0]
        for i in range(multilinestring_count):
            linestring = self.multilinestrings.geometry[i]
            linestring_point_count = len(linestring)
            if point_linestring_number is not None and i == point_linestring_number:
                if point_linestring_point_number > 0:
                    previous = point_linestring_point_number - 1
                    edges_inside.append((linestring[previous], None, None, i, previous))
                if point_linestring_point_number + 1 < linestring_point_count:
                    following = point_linestring_point_number + 1
                    edges_inside.append((linestring[following], None, None, i, following))
            line = list()
            for j in range(linestring_point_count):
                line.append((linestring[j], None, None, i, j))
            visible_vertices.add_line(line)
        visible_edges = visible_vertices.get_edges(point)
<<<<<<< HEAD
        visible_edges.extend(edges_inside)
=======
        if point_linestring_number is not None and point_polygon_number is not None:
            visible_edges.extend(edges_inside)
>>>>>>> 70a3b1178d29b62afd9b50a07971491e14353853
        return visible_edges 

    def __process_points_of_objects(self, obj_type, G, plot):
        max_poly_len = 10000                    # for graph indexing
        object_count = self.polygons.shape[0] if obj_type == 'polygon' else self.multilinestrings.shape[0]
        for i in range(object_count):
            obj = self.polygons.geometry[i] if obj_type == 'polygon' else self.multilinestrings.geometry[i]
            point_count = len(obj) - 1 if obj_type == 'polygon' else len(obj)
            for j in range(point_count):
                point = obj[j]
                px, py = point
                point_data = (point, i, j, None, None) if obj_type == 'polygon' else (point, None, None, i, j)
                point_index = i * max_poly_len + j if obj_type == 'polygon' else (i + 0.5) * max_poly_len + j
                G.add_node(point_index, x=px, y=py)
                vertices = self.incident_vertices(point_data)
                if vertices is None:
                    continue
                for vertex in vertices:
                    vx, vy = vertex[0]         # x and y coordinates of vertex
                    if vertex[1] is not None:  # vertex belongs to a polygon
                        vertex_index = vertex[1] * max_poly_len + vertex[2]
                    else:                       # vertex belongs to a linestring
                        vertex_index = (vertex[3] + 0.5) * max_poly_len + vertex[4]
                    G.add_node(vertex_index, x=vx, y=vy)
                    G.add_edge(point_index, vertex_index)
                    if plot:
                        plt.plot([px, vx], [py, vy])

    def build_graph(self, plot=False, crs='EPSG:4326'):
        G = nx.Graph(crs=crs)
        if plot:
            fig = plt.figure()
        self.__process_points_of_objects('polygon', G, plot)
        self.__process_points_of_objects('multilinestring', G, plot)
        return G, fig if plot else G
