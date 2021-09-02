from typing import Optional, List, TypeVar, Tuple

from geometry.algorithms import ray_intersects_segment, turn, equal_points

TPoint = TypeVar("TPoint")  # Tuple[float, float]
TPolygon = TypeVar("TPolygon")  # Tuple[TPoint, ...]
PointData = TypeVar("PointData")  # Tuple[TPoint, Optional[int], Optional[int], Optional[bool], Optional[int]]


def find_supporting_pair_brute(point: TPoint, polygon: TPolygon, point_number: Optional[int]):
    assert equal_points(polygon[0], polygon[-1])
    polygon_size = len(polygon) - 1
    result = list()

    for i in range(polygon_size):
        pi = polygon[i]
        if point_number is not None and i == point_number:
            continue

        # cannot be supporting point
        if turn(point, pi, polygon[(i - 1) % polygon_size]) * turn(point, pi, polygon[(i + 1) % polygon_size]) < 0:
            continue

        # check intersection with all other points
        found = True
        for j in range(polygon_size):
            if j in (i - 1, i) or (point_number is not None and j in (point_number - 1, point_number)):
                continue
            if ray_intersects_segment(point, pi, polygon[j], polygon[j + 1], True):
                found = False
                break
        if found:
            result.append(i)

    if len(result) != 2:
        return None

    point1, point2 = result
    return point1, point2


def find_restriction_pair(point: TPoint, polygon: TPolygon, point_number: int) -> Optional[Tuple[TPoint, TPoint]]:
    supporting_pair = find_supporting_pair_brute(point, polygon, point_number)
    if supporting_pair is None:
        return None
    point1, point2 = supporting_pair
    return polygon[point1], polygon[point2]


def find_supporting_line(point: TPoint, polygon: TPolygon, polygon_number: int) -> Optional[List[PointData]]:
    polygon_size = len(polygon) - 1
    supporting_pair = find_supporting_pair_brute(point, polygon, None)
    if supporting_pair is None:
        return None
    point1, point2 = supporting_pair

    line = list()
    if point2 - point1 > (polygon_size - 1) / 2:
        for i in range(point2, polygon_size + 1):
            line.append((polygon[i], polygon_number, i, True, 0))
        for i in range(0, point1 + 1):
            line.append((polygon[i], polygon_number, i, True, 0))
    else:
        for i in range(point1, point2 + 1):
            line.append((polygon[i], polygon_number, i, True, 0))
    return line
