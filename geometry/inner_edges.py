from shapely.geometry import Polygon, LineString
from numpy import arange
from numpy.random import choice
from typing import Optional, Sequence, Union, TypeVar, List
TPoint = TypeVar("TPoint")
TPolygon = TypeVar("TPolygon")
PointData = TypeVar("PointData")


def inner_edges(point: TPoint, point_number: Optional[int], polygon: Sequence[TPolygon],
                polygon_number: int, inside_percent: Union[int, float]) -> List[PointData]:
    """
    Finds segments from point to polygon vertices which are strictly inside polygon
    if point is not a polygon vertex, finds all segments
    if point is a polygon vertex, finds diagonals to further vertices
    we should not add fully outer segments because they may intersect other polygons!
    now only outer polygon is processed => everywhere polygon[0] is used
    :param point_number: None if point is not a polygon vertex else number or vertex
    :param polygon: polygons (polygon[0] is outer, rest are inner)
    for each polygon first and last points must be equal
    :param polygon_number: additional info which will be returned in PointData
    :param inside_percent: probability of an inner edge to be added (from 0 to 1)
    :return: list of PointData tuples of each point forming an inner edge with point
    """
    assert 0 <= inside_percent <= 1

    edges_inside = list()
    size = len(polygon[0]) - 1

    # point is strictly in polygon
    if point_number is None:
        for i in range(size):
            if Polygon(polygon[0]).contains(LineString([point, polygon[0][i]])):

                # randomly choose segments to add with percentage
                if inside_percent == 1 or choice(arange(0, 2), p=[1 - inside_percent, inside_percent]) == 1:
                    edges_inside.append((polygon[0][i], polygon_number, i, True, 1))

        return edges_inside

    # connect last and first vertex
    if point_number == size - 1:
        return [(polygon[0][0], polygon_number, 0, True, 1)]

    for i in range(point_number + 1, size):

        # neighbour vertex in polygon
        if i == point_number + 1:
            edges_inside.append((polygon[0][i], polygon_number, i, True, 1))

        # check if a segment is inner with shapely
        if Polygon(polygon[0]).contains(LineString([point, polygon[0][i]])):

            # randomly choose diagonals to add with percentage
            if inside_percent == 1 or choice(arange(0, 2), p=[1 - inside_percent, inside_percent]) == 1:
                edges_inside.append((polygon[0][i], polygon_number, i, True, 1))

    return edges_inside
