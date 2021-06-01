from numpy import array, cross, dot
from math import fabs, atan2, pi


# from geopy.distance import geodesic
# points a and b given in format (lon, lat)
# def dist(a, b):
#     return geodesic((a[1], a[0]), (b[1], b[0])).km


# [ab, bc]
def turn(a, b, c):
    return cross(array(b) - array(a), array(c) - array(b))


# polar angle of vector ab
def angle(a, b):
    return (atan2(b[1] - a[1], b[0] - a[0]) + 2 * pi) % (2 * pi)


# check if point i is in angle (lpr)
def point_in_angle(i, l, p, r):
    if turn(l, p, r) > 0:
        return turn(p, l, i) < 0 < turn(p, r, i)
    return turn(p, r, i) < 0 < turn(p, l, i)


# find intersection point, then check if it belongs to a ray and a segment
def ray_intersects_segment(a0, b0, c0, d0, end_intersection=False):

    # relative coordinates
    a = array(a0)
    b = array(b0) - a
    c = array(c0) - a
    d = array(d0) - a

    # coordinates of segment
    x1, y1 = c
    x2, y2 = d

    # line equasions
    k12 = 10 ** 10 if x1 == x2 else (y1 - y2) / (x1 - x2)
    b12 = y1 - k12 * x1
    delta = 10 ** -7
    k = 10 ** 10 if fabs(b[0]) < delta else b[1] / b[0]

    # overlap is not an intersection
    if fabs(k - k12) < delta:
        return False

    # intersection point
    x = b12 / (k - k12)
    y = k * x

    # end of segment is an intersection
    if end_intersection:
        if x < min(x1, x2) - delta or x > max(x1, x2) + delta or y < min(y1, y2) - delta or y > max(y1, y2) + delta:
            return False

    # end of segment is NOT an intersection
    else:
        if x < min(x1, x2) + delta or x > max(x1, x2) - delta or y < min(y1, y2) + delta or y > max(y1, y2) - delta:
            return False
    return dot(array([x, y]), b) > 0


def compare_points(p1, p2, delta):
    return fabs(p1[0] - p2[0]) < delta and fabs(p1[1] - p2[1]) < delta


# O(n) algorithm
def point_in_ch_linear(point, polygon):
    n = len(polygon) - 1
    if n <= 2:
        return False
    polygon_turn = turn(polygon[0], polygon[1], polygon[2])
    for i in range(n):
        if turn(polygon[i], polygon[i + 1], point) * polygon_turn < 0:
            return False
    return True


# O(log n) Preparata Shamos algorithm
# polygon has to be given counter-clockwise
def point_in_ch(point, polygon, angles):

    if angles is None:
        return False

    # point equals [0] point of polygon
    if compare_points(point, polygon[0], 10 ** -10):
        return True

    # binary search
    point_angle = angle(polygon[0], point)
    mid = (len(angles) - 1) // 2
    low = 0
    high = len(angles) - 1
    while low <= high:
        if mid + 1 == len(angles):
            return False
        angle1 = angles[mid]
        angle2 = angles[mid + 1]

        # 2 angles contain zero-angle
        if angle1 > pi and angle2 < pi:
            if point_angle >= angle1 or point_angle <= angle2:
                return turn(polygon[mid + 1], polygon[mid + 2], point) >= 0
            if point_angle > pi:
                high = mid - 1
            if point_angle < pi:
                low = mid + 1
        else:
            if point_angle >= angle1 and point_angle <= angle2:
                return turn(polygon[mid + 1], polygon[mid + 2], point) >= 0
            if point_angle - pi > angle2:
                high = mid - 1
            elif point_angle + pi < angle1:
                low = mid + 1
            elif point_angle < angle1:
                high = mid - 1
            else:
                low = mid + 1
        mid = (high + low) // 2
    return False
