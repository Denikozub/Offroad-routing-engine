from math import pi
from typing import Tuple, Optional, TypeVar

from geometry.algorithms import polar_angle, equal_points, turn

TPoint = TypeVar("TPoint")  # Tuple[float, float]
TPolygon = TypeVar("TPolygon")  # Sequence[TPoint]
TAngles = TypeVar("TAngles")  # Sequence[float]


def localize_convex_linear(point: TPoint, polygon: TPolygon) -> bool:
    assert equal_points(polygon[0], polygon[-1])
    polygon_size = len(polygon) - 1
    if polygon_size <= 2:
        return False
    polygon_cross = turn(polygon[0], polygon[1], polygon[2])
    for i in range(polygon_size):
        if turn(polygon[i], polygon[i + 1], point) * polygon_cross <= 0:
            return False
    return True


def localize_convex(point: TPoint, polygon: TPolygon, angles: Optional[TAngles],
                    reverse_angle: bool = False) -> Tuple[bool, Optional[int]]:
    """
    Localizing point inside convex polygon O(log n) Preparata-Shamos algorithm.

    :param point: point to be localized
    :param polygon: given counter-clockwise, first and last points must be equal
    :param angles: polar angles from first point to others or None if polygon is a segment or a point
    :param reverse_angle: point_angle should be turned on pi (True) or not (False)
    :return: tuple of 2 elements:
        1. bool - point is inside polygon
        2. None if point is inside polygon else int - number of polygon vertex where point_angle is located
    """

    if angles is None:
        return False, None

    if equal_points(point, polygon[0]):
        return True, None

    assert equal_points(polygon[0], polygon[-1])
    assert len(polygon) == 2 or turn(polygon[0], polygon[1], polygon[2]) >= 0

    point_angle = polar_angle(point, polygon[0]) if reverse_angle else polar_angle(polygon[0], point)

    # point angle not between angles
    if angles[-1] < pi < angles[0]:
        if angles[-1] <= point_angle <= angles[0]:
            return False, None
    elif point_angle <= angles[0] or point_angle >= angles[-1]:
        return False, None

    mid = (len(angles) - 1) // 2
    low = 0
    high = len(angles) - 1
    while low <= high:
        if mid + 1 == len(angles):
            return False, None
        angle1 = angles[mid]
        angle2 = angles[mid + 1]

        # 2 angles contain zero-angle
        if angle1 > pi > angle2:
            if point_angle >= angle1 or point_angle <= angle2:
                return turn(polygon[mid + 1], polygon[mid + 2], point) > 0, mid + 2
            if point_angle > pi:
                high = mid - 1
            if point_angle < pi:
                low = mid + 1
        else:
            if angle1 <= point_angle <= angle2:
                return turn(polygon[mid + 1], polygon[mid + 2], point) > 0, mid + 2
            if point_angle - pi > angle2:
                high = mid - 1
            elif point_angle + pi < angle1:
                low = mid + 1
            elif point_angle < angle1:
                high = mid - 1
            else:
                low = mid + 1
        mid = (high + low) // 2
    return False, None
