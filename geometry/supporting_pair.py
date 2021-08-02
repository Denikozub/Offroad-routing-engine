from typing import Optional, Union, List, TypeVar, Tuple

from geometry.algorithm import ray_intersects_segment, turn

TPoint = TypeVar("TPoint")  # Tuple[float, float]
TPolygon = TypeVar("TPolygon")  # Sequence[TPoint]
PointData = TypeVar("PointData")  # Tuple[TPoint, Optional[int], Optional[int], Optional[bool], Optional[int]]


def find_line_brute_force(point: TPoint, polygon: TPolygon, polygon_number: int,
                          point_number: Optional[int] = None) -> Union[Tuple[TPoint, TPoint], List[PointData], None]:
    """
    Find a pair of supporting points from point to a non-convex polygon, O(n^2) brute force.

    :param point: visibility point
    :param polygon: first and last points must be equal
    :param polygon_number: additional info which will be returned in PointData
    :param point_number: None if point is not a polygon vertex else number or vertex
    :return: None if supporting points were not found,
             a tuple of coordinates of 2 supporting points if polygon_point_number is None,
             a list of PointData tuples of points connecting 2 supporting points else
    """

    n = len(polygon) - 1
    result = list()

    # loop over all points of a polygon
    for i in range(n):
        pi = polygon[i]

        # point equals current point
        if point_number is not None and i == point_number:
            continue

        # cannot be supporting point
        if turn(point, pi, polygon[(i - 1) % n]) * turn(point, pi, polygon[(i + 1) % n]) < 0:
            continue
        found = True

        # check intersection with all other points
        for j in range(n):
            if j in (i - 1, i) or (point_number is not None and j in (point_number - 1, point_number)):
                continue
            if ray_intersects_segment(point, pi, polygon[j], polygon[j + 1]):
                found = False
                break
        if found:
            result.append(i)

    # did not find 2 supporting points
    if len(result) != 2:
        return None

    # return restriction pair if point is part of polygon
    point1, point2 = result
    if point_number is not None:
        return polygon[point1], polygon[point2]

    # add shortest line from one point to another
    line = list()
    if point2 - point1 > (n - 1) / 2:
        for i in range(point2, n + 1):
            line.append((polygon[i], polygon_number, i, True, 0))
        for i in range(0, point1 + 1):
            line.append((polygon[i], polygon_number, i, True, 0))
    else:
        for i in range(point1, point2 + 1):
            line.append((polygon[i], polygon_number, i, True, 0))
    return line
