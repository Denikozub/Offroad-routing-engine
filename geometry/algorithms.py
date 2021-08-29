from math import fabs, atan2, pi
from typing import TypeVar

from geopy.distance import geodesic
from numpy import array, cross, dot, isclose

TPoint = TypeVar("TPoint")  # Tuple[float, float]


# points a and b given in format (lon, lat)
def point_distance(a: TPoint, b: TPoint) -> float:
    return geodesic((a[1], a[0]), (b[1], b[0])).km


def cross_product(a: TPoint, b: TPoint, c: TPoint) -> float:
    return float(cross(array(b) - array(a), array(c) - array(b)))


# polar angle of vector ab (0 to 2*pi)
def polar_angle(a: TPoint, b: TPoint) -> float:
    return (atan2(b[1] - a[1], b[0] - a[0]) + 2 * pi) % (2 * pi)


# check if point is in sector (lpr < pi) formed by points
def point_in_sector(point: TPoint, l: TPoint, p: TPoint, r: TPoint) -> bool:
    if cross_product(l, p, r) > 0:
        return cross_product(p, l, point) < 0 < cross_product(p, r, point)
    return cross_product(p, r, point) < 0 < cross_product(p, l, point)


# ray a0b0 intersects line segment c0d0
def ray_intersects_segment(a0: TPoint, b0: TPoint, c0: TPoint, d0: TPoint, end_intersection: bool = False) -> bool:
    delta = 1e-7
    a = array(a0)
    b, c, d = array(b0) - a, array(c0) - a, array(d0) - a
    (x1, y1), (x2, y2) = c, d

    k12 = 1e10 if x1 == x2 else (y1 - y2) / (x1 - x2)
    b12 = y1 - k12 * x1
    k = 1e10 if fabs(b[0]) < delta else b[1] / b[0]

    # overlap is not an intersection
    if fabs(k - k12) < delta:
        return False

    x = b12 / (k - k12)
    y = k * x

    if end_intersection:
        if x < min(x1, x2) - delta or x > max(x1, x2) + delta or y < min(y1, y2) - delta or y > max(y1, y2) + delta:
            return False
    elif x < min(x1, x2) + delta or x > max(x1, x2) - delta or y < min(y1, y2) + delta or y > max(y1, y2) - delta:
        return False
    return dot(array([x, y]), b) > 0


def equal_points(p1: TPoint, p2: TPoint) -> bool:
    return isclose(p1, p2).all()
