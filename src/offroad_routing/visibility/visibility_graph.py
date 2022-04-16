from concurrent.futures import ProcessPoolExecutor

from networkx import MultiGraph
from offroad_routing.geometry.algorithms import compare_points
from offroad_routing.geometry.ch_localization import localize_convex
from offroad_routing.geometry.geom_types import TPolygonData
from offroad_routing.geometry.geom_types import TSegmentData
from offroad_routing.surface.tag_value import polygon_values
from offroad_routing.visibility.inner_edges import find_inner_edges
from offroad_routing.visibility.segment_visibility import SegmentVisibility
from offroad_routing.visibility.supporting_line import find_restriction_pair
from offroad_routing.visibility.supporting_line import find_supporting_line
from offroad_routing.visibility.supporting_pair import find_supporting_pair
from osmnx.folium import plot_graph_folium


class VisibilityGraph:
    """
    Class for building and utilizing visibility graphs.
    Polygons and polylines are used as obstacles on the plane.
    """

    __slots__ = ("polygons", "linestrings", "__graph", "default_weight")

    def __init__(self, polygons, linestrings, default_surface="grass"):
        """
        :param TSegmentData linestrings: road segment records
        :param TPolygonData polygons: polygon records
        :param str default_surface: default surface for unfilled areas (choose prevailing surface)
        """

        self.polygons = polygons
        self.linestrings = linestrings
        if default_surface not in polygon_values.keys():
            raise ValueError("Unknown default surface value")
        self.default_weight = polygon_values[default_surface]
        self.__graph = MultiGraph(crs='EPSG:4326')

    @property
    def graph(self):
        return self.__graph

    def incident_vertices(self, point_data, inside_percent=1):
        """
        Find all incident vertices in visibility graph for given point, computes without building graph.

        :param PointData point_data: point on the map to find incident vertices from
        :param float inside_percent: (from 0 to 1) - controls the number of inner polygon edges
        :return: All visible points from given point on the map.
        :rtype: List[PointData]
        """
        if inside_percent < 0 or inside_percent > 1:
            raise ValueError("inside_percent should be from 1 to 0")

        point, obj_number, point_number, is_polygon = point_data[0:4]
        is_unknown = obj_number is None or point_number is None or is_polygon is None
        visible_vertices = SegmentVisibility()
        edges_inside = list()

        for i, polygon in enumerate(self.polygons):

            # if a point is a part of a current polygon
            if not is_unknown and is_polygon and i == obj_number:

                edges_inside = find_inner_edges(point, point_number, polygon["geometry"], i, inside_percent,
                                                polygon["tag"][0])

                convex_hull_point_count = len(polygon["convex_hull"]) - 1
                if convex_hull_point_count <= 2:
                    continue

                # if a point is a part of convex hull
                if point_number in polygon["convex_hull_points"]:
                    position = polygon["convex_hull_points"].index(
                        point_number)
                    left = polygon["convex_hull_points"][(
                        position - 1) % convex_hull_point_count]
                    right = polygon["convex_hull_points"][(
                        position + 1) % convex_hull_point_count]
                    restriction_pair = (
                        polygon["geometry"][0][left], polygon["geometry"][0][right])
                    visible_vertices.set_restriction_angle(
                        restriction_pair, point, reverse_angle=True)

                # if a point is strictly inside a convex hull and a part of polygon
                else:
                    restriction_pair = find_restriction_pair(
                        point, polygon["geometry"][0], point_number)
                    if restriction_pair is None:
                        return edges_inside
                    visible_vertices.set_restriction_angle(
                        restriction_pair, point, reverse_angle=False)

            # if a point not inside convex hull
            elif not localize_convex(point, polygon["convex_hull"], polygon["angles"])[0]:
                pair = find_supporting_pair(
                    point, polygon["convex_hull"], polygon["angles"])
                if pair is not None:
                    pair = [polygon["convex_hull_points"][k] for k in pair]
                    pair = [(polygon["geometry"][0][k], i, k, True, self.default_weight)
                            for k in pair]
                visible_vertices.add_pair(pair)

            # if a point is inside convex hull but not a part of polygon
            else:
                line = find_supporting_line(point, polygon["geometry"][0])
                if line is None:
                    if is_unknown:
                        return find_inner_edges(point, None, polygon["geometry"], i, inside_percent, polygon["tag"][0])
                    return list()
                # polygons touching
                if len(line) == 1:
                    return [(point, i, line[0], True, 0)]
                line = [(polygon["geometry"][0][k], i, k, True, self.default_weight)
                        for k in line]
                visible_vertices.add_line(line)

        # loop over all segments
        for i, linestring in enumerate(self.linestrings):
            weight = linestring["tag"]
            geometry = linestring["geometry"]

            if is_polygon or is_unknown and not linestring["inside"]:
                visible_vertices.add_pair(
                    ((geometry[0], i, 0, False, 0), (geometry[1], i, 1, False, self.default_weight)))
            elif compare_points(point, geometry[0]):
                edges_inside.append((geometry[1], i, 1, False, weight))
            elif compare_points(point, geometry[1]):
                edges_inside.append((geometry[0], i, 0, False, weight))

        # building visibility graph of segments
        visible_edges = visible_vertices.get_edges_sweepline(point)
        visible_edges.extend(edges_inside)
        return visible_edges

    def __process_points_of_objects(self, is_polygon, inside_percent, multiprocessing) -> None:
        max_poly_len = 10000  # for graph indexing
        objects = self.polygons if is_polygon else self.linestrings
        futures = list()
        with ProcessPoolExecutor() as executor:
            for i, obj in enumerate(objects):
                geometry = obj["geometry"]
                for j, point in enumerate(geometry[0][:-1] if is_polygon else geometry):

                    # adding a vertex in networkx graph
                    px, py = point
                    point_index = i * max_poly_len + \
                        j if is_polygon else int((i + 0.5) * max_poly_len + j)
                    self.__graph.add_node(point_index, x=px, y=py)

                    # getting incident vertices
                    point_data = (point, i, j, is_polygon, None)
                    future = self.incident_vertices(point_data, inside_percent) if not multiprocessing else \
                        executor.submit(self.incident_vertices,
                                        point_data, inside_percent)
                    futures.append((future, point, point_index))

        for future_data in futures:
            future, point, point_index = future_data
            vertices = future.result() if multiprocessing else future
            if vertices is None:
                continue
            for vertex in vertices:
                vx, vy = vertex[0]
                vertex_index = vertex[1] * max_poly_len + vertex[2] if vertex[3] \
                    else int((vertex[1] + 0.5) * max_poly_len + vertex[2])
                self.__graph.add_node(vertex_index, x=vx, y=vy)
                self.__graph.add_edge(
                    point_index, vertex_index, weight=vertex[4])

    def build(self, inside_percent=0.4, multiprocessing=True):
        """
        Compute visibility graph for a set of polygons and polylines and store it in memory.

        :param float inside_percent: (from 0 to 1) - controls the number of inner polygon edges
        :param bool multiprocessing: speed up computation for dense areas using multiprocessing
        """
        if inside_percent < 0 or inside_percent > 1:
            raise ValueError("inside_percent should be from 1 to 0")

        self.__process_points_of_objects(True, inside_percent, multiprocessing)
        self.__process_points_of_objects(
            False, inside_percent, multiprocessing)

    def plot(self, **kwargs):
        """
        Build folium map of computed graph.

        :param kwargs: additional ox.folium.plot_graph_folium() parameters
        :rtype: folium.folium.Map
        """

        if 'color' not in kwargs.keys():
            kwargs['color'] = 'purple'
        if 'tiles' not in kwargs.keys():
            kwargs['tiles'] = 'OpenStreetMap'
        if 'weight' not in kwargs.keys():
            kwargs['weight'] = 0.5
        return plot_graph_folium(self.__graph, **kwargs)

    @property
    def stats(self):
        return {
            'number_of_polygons': len(self.polygons),
            'number_of_road_segments': len(self.linestrings),
            'number_of_edges': self.graph.number_of_edges(),
            'number_of_nodes': self.graph.number_of_nodes()
        }
