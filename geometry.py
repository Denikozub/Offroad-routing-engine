import numpy as np
import math
from geopy.distance import geodesic


def dist(a, b):
    return geodesic((a[1], a[0]), (b[1], b[0])).km


def vec(a, b):
    x_sign = 1 if b[0] - a[0] >= 0 else -1
    y_sign = 1 if b[1] - a[1] >= 0 else -1
    return np.array([x_sign * dist(a, (a[0], b[1])), y_sign * dist((a[0], b[1]), b)])


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
    x = v[0]
    y = v[1]
    delta = 0.000001
    if math.fabs(x) < delta:
        if y > delta:
            return math.pi / 2
        if y < -delta:
            return 3 * math.pi / 2
        return 0
    if math.fabs(y) < delta:
        if x > delta:
            return 0
        return math.pi
    if x >= 0 and y >= 0:
        delta = 0
    elif x * y <= 0:
        delta = math.pi
    else:
        delta = 2 * math.pi
    angle = math.pi / 2 - math.atan2(y, x) + delta
    if angle < 0:
        angle += math.pi * 2
    if angle >= 2 * math.pi:
        angle -= math.pi * 2
    return angle


def turn(a, b, c):
    return np.cross(np.array(b) - np.array(a), np.array(c) - np.array(b))


def point_in_angle(i, l, p, r):
    if turn(l, p, r) > 0:
        return turn(p, l, i) < 0 < turn(p, r, i)
    return turn(p, r, i) < 0 < turn(p, l, i)


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
