from typing import Optional, TypeVar, Tuple

from offroad_routing.geometry.algorithms import turn, compare_points
from offroad_routing.geometry.ch_localization import localize_convex

TPoint = TypeVar("TPoint")  # Tuple[float, float]
TPolygon = TypeVar("TPolygon")  # Tuple[TPoint, ...]
TAngles = TypeVar("TAngles")  # Tuple[float, ...]
PointData = TypeVar("PointData")  # Tuple[TPoint, Optional[int], Optional[int], Optional[bool], Optional[int]]

"""
All algorithms work with quality of convex polygon in respect to a point:
angles of polygon and semi-planes forming the polygon are sorted by the fact of containing the point.
Therefore 2 subsets are formed, points dividing them are supporting points, each of them is found with binary search.
See more details in documentation.
"""


def find_supporting_point(point: TPoint, polygon: TPolygon, low: int, high: int, low_contains: bool) -> Optional[int]:
    """
    Find supporting point from point to polygon (index between low and high) with binary search.

    :param point: visibility point (x, y)
    :param polygon: convex, given counter-clockwise, first and last points must be equal
    :param low: binary search algorithm parameter (polygon min index)
    :param high: binary search algorithm parameter (polygon max index)
    :param low_contains: angle formed by polygon[low] contains point (True) or not (False)
    :return: index of supporting point from point to polygon or None if unable to find
    """

    polygon_size = len(polygon) - 1
    assert polygon_size >= 3
    assert compare_points(polygon[0], polygon[-1])
    assert turn(polygon[0], polygon[1], polygon[2]) >= 0

    mid = (high + low) // 2
    while low <= high and mid < polygon_size:

        # supporting point separating 2 subsets is found
        if turn(polygon[mid], polygon[(mid + 1) % polygon_size], point) <= 0 and \
                turn(polygon[(mid - 1) % polygon_size], polygon[mid], point) >= 0 or \
                turn(polygon[mid], polygon[(mid + 1) % polygon_size], point) >= 0 and \
                turn(polygon[(mid - 1) % polygon_size], polygon[mid], point) <= 0:
            return mid

        # update mid
        if low_contains and turn(polygon[mid], polygon[(mid + 1) % polygon_size], point) >= 0 or \
                not low_contains and turn(polygon[mid], polygon[(mid + 1) % polygon_size], point) <= 0:
            low = mid + 1
        else:
            high = mid - 1
        mid = (high + low) // 2
        
    return None


def find_supporting_pair(point: TPoint, polygon: TPolygon, polygon_number: int,
                         angles: Optional[TAngles]) -> Optional[Tuple[PointData, PointData]]:
    """
        Find pair of supporting points from point to polygon in log time (binary search).

        :param point: visibility point (x, y)
        :param polygon: convex, given counter-clockwise, first and last points must be equal
        :param polygon_number: sequence number of polygon for PointData
        :param angles: tuple of polar angles from #0 point of polygon to all others except itself
        :return: pair of PointData of supporting points or None if unable to find
    """

    polygon_size = len(polygon) - 1
    assert polygon_size >= 2
    assert compare_points(polygon[0], polygon[-1])
    if polygon_size <= 3:
        return find_supporting_pair_semiplanes(point, polygon, polygon_number)
    assert turn(polygon[0], polygon[1], polygon[2]) >= 0
    assert len(angles) == polygon_size - 1

    start_to_point = localize_convex(point, polygon, angles, False)

    # ray polygon[0], point intersects polygon
    if start_to_point[1] is not None:
        index1 = find_supporting_point(point, polygon, 0, start_to_point[1], True)
        if index1 is None:
            return None
        index2 = find_supporting_point(point, polygon, start_to_point[1], polygon_size - 1, False)
        if index2 is None:
            return None
    else:
        point_to_start = localize_convex(point, polygon, angles, True)

        # ray polygon[0], point does not intersect polygon
        if point_to_start[1] is not None:
            index1 = find_supporting_point(point, polygon, 0, point_to_start[1], False)
            if index1 is None:
                return None
            index2 = find_supporting_point(point, polygon, point_to_start[1], polygon_size - 1, True)
            if index2 is None:
                return None

        # polygon[0] is supporting point
        else:
            index1 = 0
            index2 = find_supporting_point(point, polygon, 1, polygon_size-1, turn(polygon[0], polygon[1], point) >= 0)
            if index2 is None:
                return None

    return (polygon[index1], polygon_number, index1, True, 0), (polygon[index2], polygon_number, index2, True, 0)


def find_supporting_pair_semiplanes(point: TPoint, polygon: TPolygon, polygon_number: int) -> Optional[tuple]:
    """
        Find pair of supporting points from point to polygon in linear line.

        :param point: visibility point (x, y)
        :param polygon: convex, first and last points must be equal
        :param polygon_number: sequence number of polygon for PointData
        :return: pair of PointData of supporting points or None if unable to find
    """

    polygon_size = len(polygon) - 1
    assert polygon_size >= 2
    assert compare_points(polygon[0], polygon[-1])
    if polygon_size == 2:
        return (polygon[0], polygon_number, 0, True, 0), (polygon[1], polygon_number, 1, True, 0)

    semiplanes = [1] * polygon_size
    count = 0
    polygon_turn = turn(polygon[0], polygon[1], polygon[2])

    # fill an array of angles containing (1) or not containing (0) point (2 subsets)
    for i in range(polygon_size):
        if turn(polygon[i % polygon_size], polygon[(i + 1) % polygon_size], point) * polygon_turn < 0:
            semiplanes[i] = 0
            count += 1

    if count in (0, polygon_size):
        return None

    start = semiplanes.index(1) if semiplanes[0] == 0 else semiplanes.index(0)
    end = (len(semiplanes) - semiplanes[::-1].index(1)) % polygon_size if semiplanes[0] == 0 else \
        (len(semiplanes) - semiplanes[::-1].index(0)) % polygon_size
    return (polygon[start], polygon_number, start, True, 0), (polygon[end], polygon_number, end, True, 0)
