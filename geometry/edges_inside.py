from shapely.geometry import Polygon, LineString
from numpy import arange
from numpy.random import choice


def edge_inside_poly(point, point_number, polygon, polygon_number, inside_percent):
    """
    finds segments from point to polygon vertices which are strictly inside polygon
    if point is not a polygon vertex, finds all segments
    if point is a polygon vertex, finds diagonals to further vertices
    :param point: iterable of x, y
    :param point_number: None if point is not a polygon vertex else number or vertex
    :param polygon: iterable of points (polygon[0] == polygon[-1])
    :param polygon_number: additional info which will be returned in point_data
    :param inside_percent: float parameter setting the probability of an inner edge to be added (from 0 to 1)
    :return: list of point_data tuples of each point forming an inner edge with point
    point_data is a tuple where:
        0 element: point coordinates - tuple of x, y
        1 element: number of object where point belongs
        2 element: number of point in object
        3 element: if object is polygon (1) or linestring (0)
        4 element: surface type (0 - edge between objects, 1 - edge inside polygon, 2 - road edge)
    """
    iter(point)
    iter(polygon)

    if point_number is not None:
        if type(point_number) not in {float, int}:
            raise TypeError("wrong point_number type")

    if type(polygon_number) not in {float, int}:
        raise TypeError("wrong polygon_number type")

    if type(inside_percent) not in {float, int}:
        raise TypeError("wrong inside_percent type")

    if 0 < inside_percent > 1:
        raise ValueError("wrong inside_percent value")

    edges_inside = list()
    size = len(polygon) - 1

    # point is strictly in polygon
    if point_number is None:
        for i in range(size):
            if Polygon(polygon).contains(LineString([point, polygon[i]])):

                # randomly choose segments to add with percentage
                if inside_percent == 1 or choice(arange(0, 2), p=[1 - inside_percent, inside_percent]) == 1:
                    edges_inside.append((polygon[i], polygon_number, i, True, 1))

        return edges_inside

    # connect last and first vertex
    if point_number == size - 1:
        return [(polygon[0], polygon_number, 0, True, 1)]

    for i in range(point_number + 1, size):

        # neighbour vertex in polygon
        if i == point_number + 1:
            edges_inside.append((polygon[i], polygon_number, i, True, 1))

        # check if a segment is inner with shapely
        if Polygon(polygon).contains(LineString([point, polygon[i]])):

            # randomly choose diagonals to add with percentage
            if inside_percent == 1 or choice(arange(0, 2), p=[1 - inside_percent, inside_percent]) == 1:
                edges_inside.append((polygon[i], polygon_number, i, True, 1))

            # we should not add fully outer segments because they may intersect other polygons!!!!!

    return edges_inside
