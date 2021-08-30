from math import fabs, atan2, pi
from typing import TypeVar

from geopy.distance import geodesic
from numpy import isclose

TPoint = TypeVar("TPoint")  # Tuple[float, float]


# points a and b given in format (lon, lat)
def point_distance(a: TPoint, b: TPoint) -> float:
    return geodesic((a[1], a[0]), (b[1], b[0])).km


def cross_product(p: TPoint, q: TPoint) -> float:
    return p[0] * q[1] - p[1] * q[0]


def turn(a: TPoint, b: TPoint, c: TPoint) -> float:
    return (b[0] - a[0]) * (c[1] - b[1]) - (b[1] - a[1]) * (c[0] - b[0])


# polar angle of vector ab (0 to 2*pi)
def polar_angle(a: TPoint, b: TPoint) -> float:
    return (atan2(b[1] - a[1], b[0] - a[0]) + 2 * pi) % (2 * pi)


# check if point is in sector (lpr < pi) formed by points
def point_in_sector(point: TPoint, l: TPoint, p: TPoint, r: TPoint) -> bool:
    if turn(l, p, r) > 0:
        return turn(p, l, point) < 0 < turn(p, r, point)
    return turn(p, r, point) < 0 < turn(p, l, point)


def segments_intersect(a0: TPoint, b0: TPoint, c0: TPoint, d0: TPoint) -> bool:
    return turn(a0, b0, c0) * turn(a0, b0, d0) < 0 and \
           turn(c0, d0, a0) * turn(c0, d0, b0) < 0


# ray ab intersects line segment cd
def ray_intersects_segment(p: TPoint, b: TPoint, q: TPoint, d: TPoint, end_intersection: bool = False) -> bool:
    r, s = (b[0] - p[0], b[1] - p[1]), (d[0] - q[0], d[1] - q[1])
    pq = q[0] - p[0], q[1] - p[1]
    r_cross_s = cross_product(r, s)
    if fabs(r_cross_s) < 1e-8:
        return False
    t = cross_product(pq, s) / r_cross_s
    u = cross_product(pq, r) / r_cross_s
    return 0 <= t and 0 <= u <= 1 if end_intersection else 0 < t and 0 < u < 1


def equal_points(p1: TPoint, p2: TPoint) -> bool:
    return isclose(p1, p2).all()
