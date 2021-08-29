from typing import TypeVar, Tuple, Optional

from scipy.spatial import ConvexHull

from geometry.algorithms import polar_angle, equal_points

TPoint = TypeVar("TPoint")  # Tuple[float, float]
TPolygon = TypeVar("TPolygon")  # Sequence[TPoint]
TAngles = TypeVar("TAngles")  # Sequence[float]


def build_convex_hull(polygon: TPolygon) -> Tuple[TPolygon, Tuple[int, ...], Optional[TAngles]]:
    """
    :return: tuple of 3 elements:
        1. tuple of convex hull points
        2. tuple of their indexes in initial polygon
        3. tuple of polar angles from first point to others or None if polygon is a segment or a point
    """

    assert equal_points(polygon[0], polygon[-1])
    polygon_size = len(polygon) - 1
    if polygon_size <= 2:
        return polygon, tuple([i for i in range(len(polygon) - 1)]), None
    if polygon_size == 3:
        starting_point = polygon[0]
        angles = [polar_angle(starting_point, vertex) for vertex in polygon]
        angles.pop(0)
        angles.pop()
        return polygon, tuple([i for i in range(len(polygon) - 1)]), tuple(angles)

    ch = ConvexHull(polygon)
    points = list(ch.vertices)
    points.append(points[0])
    vertices = ch.points[points]
    vertices = tuple([tuple(point) for point in vertices])
    points.pop()

    # calculating angles
    starting_point = vertices[0]
    angles = [polar_angle(starting_point, vertex) for vertex in vertices]
    angles.pop(0)
    angles.pop()
    return vertices, tuple(points), tuple(angles)
