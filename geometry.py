import numpy as np
import math
from geopy.distance import geodesic


def dist(a, b):
    return geodesic((a[1], a[0]), (b[1], b[0])).km


def vec(a, b):
    x_sign = 1 if b[0] - a[0] >= 0 else -1
    y_sign = 1 if b[1] - a[1] >= 0 else -1
    return np.array([x_sign * dist(b, (a[0], b[1])), y_sign * dist((a[0], b[1]), a)])


def mod(v):
    return (v[0]**2 + v[1]**2)**0.5


def box_width(box):
    return dist([box[1], box[0]], [box[1], box[2]])


def box_length(box):
    return dist([box[1], box[0]], [box[3], box[0]])


def angle(a, b, c):
    mods = mod(vec(b, a)) * mod(vec(b, c))
    if mods == 0:
        return 1
    cos = np.dot(vec(b, a), vec(b, c)) / mods
    if math.fabs(cos) > 1:
        return 1
    return math.acos(cos)


def angle_horizontal(a, b):
    v = vec(a, b)
    return math.atan2(v[1], v[0])


def turn(a, b, c):
    return np.cross(np.array(b) - np.array(a), np.array(c) - np.array(b))


def point_in_angle(i, l, p, r):
    if turn(l, p, r) > 0:
        return turn(p, l, i) < 0 < turn(p, r, i)
    return turn(p, r, i) < 0 < turn(p, l, i)


def intersects(a0, b0, c0, d0, segment=False):
    a = np.array(a0)
    b = np.array(b0) - a
    c = np.array(c0) - a
    d = np.array(d0) - a
    x1, y1 = c
    x2, y2 = d
    k12 = 10 ** 10 if x1 == x2 else (y1 - y2) / (x1 - x2)
    b12 = y1 - k12 * x1
    delta = 0.0000000001
    k = 10 ** 10 if math.fabs(b[0]) < delta else b[1] / b[0]
    if math.fabs(k - k12) < delta:
        return False  # overlap not an intersection
    x = b12 / (k - k12)
    y = k * x
    if x < min(x1, x2) + delta or x > max(x1, x2) - delta or y < min(y1, y2) + delta or y > max(y1, y2) - delta:
        return False  # end of segment not an intersection
    if not segment:
        return np.dot(np.array([x, y]), b) > 0
    return x > min(0, b[0]) + delta and x < max(0, b[0]) - delta and y > min(0, b[1]) + delta and y < max(0, b[1]) - delta


def point_in_ch(point, polygon):
    n = len(polygon) - 1
    if n <= 2:
        return False
    polygon_turn = turn(polygon[0], polygon[1], polygon[2])
    for i in range(n):
        if turn(polygon[i], polygon[i + 1], point) * polygon_turn < 0:
            return False
    return True


def inner_diag(p1, p2, polygon, n):
    if math.fabs(p1 - p2) in (0, 1, n):
        return True
    point1 = polygon[p1]
    point2 = polygon[p2]
    n = len(polygon) - 1
    if turn(point1, point2, polygon[(p2 - 1) % n]) * turn(point1, point2, polygon[(p2 + 1) % n]) >= 0 or \
            turn(point2, point1, polygon[(p1 - 1) % n]) * turn(point2, point1, polygon[(p1 + 1) % n]) >= 0:
        return False   
    for i in range(n):
        if i in (p1, p1 - 1, p2, p2 - 1):
            continue
        if intersects(point1, point2, polygon[i], polygon[i + 1], segment=True):
            return False
    return True

