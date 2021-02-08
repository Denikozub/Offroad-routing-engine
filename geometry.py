import numpy as np
import math


def vec(a, b):
    return np.array(b) - np.array(a)


def mod(v):
    return (v[0]**2 + v[1]**2)**0.5


def angle(a, b, c):
    mods = mod(vec(b, a)) * mod(vec(b, c))
    if mods == 0:
        return 1
    cos = np.dot(vec(b, a), vec(b, c)) / mods
    if math.fabs(cos) > 1:
        return 1
    return math.acos(cos)


def turn(a, b, c):
    return np.cross(np.array(b) - np.array(a), np.array(c) - np.array(b))


def point_in_angle(i, l, p, r):
    if turn(l, p, r) > 0:
        return turn(p, l, i) < 0 < turn(p, r, i)
    else:
        return turn(p, r, i) < 0 < turn(p, l, i)
