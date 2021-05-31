from pyrosm import OSM
from shapely.geometry import mapping, MultiPolygon, Polygon, MultiLineString, LineString, Point
from geometry.geometry import point_in_ch, angle
from scipy.spatial import ConvexHull
from segment_visibility import SegmentVisibility
from math import fabs
from geometry.supporting_non_convex import find_line_brute_force
from numpy import array, arange
from numpy.random import choice
from networkx import Graph
import matplotlib.pyplot as plt
import pandas as pd
import rdp


class VisibilityGraph:

    def __init__(self, filename, bbox):

        # parsing OMS map with pyrosm
        osm = OSM(filename, bounding_box=bbox)
        natural = osm.get_natural()  # Additional attributes: natural.tags.unique()
        natural = natural.loc[:, ['natural', 'geometry']]

        # splitting polygon and linestring data
        self.polygons = pd.DataFrame(natural.loc[natural.geometry.type == 'Polygon'])
        self.multipolygons = pd.DataFrame(natural.loc[natural.geometry.type == 'MultiPolygon'])
        self.multilinestrings = pd.DataFrame(natural.loc[natural.geometry.type == 'MultiLineString']).rename(columns={'natural' : 'surface'})

        # getting road network data with pyrosm
        roads = osm.get_network()
        if roads is not None:
            roads = pd.DataFrame(roads.loc[:, ['surface', 'geometry']].loc[roads.geometry.type == 'MultiLineString'])
            self.multilinestrings = self.multilinestrings.append(roads)

        # bounding box size
        self.bbox_size = None if bbox is None else (fabs(bbox[2] - bbox[0]), fabs(bbox[3] - bbox[1]))

    def __get_coord(self, obj, epsilon, bbox_comp, is_polygon):

        # getting object bbox with shapely
        bounds = Polygon(obj).bounds if is_polygon else MultiLineString(obj).bounds
        bounds_size = (fabs(bounds[2] - bounds[0]), fabs(bounds[3] - bounds[1]))

        # if object is point-like or segment-like
        if bounds_size[0] == 0 or bounds_size[1] == 0:
            return None

        # comparing object sizes
        if bbox_comp is not None and self.bbox_size[0] / bounds_size[0] >= bbox_comp and \
                self.bbox_size[1] / bounds_size[1] >= bbox_comp:
            return None

        # extracting coordinates from GeoPandas.GeoDataFrame
        if is_polygon:
            coordinates = mapping(obj)['coordinates'][0]
        else:
            coordinates = mapping(obj)['coordinates']
            points = [pair[0] for pair in coordinates]
            points.append(coordinates[-1][1])
            coordinates = points
        return [tuple(point) for point in coordinates] if epsilon is None or epsilon <= 0 else [tuple(point) for point in rdp.rdp(coordinates, epsilon=epsilon)]

    # method returns an array of coordinates of CH points and a list or their numbers in initial polygon
    @staticmethod
    def __convex_hull(polygon_df):
        polygon = polygon_df[0]

        # polygon is a segment or a point
        if len(polygon) <= 4:
            starting_point = polygon[0]
            angles = [angle(starting_point, vertice) for vertice in polygon]
            angles.pop(0)
            angles.pop()
            return polygon, [i for i in range(len(polygon) - 1)], angles

        # getting convex hull with scipy
        ch = ConvexHull(polygon)
        points = list(ch.vertices)
        points.append(points[0])
        vertices = ch.points[points]
        vertices = [tuple(point) for point in vertices]
        points.pop()
        
        # calculating angles for O(n log n) algorithm
        starting_point = vertices[0]
        angles = [angle(starting_point, vertice) for vertice in vertices]
        angles.pop(0)
        angles.pop()
        return vertices, points, angles

    """
    epsilon is a parameter of Ramer-Douglas-Peucker algorithm
    bbox_comp is a scale object comparison parameter
    length_comp is a scale linestring comparison parameter
    """
    def build_dataframe(self, epsilon=None, bbox_comp=None, length_comp=None):
    
        for param in {epsilon, bbox_comp, length_comp}:
            if param is not None:
            
                if type(param) not in {float, int}:
                    raise TypeError("wrong ", str(param), " type")
                
                if param < 0:
                    raise ValueError("wrong ", str(param), " value")

        # polygon coordinates
        self.polygons.geometry = self.polygons.geometry.apply(self.__get_coord, args=[epsilon, bbox_comp, True])

        # multipolygon coordinates
        for i in range(self.multipolygons.shape[0]):
            natural = self.multipolygons.natural.iloc[i]
            for polygon in MultiPolygon(self.multipolygons.geometry.iloc[i]).geoms:
                self.polygons = self.polygons.append({'geometry': self.__get_coord(polygon, epsilon, bbox_comp, True),
                                                      'natural': natural}, ignore_index=True)

        # free multipolugon memory
        self.multipolygons = self.multipolygons.iloc[0:0]

        # delete None elements
        self.polygons = self.polygons[self.polygons['geometry'].notna()]
        self.polygons = self.polygons.reset_index().drop(columns='index')

        # add info about convex hull
        self.polygons = self.polygons.join(pd.DataFrame(self.polygons.geometry).apply(self.__convex_hull, axis=1,
                result_type='expand').rename(columns={0: 'convex_hull', 1: 'convex_hull_points', 2: 'angles'}))

        # linestring coordinates
        self.multilinestrings.geometry = self.multilinestrings.geometry.apply(self.__get_coord, args=[epsilon, bbox_comp, False])

        # delete None elements
        self.multilinestrings = self.multilinestrings[self.multilinestrings['geometry'].notna()]
        self.multilinestrings = self.multilinestrings.reset_index().drop(columns='index')

        # length_comp length between linestring points comparison
        if length_comp is None:
            return
        for i in range(self.multilinestrings.shape[0]):
            line_geometry = self.multilinestrings.geometry[i]
            point1 = line_geometry[0]
            new_line = list()
            new_line.append(point1)
            for j in range(len(line_geometry) - 1):
                point2 = line_geometry[j + 1]
                if ((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)**0.5 < min(self.bbox_size[0], self.bbox_size[1]) / length_comp:
                    continue
                new_line.append(point2)
                point1 = point2
            self.multilinestrings.geometry[i] = new_line

    @staticmethod
    def __add_inside_poly(point, point_number, polygon, polygon_number, inside_percent):
        n = len(polygon) - 1
        edges_inside = list()

        # polygon is a segment or a point
        if n < 2:
            return edges_inside
        for i in range(n):

            # check if a segment is inner with shapely
            if (point_number is not None and i != point_number and (fabs(point_number - i) in (0, 1, n-1)) or \
                    (Polygon(polygon).contains(LineString([point, polygon[i]])))):

                # randomly choose diagonals to add with percentage
                if inside_percent == 1 or choice(arange(0, 2), p=[1-inside_percent, inside_percent]) == 1:
                    edges_inside.append((polygon[i], polygon_number, i, True, 1))

                # we should not add fully outer segments because they may intersect other polygons!!!!!

        return edges_inside

    """
    point_data is a tuple where:
        0 element: point coordinates
        1 element: number of object where point belongs
        2 element: number of point in object
        3 element: if object is polygon or linestring
        4 element: surface type
    pair_func is a function that takes point, polygon, polygon_number as arguments and returns a tuple (point_data, point_data) representing supporting points
    seg_func is a string parameter ("brute" or "sweep") which sets a function to be used for building graph of segments
    add_edges_inside is a bool parameter which indicates whether inside edges should be added
    inside_percent is a float parameter setting the probability of an inner edge to be added (from 0 to 1)
    """
    def incident_vertices(self, point_data, pair_func, seg_func="sweep", add_edges_inside=True, inside_percent=1):
        
        iter(point_data)
        
        if len(point_data) != 5:
            raise ValueError("wrong point_data length")
        
        if not callable(pair_func):
            raise ValueError("pair_func is not callable")
        
        if type(seg_func) != str:
            raise TypeError("wrong seg_func type")
        
        if seg_func not in {"brute", "sweep"}:
            raise ValueError("wrong seg_func value")
        
        if type(add_edges_inside) != bool:
            raise TypeError("wrong add_edges_inside type")
        
        if type(inside_percent) not in {float, int}:
            raise TypeError("wrong inside_percent type")
        
        if 0 < inside_percent > 1:
            raise ValueError("wrong inside_percent value")
        
        point = point_data[0]
        obj_number = point_data[1]
        point_number = point_data[2]
        is_polygon = point_data[3]
        visible_vertices = SegmentVisibility()
        polygon_count = self.polygons.shape[0]
        edges_inside = list()

        # loop over all polygons
        for i in range(polygon_count):
            polygon = self.polygons.iloc[i]

            # if a point is not a part of an object
            if obj_number is None or point_number is None or is_polygon is None:
                if Polygon(polygon.geometry).contains(Point(point)):
                    return self.__add_inside_poly(point, None, polygon.geometry, i, inside_percent)
                else:
                    continue

            # if a point is a part of a current polygon
            if is_polygon and i == obj_number:

                # add edges inside a polygon
                if add_edges_inside:
                    edges_inside = self.__add_inside_poly(point, point_number, polygon.geometry, i, inside_percent)

                convex_hull_point_count = len(polygon.convex_hull) - 1
                if convex_hull_point_count <= 2:
                    continue

                # if a point is a part of convex hull
                if point_number in polygon.convex_hull_points:
                    position = polygon.convex_hull_points.index(point_number)
                    left = polygon.convex_hull_points[(position - 1) % convex_hull_point_count]
                    right = polygon.convex_hull_points[(position + 1) % convex_hull_point_count]
                    restriction_pair = (polygon.geometry[left], polygon.geometry[right])
                    visible_vertices.set_restriction_angle(restriction_pair, point, True)

                # if a point is strictly inside a convex hull and a part of polygon
                else:
                    restriction_pair = find_line_brute_force(point, polygon.geometry, i, point_number)
                    if restriction_pair is None:
                        return edges_inside
                    visible_vertices.set_restriction_angle(restriction_pair, point, False)

            # if a point not inside convex hull
            elif not point_in_ch(point, polygon.convex_hull, polygon.angles):
                pair = pair_func(point, polygon.convex_hull, i)
                visible_vertices.add_pair(pair)

            # if a point is inside convex hull but not a part of polygon
            else:
                line = find_line_brute_force(point, polygon.geometry, i)
                if line is None:
                    return self.__add_inside_poly(point, None, polygon.geometry, i, inside_percent)
                visible_vertices.add_line(line)

        # loop over all linestrings
        multilinestring_count = self.multilinestrings.shape[0]
        for i in range(multilinestring_count):
            linestring = self.multilinestrings.geometry[i]
            linestring_point_count = len(linestring)

            # if a point is a part of a current linestring
            if not is_polygon and i == obj_number:
                if point_number > 0:
                    previous = point_number - 1
                    edges_inside.append((linestring[previous], i, previous, False, 2))
                elif point_number + 1 < linestring_point_count:
                    following = point_number + 1
                    edges_inside.append((linestring[following], i, following, False, 2))

            # add whole linestring
            line = list()
            for j in range(linestring_point_count):
                line.append((linestring[j], i, j, False, 0))
            visible_vertices.add_line(line)

        # building visibility graph of segments
        if seg_func=="sweep":
            visible_edges = visible_vertices.get_edges_sweepline(point)
        if seg_func=="brute":
            visible_edges = visible_vertices.get_edges_brute(point)
        visible_edges.extend(edges_inside)
        return visible_edges

    def __process_points_of_objects(self, is_polygon, G, plot, pair_func, seg_func, add_edges_inside, inside_percent):
        max_poly_len = 10000                    # for graph indexing
        object_count = self.polygons.shape[0] if is_polygon else self.multilinestrings.shape[0]

        # loop over all objects
        for i in range(object_count):

            # object coordinates
            obj = self.polygons.geometry[i] if is_polygon else self.multilinestrings.geometry[i]
            point_count = len(obj) - 1 if is_polygon else len(obj)

            # loop over all points of an object
            for j in range(point_count):
                point = obj[j]
                point_data = (point, i, j, is_polygon, None)

                # adding a vertex in networkx graph
                if G is not None:
                    px, py = point
                    point_index = i * max_poly_len + j if is_polygon else (i + 0.5) * max_poly_len + j
                    G.add_node(point_index, x=px, y=py)

                # getting incident vertices
                vertices = self.incident_vertices(point_data, pair_func, seg_func, add_edges_inside, inside_percent)
                if vertices is None:
                    continue
                if G is None and plot is None:
                    continue

                # drawing plot for mplleaflet and adding edges to the graph
                for vertex in vertices:
                    vx, vy = vertex[0]

                    # adding edges to the graph
                    if G is not None:
                        vertex_index = vertex[1] * max_poly_len + vertex[2] if vertex[3] \
                                else (vertex[1] + 0.5) * max_poly_len + vertex[2]
                        G.add_node(vertex_index, x=vx, y=vy)
                        G.add_edge(point_index, vertex_index)

                    # drawing plot for mplleaflet
                    if plot is not None:
                        px, py = point
                        plt.plot([px, vx], [py, vy], color=plot[1][vertex[4]])

    def build_graph(self, pair_func, seg_func="sweep", add_edges_inside=True, inside_percent=1, graph=False, plot=None, crs='EPSG:4326'):
    
        if not callable(pair_func):
            raise ValueError("pair_func is not callable")
        
        if type(seg_func) != str:
            raise TypeError("wrong seg_func type")
        
        if seg_func not in {"brute", "sweep"}:
            raise ValueError("wrong seg_func value")
        
        if type(add_edges_inside) != bool:
            raise TypeError("wrong add_edges_inside type")
        
        if type(inside_percent) not in {float, int}:
            raise TypeError("wrong inside_percent type")
        
        if 0 < inside_percent > 1:
            raise ValueError("wrong inside_percent value")
    
        if type(graph) != bool:
            raise TypeError("wrong graph type")
        
        if plot is not None:
            iter(plot)
        
        if type(crs) != str:
            raise TypeError("wrong crs type")
        
        G = Graph(crs=crs) if graph else None  # MultiGraph
        fig = None

        # drawing polygons for mplleaflet
        if plot is not None:
            fig = plt.figure()
            for p in self.polygons.geometry:
                x, y = zip(*list(p))
                plt.fill(x, y, color=plot[0]);

        # processing polygons and linestrings
        self.__process_points_of_objects(True, G, plot, pair_func, seg_func, add_edges_inside, inside_percent)
        self.__process_points_of_objects(False, G, plot, pair_func, seg_func, add_edges_inside, inside_percent)
        return G, fig

