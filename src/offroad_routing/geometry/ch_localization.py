from math import pi
from typing import Optional
from typing import Tuple
from typing import TypeVar

from offroad_routing.geometry.algorithms import compare_points
from offroad_routing.geometry.algorithms import polar_angle
from offroad_routing.geometry.algorithms import turn

TPoint = TypeVar("TPoint")  # Tuple[float, float]
TPolygon = TypeVar("TPolygon")  # Tuple[TPoint, ...]
TAngles = TypeVar("TAngles")  # Tuple[float, ...]


def localize_convex_linear(point: TPoint, polygon: TPolygon) -> bool:
    """
    Localize point inside convex polygon in linear time.

    :param point: point to be localized (x, y)
    :param polygon: convex, given counter-clockwise, first and last points must be equal
    """

    polygon_size = len(polygon) - 1
    assert polygon_size >= 2
    assert compare_points(polygon[0], polygon[-1])
    if polygon_size <= 2:
        return False
    polygon_cross = turn(polygon[0], polygon[1], polygon[2])
    for i in range(polygon_size):
        if turn(polygon[i], polygon[i + 1], point) * polygon_cross <= 0:
            return False
    return True


def localize_convex(point: TPoint, polygon: TPolygon, angles: Optional[TAngles], *,
                    reverse_angle: bool = False) -> Tuple[bool, Optional[int]]:
    """
    Localize point inside convex polygon in log time (Preparata-Shamos algorithm).

    :param point: point to be localized (x, y)
    :param polygon: convex, given counter-clockwise, first and last points must be equal
    :param angles: tuple of polar angles from #0 point of polygon to all others except itself
    :param reverse_angle: point angles should be turned on pi (True) or not (False)
    :return: tuple of 2 elements:
        1. bool - point is inside polygon
        2. None if point is inside polygon else int - number of polygon vertex where point_angle is located.
    """

    polygon_size = len(polygon) - 1
    assert polygon_size >= 2
    assert compare_points(polygon[0], polygon[-1])
    if polygon_size <= 2:
        return False, None
    assert turn(polygon[0], polygon[1], polygon[2]) >= 0
    assert len(angles) == polygon_size - 1

    if compare_points(point, polygon[0]):
        return True, None
    point_angle = polar_angle(
        point, polygon[0]) if reverse_angle else polar_angle(polygon[0], point)

    # point angle not between angles
    if angles[-1] < pi < angles[0]:
        if angles[-1] <= point_angle <= angles[0]:
            return False, None
    elif point_angle <= angles[0] or point_angle >= angles[-1]:
        return False, None

    angles_len = len(angles)
    mid = (angles_len - 1) // 2
    low = 0
    high = angles_len - 1
    while low <= high:
        if mid + 1 == angles_len:
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
