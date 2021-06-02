from geometry.algorithm import angle, compare_points, turn
from math import pi


def point_in_ch_linear(point, polygon):
    """
    locating point inside convex polygon O(n) algorithm
    :param point: iterable of x, y
    :param polygon: iterable of points (polygon[0] == polygon[-1])
    :return: bool - point is inside polygon
    """
    iter(point)
    iter(polygon)

    n = len(polygon) - 1
    if n <= 2:
        return False
    polygon_turn = turn(polygon[0], polygon[1], polygon[2])
    for i in range(n):
        if turn(polygon[i], polygon[i + 1], point) * polygon_turn < 0:
            return False
    return True


def point_in_ch(point, polygon, angles, reverse_angle=False):
    """
    locating point inside convex polygon O(log n) Preparata Shamos algorithm
    :param point: iterable of x, y
    :param polygon: iterable of points (polygon[0] == polygon[-1]) given counter-clockwise
    :param angles: tuple of polar angles from first point to others or None if polygon is a segment or a point
    :param reverse_angle: bool - point_angle should be turned on pi
    :return: tuple of 2 elements:
        bool - point is inside polygon
        None if 0 element == False else int - number of polygon vertex where point_angle is located
    """

    if angles is None:
        return False, None

    iter(point)
    iter(polygon)
    iter(angles)

    if type(reverse_angle) != bool:
        raise TypeError("wrong reverse_angle type")

    # point equals [0] point of polygon
    if compare_points(point, polygon[0], 10 ** -10):
        return True, None

    point_angle = angle(point, polygon[0]) if reverse_angle else angle(polygon[0], point)

    # point angle not between angles
    if angles[-1] < pi < angles[0]:
        if angles[-1] < point_angle < angles[0]:
            return False, None
    elif point_angle < angles[0] or point_angle > angles[-1]:
        return False, None

    # binary search
    mid = (len(angles) - 1) // 2
    low = 0
    high = len(angles) - 1
    while low <= high:
        if mid + 1 == len(angles):
            return False, None
        angle1 = angles[mid]
        angle2 = angles[mid + 1]

        # 2 angles contain zero-angle
        if angle1 > pi > angle2:
            if point_angle >= angle1 or point_angle <= angle2:
                return turn(polygon[mid + 1], polygon[mid + 2], point) >= 0, mid + 2
            if point_angle > pi:
                high = mid - 1
            if point_angle < pi:
                low = mid + 1
        else:
            if angle1 <= point_angle <= angle2:
                return turn(polygon[mid + 1], polygon[mid + 2], point) >= 0, mid + 2
            if point_angle - pi > angle2:
                high = mid - 1
            elif point_angle + pi < angle1:
                low = mid + 1
            elif point_angle < angle1:
                high = mid - 1
            else:
                low = mid + 1
        mid = (high + low) // 2
    return False, None