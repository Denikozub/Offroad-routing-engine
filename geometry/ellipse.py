from random import seed, randint

"""
This is an attempt to approximate a polygon with an ellipse
prune_geometry() must be changed to store coordinates of a bbox instead of a convex hull
This requires usage of a specialized function find_pair_ellipse() to find a pair of supporting lines
find_pair_ellipse() finds it in O(1) time, which allows to speed up the algorithm
Current implementation does not work properly
"""


def quad_equation(a, b, c):
    if a == 0:
        return -c / b
    d = b**2 - 4 * a * c
    if d < 0:
        return None
    elif d == 0:
        return -b / (2 * a), -b / (2 * a)
    return (-b + d**0.5) / (2 * a), (-b - d**0.5) / (2 * a)


def find_pair_ellipse(point, polygon, polygon_number=None):
    mult = 1e7
    a, b = (polygon[2][0] - polygon[1][0]) / 2 * mult, (polygon[1][1] - polygon[0][1]) / 2 * mult
    xc, yc = (polygon[2][0] + polygon[1][0]) / 2 * mult, (polygon[1][1] + polygon[0][1]) / 2 * mult
    x0, y0 = point[0] * mult - xc, point[1] * mult - yc
    y = quad_equation(b**2 + y0**2 * a**2 / x0**2, -2 * y0 * b**2 * a**2 / x0**2, -b**4 + a**2 * b**2 / x0**2)
    if y is None:
        return None
    x1, x2 = (1 - y0 * y[0] / b**2) * a**2 / x0, (1 - y0 * y[1] / b**2) * a**2 / x0
    point1, point2 = ((x1 + xc) / mult, (y[0] + yc) / mult), ((x2 + xc) / mult, (y[1] + yc) / mult)
    seed(1)
    return (point1, polygon_number, randint(5000, 9999), True, 0), (point2, polygon_number, randint(5000, 9999), True, 0)
