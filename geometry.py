from numpy import array, cross, dot
from math import fabs
# from geopy.distance import geodesic


# points a and b given in format (lon, lat)
# def dist(a, b):
#     return geodesic((a[1], a[0]), (b[1], b[0])).km


# [ab, bc]
def turn(a, b, c):
    return cross(array(b) - array(a), array(c) - array(b))


# check if point i is in angle (lpr)
def point_in_angle(i, l, p, r):
    if turn(l, p, r) > 0:
        return turn(p, l, i) < 0 < turn(p, r, i)
    return turn(p, r, i) < 0 < turn(p, l, i)


# find intersection point, then check if it belongs to a ray and a segment
def ray_intersects_segment(a0, b0, c0, d0):
    a = array(a0)
    b = array(b0) - a
    c = array(c0) - a
    d = array(d0) - a
    x1, y1 = c
    x2, y2 = d
    k12 = 10 ** 10 if x1 == x2 else (y1 - y2) / (x1 - x2)
    b12 = y1 - k12 * x1
    delta = 0.00000000001
    k = 10 ** 10 if fabs(b[0]) < delta else b[1] / b[0]
    if fabs(k - k12) < delta:
        return False  # overlap not an intersection
    x = b12 / (k - k12)
    y = k * x
    if x < min(x1, x2) + delta or x > max(x1, x2) - delta or y < min(y1, y2) + delta or y > max(y1, y2) - delta:
        return False  # end of segment not an intersection
    return dot(array([x, y]), b) > 0


def compare_points(p1, p2, delta):
    return p1[0] - p2[0] < delta and p1[1] - p2[1] < delta


# O(n) algorithm
# O(log n) implementation in the future
def point_in_ch(point, polygon):
    n = len(polygon) - 1
    if n <= 2:
        return False
    polygon_turn = turn(polygon[0], polygon[1], polygon[2])
    for i in range(n):
        if turn(polygon[i], polygon[i + 1], point) * polygon_turn < 0:
            return False
    return True

