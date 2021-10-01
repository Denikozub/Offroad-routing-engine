from concurrent.futures import ProcessPoolExecutor
from typing import Optional, TypeVar, List

from networkx import MultiGraph
from shapely.geometry import Polygon, Point

from offroad_routing.geometry.ch_localization import localize_convex
from offroad_routing.geometry.inner_edges import find_inner_edges
from offroad_routing.geometry.supporting_line import find_restriction_pair, find_supporting_line
from offroad_routing.geometry.supporting_pair import find_supporting_pair
from offroad_routing.osm_data.geometry_saver import GeometrySaver
from offroad_routing.visibility.segment_visibility import SegmentVisibility

TPoint = TypeVar("TPoint")  # Tuple[float, float]
PointData = TypeVar("PointData")  # Tuple[TPoint, Optional[int], Optional[int], Optional[bool], Optional[int]])


class VisibilityGraph(GeometrySaver):

    def incident_vertices(self, point_data: PointData, inside_percent: float = 1) -> List[PointData]:
        """
        Find all incident vertices in visibility graph for given point.
        PointData is a tuple with elements
        0: point coordinates x, y
        1: number of object where point belongs
        2: number of point in object
        3: object is polygon (True) or linestring (False)
        4: surface weight

        :param point_data: information about point
        :param inside_percent: (from 0 to 1) - controls the number of inner polygon edges
        :return: list of PointData of all visible points
        """
        if inside_percent < 0 or inside_percent > 1:
            raise ValueError("inside_percent should be from 1 to 0")

        point = point_data[0]
        obj_number = point_data[1]
        point_number = point_data[2]
        is_polygon = point_data[3]
        visible_vertices = SegmentVisibility()
        polygon_count = self.polygons.shape[0]
        edges_inside = list()

        for i in range(polygon_count):
            polygon = self.polygons.iloc[i]

            # if a point is not a part of an object
            if obj_number is None or point_number is None or is_polygon is None:
                if Polygon(polygon.geometry[0]).contains(Point(point)):
                    return find_inner_edges(point, None, polygon.geometry, i, inside_percent, polygon.tag[0])
                else:
                    continue

            # if a point is a part of a current polygon
            if is_polygon and i == obj_number:

                edges_inside = find_inner_edges(point, point_number, polygon.geometry, i, inside_percent,
                                                polygon.tag[0])

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
                    restriction_pair = find_restriction_pair(point, polygon.geometry[0], point_number)
                    if restriction_pair is None:
                        return edges_inside
                    visible_vertices.set_restriction_angle(restriction_pair, point, False)

            # if a point not inside convex hull
            elif not localize_convex(point, polygon.convex_hull, polygon.angles)[0]:
                pair = find_supporting_pair(point, polygon.convex_hull, i, polygon.angles)
                visible_vertices.add_pair(pair)

            # if a point is inside convex hull but not a part of polygon
            else:
                line = find_supporting_line(point, polygon.geometry[0], i)
                if line is None:
                    return list()
                visible_vertices.add_line(line)

        # loop over all linestrings
        multilinestring_count = self.multilinestrings.shape[0]
        for i in range(multilinestring_count):
            linestring = self.multilinestrings.geometry[i]
            weight = self.multilinestrings.tag[i][0]
            linestring_point_count = len(linestring)

            # if a point is a part of a current linestring
            if not is_polygon and i == obj_number:
                if point_number > 0:
                    previous = point_number - 1
                    edges_inside.append((linestring[previous], i, previous, False, weight))
                elif point_number + 1 < linestring_point_count:
                    following = point_number + 1
                    edges_inside.append((linestring[following], i, following, False, weight))

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

    def __process_points_of_objects(self, is_polygon, G, inside_percent, multiprocessing) -> None:
        max_poly_len = 10000  # for graph indexing
        object_count = self.polygons.shape[0] if is_polygon else self.multilinestrings.shape[0]
        futures = list()
        with ProcessPoolExecutor() as executor:
            for i in range(object_count):
                obj = self.polygons.geometry[i][0] if is_polygon else self.multilinestrings.geometry[i]
                point_count = len(obj) - 1 if is_polygon else len(obj)
                for j in range(point_count):
                    point = obj[j]

                    # adding a vertex in networkx graph
                    px, py = point
                    point_index = i * max_poly_len + j if is_polygon else (i + 0.5) * max_poly_len + j
                    G.add_node(point_index, x=px, y=py)

                    # getting incident vertices
                    point_data = (point, i, j, is_polygon, None)
                    future = self.incident_vertices(point_data, inside_percent) if not multiprocessing else \
                        executor.submit(self.incident_vertices, point_data, inside_percent)
                    futures.append((future, point, point_index))

        for future_data in futures:
            future, point, point_index = future_data
            vertices = future.result() if multiprocessing else future
            if vertices is None:
                continue
            for vertex in vertices:
                vx, vy = vertex[0]
                vertex_index = vertex[1] * max_poly_len + vertex[2] if vertex[3] \
                    else (vertex[1] + 0.5) * max_poly_len + vertex[2]
                G.add_node(vertex_index, x=vx, y=vy)
                G.add_edge(point_index, vertex_index)

    def build_graph(self, inside_percent: float = 0.4, multiprocessing: bool = True,
                    crs: str = 'EPSG:4326') -> Optional[MultiGraph]:
        """
        Compute [and build] [and plot] visibility graph.

        :param inside_percent: (from 0 to 1) - controls the number of inner polygon edges
        :param multiprocessing: bool - speed up computation for dense areas using multiprocessing
        :param crs: coordinate reference system
        :return: networkx.MultiGraph
        """
        if inside_percent < 0 or inside_percent > 1:
            raise ValueError("inside_percent should be from 1 to 0")

        G = MultiGraph(crs=crs)
        self.__process_points_of_objects(True, G, inside_percent, multiprocessing)
        self.__process_points_of_objects(False, G, inside_percent, multiprocessing)
        return G
