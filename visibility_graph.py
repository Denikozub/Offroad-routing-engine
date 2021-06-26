from shapely.geometry import Polygon, Point
from networkx import MultiGraph
from matplotlib.pyplot import plot, figure, fill
from parsers.osm_data import OsmData
from geometry.locate_convex import point_in_ch
from geometry.supporting_non_convex import find_line_brute_force
from segment_visibility import SegmentVisibility
from geometry.edges_inside import edge_inside_poly
from geometry.supporting_convex import find_pair


class VisibilityGraph(OsmData):

    def incident_vertices(self, point_data, inside_percent=0.4):
        """
        find all incident vertices in visibility graph for given point
        :param point_data: point_data of given point
        :param inside_percent: float parameter setting the probability of an inner edge to be added (from 0 to 1)
        :return: list of point_data of all visible points
        point_data is a tuple where:
            0 element: point coordinates - tuple of x, y
            1 element: number of object where point belongs
            2 element: number of point in object
            3 element: if object is polygon (1) or linestring (0)
            4 element: surface type (0 - edge between objects, 1 - edge inside polygon, 2 - road edge)
        """

        iter(point_data)

        if len(point_data) != 5:
            raise ValueError("wrong point_data length")

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
                if Polygon(polygon.geometry[0]).contains(Point(point)):
                    return edge_inside_poly(point, None, polygon.geometry, i, inside_percent)
                else:
                    continue

            # if a point is a part of a current polygon
            if is_polygon and i == obj_number:

                # add edges inside a polygon
                edges_inside = edge_inside_poly(point, point_number, polygon.geometry, i, inside_percent)

                convex_hull_point_count = len(polygon.convex_hull) - 1
                if convex_hull_point_count <= 2:
                    continue

                # if a point is a part of convex hull
                if point_number in polygon.convex_hull_points:
                    position = polygon.convex_hull_points.index(point_number)
                    left = polygon.convex_hull_points[(position - 1) % convex_hull_point_count]
                    right = polygon.convex_hull_points[(position + 1) % convex_hull_point_count]
                    restriction_pair = (polygon.geometry[0][left], polygon.geometry[0][right])
                    visible_vertices.set_restriction_angle(restriction_pair, point, True)

                # if a point is strictly inside a convex hull and a part of polygon
                else:
                    restriction_pair = find_line_brute_force(point, polygon.geometry[0], i, point_number)
                    if restriction_pair is None:
                        return edges_inside
                    visible_vertices.set_restriction_angle(restriction_pair, point, False)

            # if a point not inside convex hull
            elif not point_in_ch(point, polygon.convex_hull, polygon.angles)[0]:
                pair = find_pair(point, polygon.convex_hull, i, polygon.angles)
                visible_vertices.add_pair(pair)

            # if a point is inside convex hull but not a part of polygon
            else:
                line = find_line_brute_force(point, polygon.geometry[0], i)
                if line is None:
                    return edge_inside_poly(point, None, polygon.geometry, i, inside_percent)
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

            else:
                # add whole linestring
                line = list()
                for j in range(linestring_point_count):
                    line.append((linestring[j], i, j, False, 0))
                visible_vertices.add_line(line)

        # building visibility graph of segments
        visible_edges = visible_vertices.get_edges_sweepline(point)
        visible_edges.extend(edges_inside)
        return visible_edges

    def __process_points_of_objects(self, is_polygon, G, map_plot, inside_percent):
        """
        build visibility graph for all objects of given type (polygons or linestrings)
        :param is_polygon: bool parameter: set object type
        :param G: None or networkx.Graph
        :param map_plot: None or iterable of 2 elements: colors to plot visibility graph
            0 element: color to plot polygons  
            1 element: dict of 3 elements: colors to plot edges  
                0: edges between objects
                1: edges inside polygon
                2: road edges
        :param inside_percent: float parameter setting the probability of an inner edge to be added (from 0 to 1)
        :return: None
        """

        max_poly_len = 10000                    # for graph indexing
        object_count = self.polygons.shape[0] if is_polygon else self.multilinestrings.shape[0]

        # loop over all objects
        for i in range(object_count):

            # object coordinates
            obj = self.polygons.geometry[i][0] if is_polygon else self.multilinestrings.geometry[i]
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
                vertices = self.incident_vertices(point_data, inside_percent)
                if vertices is None:
                    continue
                if G is None and map_plot is None:
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
                    if map_plot is not None:
                        px, py = point
                        plot([px, vx], [py, vy], color=map_plot[1][vertex[4]])

    def build_graph(self, inside_percent=1, graph=False, map_plot=None, crs='EPSG:4326'):
        """
        compute [and build] [and plot] visibility graph
        :param inside_percent: float parameter setting the probability of an inner edge to be added (from 0 to 1)
        :param graph: bool parameter indicating whether to build a networkx graph
        :param map_plot: None or iterable of 2 elements: colors to plot visibility graph
            0 element: color to plot polygons  
            1 element: dict of 3 elements: colors to plot edges  
                0: edges between objects
                1: edges inside polygon
                2: road edges
        :param crs: string parameter: coordinate reference system
        :return: None
        """

        if type(inside_percent) not in {float, int}:
            raise TypeError("wrong inside_percent type")

        if 0 < inside_percent > 1:
            raise ValueError("wrong inside_percent value")

        if type(graph) != bool:
            raise TypeError("wrong graph type")

        if map_plot is not None:
            iter(map_plot)

        if type(crs) != str:
            raise TypeError("wrong crs type")

        G = MultiGraph(crs=crs) if graph else None
        fig = None

        # drawing polygons for mplleaflet
        if map_plot is not None:
            fig = figure()
            for p in self.polygons.geometry:
                x, y = zip(*list(p[0]))
                fill(x, y, color=map_plot[0])

        # processing polygons and linestrings
        self.__process_points_of_objects(True, G, map_plot, inside_percent)
        self.__process_points_of_objects(False, G, map_plot, inside_percent)
        return G, fig
