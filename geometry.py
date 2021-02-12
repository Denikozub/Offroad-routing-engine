import numpy as np
import math
from geopy.distance import geodesic


def vec(a, b):
    x_sign = 1 if b[0] - a[0] >= 0 else -1
    y_sign = 1 if b[1] - a[1] >= 0 else -1
    return np.array([x_sign * geodesic(a, (a[0], b[1])).km, y_sign * geodesic((a[0], b[1]), b).km])


def mod(v):
    return (v[0]**2 + v[1]**2)**0.5


def box_width(box):
    return dist([box[1], box[0]], [box[1], box[2]])


def box_length(box):
    return dist([box[1], box[0]], [box[3], box[0]])


def dist(a, b):
    return geodesic(a, b).km


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
    x = v[0]
    y = v[1]
    if x >= 0 and y >= 0:
        delta = 0
    elif x * y <= 0:
        delta = math.pi
    else:
        delta = 2 * math.pi
    return math.atan2(y, x) + delta


def turn(a, b, c):
    return np.cross(np.array(b) - np.array(a), np.array(c) - np.array(b))


def point_in_angle(i, l, p, r):
    if turn(l, p, r) > 0:
        return turn(p, l, i) < 0 < turn(p, r, i)
    return turn(p, r, i) < 0 < turn(p, l, i)


def inner_diag(i, j, polygon, n):
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
