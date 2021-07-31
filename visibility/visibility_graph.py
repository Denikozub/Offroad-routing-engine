from shapely.geometry import Polygon, Point
from networkx import MultiGraph
from tqdm import tqdm
from matplotlib.pyplot import plot, figure, fill
from matplotlib.figure import Figure
from typing import Tuple, Optional, Dict
from osm_data.geometry_saver import GeometrySaver
from visibility.segment_visibility import SegmentVisibility
from geometry.ch_localization import localize_ch
from geometry.supporting_pair import find_line_brute_force
from geometry.supporting_pair_ch import find_pair
from geometry.inner_edges import inner_edges


class VisibilityGraph(GeometrySaver):

    def incident_vertices(self, point_data: Tuple[Tuple[float, float], Optional[int], Optional[int], Optional[bool],
                                                  Optional[int]], inside_percent: float = 0.4) -> list:
        """
        find all incident vertices in visibility graph for given point
        :param point_data: point_data of given point
        :param inside_percent: probability of an inner edge to be added (from 0 to 1)
        :return: list of point_data of all visible points
        point_data is a tuple where:
            0 element: point coordinates x, y
            1 element: number of object where point belongs
            2 element: number of point in object
            3 element: object is polygon (True) or linestring (False)
            4 element: surface type (0 - edge between objects, 1 - edge inside polygon, 2 - road edge)
        """
        assert 0 <= inside_percent <= 1

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
                    return inner_edges(point, None, polygon.geometry, i, inside_percent)
                else:
                    continue

            # if a point is a part of a current polygon
            if is_polygon and i == obj_number:

                # add edges inside a polygon
                edges_inside = inner_edges(point, point_number, polygon.geometry, i, inside_percent)

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
            elif not localize_ch(point, polygon.convex_hull, polygon.angles)[0]:
                pair = find_pair(point, polygon.convex_hull, i, polygon.angles)
                visible_vertices.add_pair(pair)

            # if a point is inside convex hull but not a part of polygon
            else:
                line = find_line_brute_force(point, polygon.geometry[0], i)
                if line is None:
                    return inner_edges(point, None, polygon.geometry, i, inside_percent)
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

    def __process_points_of_objects(self, is_polygon: bool, G: Optional[MultiGraph],
                                    map_plot: Optional[Tuple[str, Dict[int, str]]], inside_percent: float) -> None:
        """
        Build visibility graph for all objects of given type (polygons or linestrings)
        """

        max_poly_len = 10000                    # for graph indexing
        object_count = self.polygons.shape[0] if is_polygon else self.multilinestrings.shape[0]

        # loop over all objects
        for i in tqdm(range(object_count)):

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
                        plot([px, vx], [py, vy], color=map_plot[1][vertex[4]], linewidth=4 if vertex[4] == 2 else None)

    def build_graph(self, inside_percent: float = 1, graph: bool = False,
                    map_plot: Optional[Tuple[str, Dict[int, str]]] = None,
                    crs: str = 'EPSG:4326') -> Tuple[Optional[MultiGraph], Optional[Figure]]:
        """
        Compute [and build] [and plot] visibility graph
        :param inside_percent: probability of an inner edge to be added (from 0 to 1)
        :param graph: build (True) or not to build (False) a networkx graph
        :param map_plot: colors to plot visibility graph
            0 element: color to plot polygons  
            1 element: colors to plot edges
                0: edges between objects
                1: edges inside polygon
                2: road edges
        :param crs: coordinate reference system
        """
        assert 0 <= inside_percent <= 1
        assert map_plot is None or len(map_plot) == 2 and isinstance(map_plot[1], dict)

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
