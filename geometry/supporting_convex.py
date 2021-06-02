from geometry.algorithm import point_in_angle, turn
from geometry.locate_convex import point_in_ch

"""
all algorithms work with quality of convex polygon in respect to a point
angles of polygon and semi-planes forming the polygon are sorted by the fact of containing the point
therefore 2 subsets are formed, point dividing them are supporting points
"""


def binary_search(point, polygon, low, high, low_contains):
    polygon_size = len(polygon) - 1
    mid = (high + low) // 2
    while low <= high:
        if mid + 1 == polygon_size:
            break
        if turn(polygon[mid], polygon[(mid + 1) % polygon_size], point) >= 0 and low_contains or \
                turn(polygon[mid], polygon[(mid + 1) % polygon_size], point) < 0 and not low_contains:
            low = mid + 1
        else:
            high = mid - 1
        mid = (high + low) // 2
    return mid


def find_pair(point, polygon, polygon_number, angles):
    """
    find a pair of supporting points from point to a convex polygon
    O(log n) Denis denikozub Kozub binary search through semi-planes algorithm
    :param point: iterable of x, y
    :param polygon: iterable of points (polygon[0] == polygon[-1]) given counter-clockwise
    :param polygon_number: additional info which will be returned in point_data
    :param angles: tuple of polar angles from first point to others or None if polygon is a segment or a point
    :return: None if supporting points were not found
             a tuple of point_data tuples of 2 supporting points else
    point_data is a tuple where:
        0 element: point coordinates - tuple of x, y
        1 element: number of object where point belongs
        2 element: number of point in object
        3 element: if object is polygon (1) or linestring (0)
        4 element: surface type (0 - edge between objects, 1 - edge inside polygon, 2 - road edge)
    """
    if angles is None:
        if len(polygon) == 2:
            return None
        return (polygon[0], polygon_number, 0, True, 0), (polygon[1], polygon_number, 1, True, 0)
    
    iter(point)
    iter(polygon)
    iter(angles)

    if type(polygon_number) not in {float, int}:
        raise TypeError("wrong polygon_number type")

    start_to_point = point_in_ch(point, polygon, angles, False)

    # ray polygon[0], point intersects polygon
    if start_to_point[1] is not None:
        index1 = binary_search(point, polygon, 0, start_to_point[1], True)
        index2 = binary_search(point, polygon, start_to_point[1], len(polygon) - 2, True)
    else:
        point_to_start = point_in_ch(point, polygon, angles, True)

        # ray polygon[0], point does not intersect polygon
        if point_to_start[1] is not None:
            index1 = binary_search(point, polygon, 0, point_to_start[1], False)
            index2 = binary_search(point, polygon, point_to_start[1], len(polygon) - 2, False)

        # polygon[0] is supporting point
        else:
            index1 = 0
            index2 = binary_search(point, polygon, 1, len(polygon) - 2, turn(polygon[0], polygon[1], point) >= 0)

    return (polygon[index1], polygon_number, index1, True, 0), (polygon[index2], polygon_number, index2, True, 0)


def find_pair_array(point, polygon, polygon_number, _):
    """
    find a pair of supporting points from point to a convex polygon
    O(n) Denis denikozub Kozub use of array of angles implementation
    :param point: iterable of x, y
    :param polygon: iterable of points (polygon[0] == polygon[-1])
    :param polygon_number: additional info which will be returned in point_data
    :return: None if supporting points were not found
             a tuple of point_data tuples of 2 supporting points else
    point_data is a tuple where:
        0 element: point coordinates - tuple of x, y
        1 element: number of object where point belongs
        2 element: number of point in object
        3 element: if object is polygon (1) or linestring (0)
        4 element: surface type (0 - edge between objects, 1 - edge inside polygon, 2 - road edge)
    """
    iter(point)
    iter(polygon)

    if type(polygon_number) not in {float, int}:
        raise TypeError("wrong polygon_number type")

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


def find_pair_cutoff(point, polygon, polygon_number, _):
    """
    find a pair of supporting points from point to a convex polygon
    O(n) Denis denikozub Kozub NO use of array of angles implementation
    :param point: iterable of x, y
    :param polygon: iterable of points (polygon[0] == polygon[-1])
    :param polygon_number: additional info which will be returned in point_data
    :return: None if supporting points were not found
             a tuple of point_data tuples of 2 supporting points else
    point_data is a tuple where:
        0 element: point coordinates - tuple of x, y
        1 element: number of object where point belongs
        2 element: number of point in object
        3 element: if object is polygon (1) or linestring (0)
        4 element: surface type (0 - edge between objects, 1 - edge inside polygon, 2 - road edge)
    """
    iter(point)
    iter(polygon)

    if type(polygon_number) not in {float, int}:
        raise TypeError("wrong polygon_number type")

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
