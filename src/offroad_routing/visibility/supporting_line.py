from typing import List
from typing import Optional
from typing import Tuple

from offroad_routing.geometry.algorithms import check_ray_segment_intersection
from offroad_routing.geometry.algorithms import compare_points
from offroad_routing.geometry.algorithms import turn
from offroad_routing.geometry.geom_types import PointData
from offroad_routing.geometry.geom_types import TPoint
from offroad_routing.geometry.geom_types import TPolygon


def find_supporting_pair_brute(point, polygon, polygon_size, point_number):
    result = list()
    for i in range(polygon_size):
        pi = polygon[i]
        if point_number is not None and i == point_number:
            continue
        if turn(point, pi, polygon[(i - 1) % polygon_size]) * turn(point, pi, polygon[(i + 1) % polygon_size]) < 0:
            continue

        # check intersection with all other points
        for j in range(polygon_size):
            if j in (i - 1, i) or (point_number is not None and j in (point_number - 1, point_number)):
                continue
            if check_ray_segment_intersection(point, pi, polygon[j], polygon[j + 1]):
                break
        else:
            result.append(i)

    if len(result) != 2:
        return None
    point1, point2 = result
    return point1, point2


def find_restriction_pair(point: TPoint, polygon: TPolygon, point_number: int) -> Optional[Tuple[TPoint, TPoint]]:
    """
        Find pair of supporting points from point (part of polygon) to polygon in squared time.

        :param point: visibility point (x, y)
        :param polygon: convex, given counter-clockwise, first and last points must be equal
        :param point_number: sequence number of point in polygon
        :return: pair of supporting points or None if unable to find
    """

    polygon_size = len(polygon) - 1
    assert polygon_size >= 2
    assert compare_points(polygon[0], polygon[-1])

    supporting_pair = find_supporting_pair_brute(
        point, polygon, polygon_size, point_number)
    if supporting_pair is None:
        return None
    point1, point2 = supporting_pair
    return polygon[point1], polygon[point2]


def find_supporting_line(point: TPoint, polygon: TPolygon, polygon_number: int) -> Optional[List[PointData]]:
    """
        Find pair of supporting points from point (not a part of polygon) to polygon in squared time.

        :param point: visibility point (x, y)
        :param polygon: convex, given counter-clockwise, first and last points must be equal
        :param polygon_number: sequence number of polygon for PointData
        :return: list of PointData of points connecting supporting points or None if unable to find
    """

    polygon_size = len(polygon) - 1
    assert polygon_size >= 2
    assert compare_points(polygon[0], polygon[-1])

    supporting_pair = find_supporting_pair_brute(
        point, polygon, polygon_size, None)
    if supporting_pair is None:
        return None
    point1, point2 = supporting_pair

    line = list()
    if point2 - point1 > (polygon_size - 1) / 2:
        for i in range(point2, polygon_size):
            line.append((polygon[i], polygon_number, i, True, 0))
        for i in range(0, point1 + 1):
            line.append((polygon[i], polygon_number, i, True, 0))
    else:
        for i in range(point1, point2 + 1):
            line.append((polygon[i], polygon_number, i, True, 0))
    return line
