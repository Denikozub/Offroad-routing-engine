from geometry import point_in_angle, ray_intersects_segment, turn
from shapely.geometry import Polygon, LineString
from math import sqrt
import random


# O(log n) algorithm found, will be implemented in the future


# find a pair of supporting points from point to a convex polygon
# O(n) use of array implementation
def find_pair_array(point, polygon, polygon_number):
    n = len(polygon) - 1
    if n == 2:
        start = 0
        end = 1
    else:
        b = [1 for i in range(n)]
        count = 0
        for i in range(n):
            if not point_in_angle(point, polygon[(i-1) % n], polygon[i % n], polygon[(i+1) % n]):
                b[i] = 0
                count += 1
        if count in (0, n):
            return None
        if b[0] == 1:
            start = b.index(0, 1)
            if b[n-1] == 0:
                end = n-1
            else:
                end = b.index(1, start + 1)
                end -= 1
        else:
            start = b.index(1, 1)
            start -= 1
            if b[n-1] == 1:
                end = n
            else:
                end = b.index(0, start + 1)
    return (polygon[start], polygon_number, start, True, 0), \
           (polygon[end], polygon_number, end, True, 0)


# find a pair of supporting points from point to a convex polygon
# O(n) NO use of array implementation
def find_pair_cutoff(point, polygon, polygon_number):
    n = len(polygon) - 1
    if n == 2:
        begin = 0
        end = 1
        found = True
    else:
        begin = end = -1
        found = False
        for i in range(n):
            if not point_in_angle(point, polygon[(i-1) % n], polygon[i % n], polygon[(i+1) % n]):
                if i == 0:
                    start_zero = True
                if begin == -1 and not start_zero:
                    begin = i
                if start_zero and end != -1:
                    begin = i
                    found = True
                    break
                if not start_zero and i == n - 1:
                    end = n - 1
                    found = True
                    break
            else:
                if i == 0:
                    start_zero = False
                if begin != -1 and not start_zero:
                    end = (i-1) % n
                    found = True
                    break
                if start_zero and end == -1:
                    end = (i-1) % n
                if start_zero and i == n - 1:
                    begin = n
                    found = True
                    break
    return None if not found else ((polygon[begin], polygon_number, begin, True, 0), \
           (polygon[end], polygon_number, end, True, 0))


# find a pair of supporting points from point to a non-convex polygon
# O(n^2) brute force implementation
def find_line_brute_force(point, polygon, polygon_number, polygon_point_number=None):
    n = len(polygon) - 1
    result = list()
    for i in range(n):
        pi = polygon[i]
        if polygon_point_number is not None and i == polygon_point_number:
            continue
        if turn(point, pi, polygon[(i - 1) % n]) * turn(point, pi, polygon[(i + 1) % n]) < 0:
            continue
        found = True
        for j in range(n):
            if j in (i - 1, i) or (polygon_point_number is not None and j in (polygon_point_number - 1, polygon_point_number)):
                continue
            if ray_intersects_segment(point, pi, polygon[j], polygon[j + 1]):
                found = False
                break
        if found:
            result.append(i)
    if len(result) != 2:
        return None
    point1, point2 = result
    if polygon_point_number is not None:
        return polygon[point1], polygon[point2]
    line = list()
    outter = True
    for i in range(point1 + 1, point2):
        if not LineString([point, polygon[i]]).crosses(Polygon(polygon)):
            outter = False
    if outter:
        for i in range(point2, n + 1):
            line.append((polygon[i], polygon_number, i, True, 0))
        for i in range(0, point1 + 1):
            line.append((polygon[i], polygon_number, i, True, 0))
    else:
        for i in range(point1, point2 + 1):
            line.append((polygon[i], polygon_number, i, True, 0))
    return line

