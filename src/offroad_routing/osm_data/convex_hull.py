from typing import Optional
from typing import Tuple

from offroad_routing.geometry.algorithms import compare_points
from offroad_routing.geometry.algorithms import polar_angle
from offroad_routing.geometry.algorithms import turn
from offroad_routing.geometry.geom_types import TAngles
from offroad_routing.geometry.geom_types import TPolygon
from scipy.spatial import ConvexHull


def check_polygon_direction(polygon: TPolygon) -> TPolygon:
    return len(polygon) < 3 or turn(polygon[0], polygon[1], polygon[2]) > 0


def calculate_angles(polygon: TPolygon) -> TAngles:
    starting_point = polygon[0]
    angles = [polar_angle(starting_point, point) for point in polygon]
    angles.pop(0)
    angles.pop()
    return tuple(angles)


def build_convex_hull(polygon: TPolygon) -> Tuple[TPolygon, Tuple[int, ...], Optional[TAngles]]:
    """
    :param polygon: first and last points must be equal
    :return: tuple of 3 elements:
        1. tuple of convex hull points
        2. tuple of their indexes in initial polygon
        3. tuple of polar angles from first point to others except itself or None if polygon is a segment or a point
    """

    polygon_size = len(polygon) - 1
    assert polygon_size >= 2
    assert compare_points(polygon[0], polygon[-1])

    if polygon_size == 2:
        return polygon, tuple(i for i in range(len(polygon) - 1)), None

    if polygon_size == 3:
        vertices = list(range(len(polygon) - 1)) + [0]
        if not check_polygon_direction(polygon):
            polygon = tuple(reversed(polygon))
            vertices = list(reversed(vertices))
        starting_point = polygon[0]
        angles = [polar_angle(starting_point, vertex)
                  for vertex in polygon][1:-1]
        vertices.pop()
        return polygon, tuple(vertices), tuple(angles)

    ch = ConvexHull(polygon)
    vertices = list(ch.vertices)
    vertices.append(vertices[0])
    points = ch.points[vertices]
    if not check_polygon_direction(points):
        points = tuple(reversed(points))
        vertices = list(reversed(vertices))
    points = tuple(tuple(point) for point in points)
    vertices.pop()

    return points, tuple(vertices), calculate_angles(points)
