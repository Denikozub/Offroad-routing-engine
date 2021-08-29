from typing import Optional, TypeVar, Tuple

from geometry.algorithms import point_in_sector, turn, equal_points
from geometry.ch_localization import localize_convex

TPoint = TypeVar("TPoint")  # Tuple[float, float]
TPolygon = TypeVar("TPolygon")  # Sequence[TPoint]
TAngles = TypeVar("TAngles")  # Sequence[float]
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

    :param point: visibility point
    :param polygon: given counter-clockwise, first and last points must be equal
    :param low: binary search algorithm parameter (polygon min index)
    :param high: binary search algorithm parameter (polygon max index)
    :param low_contains: angle formed by polygon[low] contains point (True) or not (False)
    :return: index of supporting point from point to polygon
    """

    polygon_size = len(polygon) - 1
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
    assert equal_points(polygon[0], polygon[-1])
    polygon_size = len(polygon) - 1
    if angles is None:
        if polygon_size == 1:
            return None
        return (polygon[0], polygon_number, 0, True, 0), (polygon[1], polygon_number, 1, True, 0)

    if polygon_size == 3:
        return find_supporting_pair_cutoff(point, polygon, polygon_number)

    assert turn(polygon[0], polygon[1], polygon[2]) >= 0

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
            index2 = find_supporting_point(point, polygon, 1, polygon_size - 1, turn(polygon[0], polygon[1], point) >= 0)
            if index2 is None:
                return None

    return (polygon[index1], polygon_number, index1, True, 0), (polygon[index2], polygon_number, index2, True, 0)


def find_supporting_pair_array(point: TPoint, polygon: TPolygon, polygon_number: int) -> Optional[tuple]:
    n = len(polygon) - 1
    if n == 1:
        return None
    if n == 2:
        return (polygon[0], polygon_number, 0, True, 0), (polygon[1], polygon_number, 1, True, 0)
    b = [1 for _ in range(n)]
    count = 0

    # fill an array of angles containing (1) or not containing (0) point (2 subsets)
    for i in range(n):
        if not point_in_sector(point, polygon[(i - 1) % n], polygon[i % n], polygon[(i + 1) % n]):
            b[i] = 0
            count += 1
    if count in (0, n):
        return None

    # find points separating 2 subsets of 0 and 1 in array - supporting points
    if b[0] == 1:
        start = b.index(0, 1)
        if b[n-1] == 0:
            end = n-1
        else:
            end = b.index(1, start + 1)
            end -= 1
    else:
        start = b.index(1, 1)
        start -= 1
        if b[n-1] == 1:
            end = n
        else:
            end = b.index(0, start + 1)
                
    return (polygon[start], polygon_number, start, True, 0), (polygon[end], polygon_number, end, True, 0)


def find_supporting_pair_cutoff(point: TPoint, polygon: TPolygon, polygon_number: int) -> Optional[tuple]:
    n = len(polygon) - 1
    if n == 1:
        return None
    if n == 2:
        return (polygon[0], polygon_number, 0, True, 0), (polygon[1], polygon_number, 1, True, 0)

    # loop over all angles containing or not containing point (2 subsets)
    # find points separating 2 subsets - supporting points without storing them in array
    begin = end = -1
    found = False
    for i in range(n):

        # angle contains point
        if not point_in_sector(point, polygon[(i - 1) % n], polygon[i % n], polygon[(i + 1) % n]):
            if i == 0:
                start_zero = True
            if begin == -1 and not start_zero:
                begin = i
            if start_zero and end != -1:
                begin = i
                found = True
                break
            if not start_zero and i == n - 1:
                end = n - 1
                found = True
                break

        # angle does not contain point
        else:
            if i == 0:
                start_zero = False
            if begin != -1 and not start_zero:
                end = (i-1) % n
                found = True
                break
            if start_zero and end == -1:
                end = (i-1) % n
            if start_zero and i == n - 1:
                begin = n
                found = True
                break
                    
    return None if not found else ((polygon[begin], polygon_number, begin, True, 0),
                                   (polygon[end], polygon_number, end, True, 0))
