from math import fabs, atan2, pi
from typing import TypeVar

from geopy.distance import geodesic
from numpy import array, cross, dot, isclose

TPoint = TypeVar("TPoint")  # Tuple[float, float]


# points a and b given in format (lon, lat)
def dist(a: TPoint, b: TPoint) -> float:
    return geodesic((a[1], a[0]), (b[1], b[0])).km


# [ab, bc]
def turn(a: TPoint, b: TPoint, c: TPoint) -> float:
    return float(cross(array(b) - array(a), array(c) - array(b)))


# polar angle of vector ab
def angle(a: TPoint, b: TPoint) -> float:
    return (atan2(b[1] - a[1], b[0] - a[0]) + 2 * pi) % (2 * pi)


# check if point i is in angle (lpr)
def point_in_angle(i: TPoint, l: TPoint,
                   p: TPoint, r: TPoint) -> bool:
    if turn(l, p, r) > 0:
        return turn(p, l, i) < 0 < turn(p, r, i)
    return turn(p, r, i) < 0 < turn(p, l, i)


# find intersection point, then check if it belongs to a ray and a segment
def ray_intersects_segment(a0: TPoint, b0: TPoint, c0: TPoint,
                           d0: TPoint, end_intersection: bool = False) -> bool:

    # relative coordinates
    a = array(a0)
    b = array(b0) - a
    c = array(c0) - a
    d = array(d0) - a

    # coordinates of segment
    x1, y1 = c
    x2, y2 = d

    # line equations
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


# p1 == p2
def compare_points(p1: TPoint, p2: TPoint) -> bool:
    return isclose(p1, p2).all()
