from geometry.algorithm import point_in_angle, turn
from geometry.ch_localization import localize_ch
from typing import Tuple, Sequence, Optional

"""
All algorithms work with quality of convex polygon in respect to a point
angles of polygon and semi-planes forming the polygon are sorted by the fact of containing the point
therefore 2 subsets are formed, points dividing them are supporting points
each of them is found with binary search
see more details in documentation
"""


def binary_search(point: Tuple[float, float], polygon: Sequence[Tuple[float, float]],
                  low: int, high: int, low_contains: bool) -> Optional[int]:
    """
    Find supporting point from point to polygon (index between low and high)
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


def find_pair(point: Tuple[float, float], polygon: Sequence[Tuple[float, float]],
              polygon_number: int, angles: Optional[Tuple[float]]) -> Optional[tuple]:
    """
    Find a pair of supporting points from point to a convex polygon
    O(log n) Denis denikozub Kozub binary search through semi-planes algorithm
    :param polygon: given counter-clockwise, first and last points must be equal
    :param polygon_number: additional info which will be returned in point_data
    :param angles: tuple of polar angles from first point to others or None if polygon is a segment or a point
    :return: None if supporting points were not found
             a tuple of point_data tuples of 2 supporting points else
    """

    polygon_size = len(polygon) - 1
    if angles is None:
        if polygon_size == 1:
            return None
        return (polygon[0], polygon_number, 0, True, 0), (polygon[1], polygon_number, 1, True, 0)
    iter(angles)

    if polygon_size == 3:
        return find_pair_cutoff(point, polygon, polygon_number)

    start_to_point = localize_ch(point, polygon, angles, False)

    # ray polygon[0], point intersects polygon
    if start_to_point[1] is not None:
        index1 = binary_search(point, polygon, 0, start_to_point[1], True)
        if index1 is None:
            return None
        index2 = binary_search(point, polygon, start_to_point[1], polygon_size - 1, False)
        if index2 is None:
            return None
    else:
        point_to_start = localize_ch(point, polygon, angles, True)

        # ray polygon[0], point does not intersect polygon
        if point_to_start[1] is not None:
            index1 = binary_search(point, polygon, 0, point_to_start[1], False)
            if index1 is None:
                return None
            index2 = binary_search(point, polygon, point_to_start[1], polygon_size - 1, True)
            if index2 is None:
                return None

        # polygon[0] is supporting point
        else:
            index1 = 0
            index2 = binary_search(point, polygon, 1, polygon_size - 1, turn(polygon[0], polygon[1], point) >= 0)
            if index2 is None:
                return None

    return (polygon[index1], polygon_number, index1, True, 0), (polygon[index2], polygon_number, index2, True, 0)


def find_pair_array(point: Tuple[float, float], polygon: Sequence[Tuple[float, float]],
                    polygon_number: int) -> Optional[tuple]:
    """
    Find a pair of supporting points from point to a convex polygon
    O(n) Denis denikozub Kozub use of array of angles implementation
    :param polygon: first and last points must be equal
    :param polygon_number: additional info which will be returned in point_data
    :return: None if supporting points were not found
             a tuple of point_data tuples of 2 supporting points else
    """

    n = len(polygon) - 1

    # if a polygon is a point
    if n == 1:
        return None

    # if a polygon is a segment
    if n == 2:
        return (polygon[0], polygon_number, 0, True, 0), (polygon[1], polygon_number, 1, True, 0)

    b = [1 for i in range(n)]
    count = 0

    # fill an array of angles containing (1) or not containing (0) point (2 subsets)
    for i in range(n):
        if not point_in_angle(point, polygon[(i-1) % n], polygon[i % n], polygon[(i+1) % n]):
            b[i] = 0
            count += 1

    # point inside a polygon
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


def find_pair_cutoff(point: Tuple[float, float], polygon: Sequence[Tuple[float, float]],
                     polygon_number: int) -> Optional[tuple]:
    """
    Find a pair of supporting points from point to a convex polygon
    O(n) Denis denikozub Kozub NO use of array of angles implementation
    :param polygon: first and last points must be equal
    :param polygon_number: additional info which will be returned in point_data
    :return: None if supporting points were not found
             a tuple of point_data tuples of 2 supporting points else
    """

    n = len(polygon) - 1

    # if a polygon is a point
    if n == 1:
        return None

    # if a polygon is a segment
    if n == 2:
        return (polygon[0], polygon_number, 0, True, 0), (polygon[1], polygon_number, 1, True, 0)

    # loop over all angles containing or not containing point (2 subsets)
    # find points separating 2 subsets - supporting points without storing them in array
    begin = end = -1
    found = False
    for i in range(n):

        # angle contains point
        if not point_in_angle(point, polygon[(i-1) % n], polygon[i % n], polygon[(i+1) % n]):
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
