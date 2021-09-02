from math import fabs
from typing import Optional, Sequence, TypeVar, List

from numpy import arange
from numpy.random import choice
from shapely.geometry import Polygon, LineString

TPoint = TypeVar("TPoint")  # Tuple[float, float]
TPolygon = TypeVar("TPolygon")  # Tuple[TPoint, ...]
PointData = TypeVar("PointData")  # Tuple[TPoint, Optional[int], Optional[int], Optional[bool], Optional[int]]


def find_inner_edges(point: TPoint, point_number: Optional[int], polygon: Sequence[TPolygon],
                     polygon_number: int, inside_percent: float) -> List[PointData]:
    """
    Finds segments from point to polygon vertices which are strictly inside polygon.
    If point is not a polygon vertex, finds all segments.
    If point is a polygon vertex, finds diagonals to further vertices.
    We should not add fully outer segments because they may intersect other polygons!
    Currently only outer polygon is processed => everywhere polygon[0] is used.

    :param point: point strictly inside outer polygon
    :param point_number: None if point is not a polygon vertex else number or vertex
    :param polygon: polygons (polygon[0] is outer, rest are inner), for each polygon first and last points must be equal
    :param polygon_number: additional info which will be returned in PointData
    :param inside_percent: probability of an inner edge to be added (from 0 to 1)
    :return: list of PointData tuples of each point forming an inner edge with point
    """
    assert 0 <= inside_percent <= 1

    edges_inside = list()
    polygon_size = len(polygon[0]) - 1

    # point is strictly in polygon
    if point_number is None:
        for i in range(polygon_size):
            if Polygon(polygon[0]).contains(LineString([point, polygon[0][i]])):
                if inside_percent == 1 or choice(arange(0, 2), p=[1 - inside_percent, inside_percent]) == 1:
                    edges_inside.append((polygon[0][i], polygon_number, i, True, 1))
        return edges_inside

    for i in range(polygon_size):
        if i == point_number:
            continue
        if fabs(i - point_number) in [1, polygon_size - 1]:
            edges_inside.append((polygon[0][i], polygon_number, i, True, 1))
            continue
        if Polygon(polygon[0]).contains(LineString([point, polygon[0][i]])):
            if inside_percent == 1 or choice(arange(0, 2), p=[1 - inside_percent, inside_percent]) == 1:
                edges_inside.append((polygon[0][i], polygon_number, i, True, 1))

    return edges_inside
