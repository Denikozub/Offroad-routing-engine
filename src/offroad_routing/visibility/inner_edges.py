from math import fabs
from typing import List
from typing import Optional
from typing import Sequence

from numpy import arange
from numpy.random import choice
from offroad_routing.geometry.algorithms import compare_points
from offroad_routing.geometry.geom_types import PointData
from offroad_routing.geometry.geom_types import TPoint
from offroad_routing.geometry.geom_types import TPolygon
from shapely.geometry import LineString
from shapely.geometry import Polygon


def find_inner_edges(point: TPoint, point_number: Optional[int], polygon: Sequence[TPolygon],
                     polygon_number: int, inside_percent: float, weight: int) -> List[PointData]:
    """
    Finds segments from point to polygon vertices which are strictly inside polygon.
    If point is not a polygon vertex, finds all segments.
    If point is a polygon vertex, finds diagonals to further vertices.
    Currently only outer polygon is processed => everywhere polygon[0] is used.

    :param point: point strictly inside outer polygon (x, y)
    :param point_number: None if point is not a polygon vertex else number or vertex
    :param polygon: polygons (polygon[0] is outer, rest are inner), for each polygon first and last points must be equal
    :param polygon_number: sequence number of polygon for PointData
    :param inside_percent: (from 0 to 1) - controls the number of inner polygon edges
    :param weight: surface weight for PointData
    :return: list of PointData tuples of each point forming an inner edge with point
    """

    assert 0 <= inside_percent <= 1
    polygon_size = len(polygon[0]) - 1
    assert polygon_size >= 2
    assert compare_points(polygon[0][0], polygon[0][-1])

    edges_inside = list()

    # point is strictly in polygon
    if point_number is None:
        for i in range(polygon_size):
            if Polygon(polygon[0]).contains(LineString([point, polygon[0][i]])):
                if inside_percent == 1 or choice(arange(0, 2), p=[1 - inside_percent, inside_percent]) == 1:
                    edges_inside.append(
                        (polygon[0][i], polygon_number, i, True, weight))
        return edges_inside

    for i in range(polygon_size):
        if i == point_number:
            continue
        if fabs(i - point_number) in [1, polygon_size - 1]:
            edges_inside.append(
                (polygon[0][i], polygon_number, i, True, weight))
            continue
        if Polygon(polygon[0]).contains(LineString([point, polygon[0][i]])):
            if inside_percent == 1 or choice(arange(0, 2), p=[1 - inside_percent, inside_percent]) == 1:
                edges_inside.append(
                    (polygon[0][i], polygon_number, i, True, weight))

    return edges_inside
