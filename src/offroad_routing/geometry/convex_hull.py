from typing import TypeVar, Tuple, Optional

from scipy.spatial import ConvexHull

from offroad_routing.geometry.algorithms import polar_angle, compare_points, turn

TPoint = TypeVar("TPoint")  # Tuple[float, float]
TPolygon = TypeVar("TPolygon")  # Tuple[TPoint, ...]
TAngles = TypeVar("TAngles")  # Tuple[float, ...]


def check_polygon_direction(polygon: TPolygon) -> TPolygon:
    return tuple(reversed(polygon)) if len(polygon) >= 3 and turn(polygon[0], polygon[1], polygon[2]) < 0 else polygon


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
        return polygon, tuple([i for i in range(len(polygon) - 1)]), None

    if polygon_size == 3:
        polygon = check_polygon_direction(polygon)
        starting_point = polygon[0]
        angles = [polar_angle(starting_point, vertex) for vertex in polygon]
        angles.pop(0)
        angles.pop()
        return polygon, tuple([i for i in range(len(polygon) - 1)]), tuple(angles)

    ch = ConvexHull(polygon)
    vertices = list(ch.vertices)
    vertices.append(vertices[0])
    points = ch.points[vertices]
    points = check_polygon_direction(points)
    points = tuple([tuple(point) for point in points])
    vertices.pop()

    return points, tuple(vertices), calculate_angles(points)
