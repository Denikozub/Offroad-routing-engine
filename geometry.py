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


def intersects(a0, b0, c0, d0):
    a = np.array(a0)
    b = np.array(b0) - a
    c = np.array(c0) - a
    d = np.array(d0) - a
    x1, y1 = c
    x2, y2 = d
    k12 = 10 ** 10 if x1 == x2 else (y1 - y2) / (x1 - x2)
    b12 = y1 - k12 * x1
    k = 10 ** 10 if math.fabs(b[0]) < delta else b[1] / b[0]
    if k == k12:
        return False  # overlap not an intersection
    x = b12 / (k - k12)
    y = k * x
    if x < min(x1, x2) or x > max(x1, x2) or y < min(y1, y2) or y > max(y1, y2):
        return False  # end of segment not an intersection
    return np.dot(np.array([x, y]), b) > 0


def inner_diag(i, j, polygon, n):
    if math.fabs(i - j) <= 1:
        return True
    pi = polygon[i]
    pj = polygon[j]
    pi_l = polygon[(i - 1) % n]
    pi_r = polygon[(i + 1) % n]
    if turn(pi_l, pi, pi_r) < 0:
        if turn(pi, pj, pi_l) > 0 or turn(pi, pi_r, pj) > 0:
            return False
        for k in range(n):
            pk = polygon[k]
            if (k > i or k < j) and turn(pi, pk, pj) > 0:
                return False
            if j < k < i and turn(pi, pj, pk) > 0:
                return False
        return True
    else:
        if turn(pi, pj, pi_r) < 0 or turn(pi, pi_l, pj) < 0:
            return False
        for k in range(n):
            pk = polygon[k]
            if (k > i or k < j) and turn(pi, pj, pk) < 0:
                return False
            if j < k < i and turn(pi, pk, pj) < 0:
                return False
        return True
