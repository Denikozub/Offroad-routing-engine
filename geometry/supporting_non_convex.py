from geometry.geometry import ray_intersects_segment, turn

# find a pair of supporting points from point to a non-convex polygon
# if supporting points were not found return None
# returns a tuple of coordinates of 2 supporting points if polygon_point_number is None
# returns a list of point_data tuples of points connecting 2 supporting points else
# O(n^2) brute force implementation

def find_line_brute_force(point, polygon, polygon_number, polygon_point_number=None):
    n = len(polygon) - 1
    result = list()

    # loop over all points of a polygon
    for i in range(n):
        pi = polygon[i]

        # point equals current point
        if polygon_point_number is not None and i == polygon_point_number:
            continue

        # cannot be supporting point
        if turn(point, pi, polygon[(i - 1) % n]) * turn(point, pi, polygon[(i + 1) % n]) < 0:
            continue
        found = True

        # check intersection with all other points
        for j in range(n):
            if j in (i - 1, i) or (polygon_point_number is not None and j in (polygon_point_number - 1, polygon_point_number)):
                continue
            if ray_intersects_segment(point, pi, polygon[j], polygon[j + 1]):
                found = False
                break
        if found:
            result.append(i)

    # did not find 2 supporting points
    if len(result) != 2:
        return None

    # return restriction pair if point is part of polygon
    point1, point2 = result
    if polygon_point_number is not None:
        return polygon[point1], polygon[point2]

    # add shortest line from one point to another
    line = list()
    if point2 - point1 > (n - 1) / 2:
        for i in range(point2, n + 1):
            line.append((polygon[i], polygon_number, i, True, 0))
        for i in range(0, point1 + 1):
            line.append((polygon[i], polygon_number, i, True, 0))
    else:
        for i in range(point1, point2 + 1):
            line.append((polygon[i], polygon_number, i, True, 0))
    return line

