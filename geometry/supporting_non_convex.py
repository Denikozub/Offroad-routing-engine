from geometry.algorithm import ray_intersects_segment, turn


def find_line_brute_force(point, polygon, polygon_number, point_number=None):
    """
    find a pair of supporting points from point to a non-convex polygon, O(n^2) brute force
    :param point: iterable of x, y
    :param polygon: iterable of points (polygon[0] == polygon[-1])
    :param polygon_number: additional info which will be returned in point_data
    :param point_number: None if point is not a polygon vertex else number or vertex
    :return: None if supporting points were not found
             a tuple of coordinates of 2 supporting points if polygon_point_number is None
             a list of point_data tuples of points connecting 2 supporting points else
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
            if j in (i - 1, i) or (point_number is not None and j in
                                   (point_number - 1, point_number)):
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
