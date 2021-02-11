import networkx as nx
import matplotlib.pyplot as plt
from geometry import *


def find_pair_array(point, left_border, right_border, coord):
    n = len(coord) - 1
    b = [1 for i in range(n)]
    count = 0
    for i in range(n):
        if not point_in_angle(point, coord[(i-1) % n], coord[i % n], coord[(i+1) % n]) and \
                (left_border is None or not point_in_angle(coord[i % n], left_border, point, right_border)):
            b[i] = 0
            count += 1
    if count == 0:
        return 'inside'
    if count == n:
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
    return start, end


def find_pair_cutoff(point, left_border, right_border, coord):
    n = len(coord) - 1
    begin = end = -1
    for i in range(n):
        if not point_in_angle(point, coord[(i-1) % n], coord[i % n], coord[(i+1) % n]) and \
                (left_border is None or not point_in_angle(coord[i % n], left_border, point, right_border)):
            if i == 0:
                start_zero = True
            if begin == -1 and not start_zero:
                begin = i
            if start_zero and end != -1:
                begin = i
                return min(begin, end), max(begin, end)
            if not start_zero and i == n - 1:
                end = n - 1
                return min(begin, end), max(begin, end)
        else:
            if i == 0:
                start_zero = False
            if begin != -1 and not start_zero:
                end = (i-1) % n
                return min(begin, end), max(begin, end)
            if start_zero and end == -1:
                end = (i-1) % n
            if start_zero and i == n - 1:
                begin = n
                return min(begin, end), max(begin, end)
    return None


def quad_equation(a, b, c):
    if a == 0:
        return -c / b
    d = b**2 - 4 * a * c
    if d < 0:
        return None
    elif d == 0:
        return -b / (2 * a), -b / (2 * a)
    return (-b + math.sqrt(d)) / (2 * a), (-b - math.sqrt(d)) / (2 * a)


def find_pair_ellipse(point, left_border, right_border, coord):
    multipl = 10000000
    a, b = (coord[2][0] - coord[1][0]) / 2 * multipl, (coord[1][1] - coord[0][1]) / 2 * multipl
    xc, yc = (coord[2][0] + coord[1][0]) / 2 * multipl, (coord[1][1] + coord[0][1]) / 2 * multipl
    x0, y0 = point[0] * multipl - xc, point[1] * multipl - yc
    y = quad_equation(b**2 + y0**2 * a**2 / x0**2, -2 * y0 * b**2 * a**2 / x0**2, -b**4 + a**2 * b**2 / x0**2)
    if y is None:
        return None
    x1, x2 = (1 - y0 * y[0] / b**2) * a**2 / x0, (1 - y0 * y[1] / b**2) * a**2 / x0
    point1, point2 = ((x1 + xc) / multipl, (y[0] + yc) / multipl), ((x2 + xc) / multipl, (y[1] + yc) / multipl)
    if left_border is None:
        return point1, point2
    if not point_in_angle(point1, left_border, point, right_border):
        if not point_in_angle(point2, left_border, point, right_border):
            return None
        return point2, point2
    if not point_in_angle(point2, left_border, point, right_border):
        return point1, point1
    return point1, point2


def add_point(new_point, point, view_angle_std, crosses, node=None):
    dist_point = dist(point, new_point)
    k1 = math.ceil(angle_horizontal(point, new_point) * 180 / math.pi / view_angle_std)
    if crosses[k1] is None or crosses[k1][0] > dist_point:
        crosses[k1] = [dist_point, [new_point[0], new_point[1], node]]
    return k1


def add_points(point1, point2, point, view_angle_std, crosses, node1=None, node2=None):
    k1 = add_point(point1, point, view_angle_std, crosses, node1)
    k2 = add_point(point2, point, view_angle_std, crosses, node2)
    x1, y1 = vec(point, point1)
    x2, y2 = vec(point, point2)
    k12 = 10 ** 10 if x1 == x2 else (y1 - y2) / (x1 - x2)
    b12 = y1 - k12 * x1
    for p in range(min(k1, k2) + 1, max(k1, k2)):
        k_curr = math.tan((p * view_angle_std + 0.0000001) * math.pi / 180)
        x = b12 / (k_curr - k12)
        y = k_curr * x
        dist_point = mod((x, y))
        if crosses[p] is None or crosses[p][0] > dist_point:
            crosses[p] = [dist_point, None]


def first_point(point, polygons, multilinestrings, view_angle=None, point_approx=False, pair_func=find_pair_array):
    view_angle_std = 1 if view_angle is None or view_angle == 0 else view_angle
    angle_count = math.floor(360 / view_angle_std)
    crosses = [None for p in range(angle_count)]

    # adding linestrings
    for j in range(multilinestrings.shape[0]):
        line_coords = multilinestrings.coords[j]
        if line_coords is None:
            continue
        point1, point1_index = line_coords[0], 0
        add_point(point1, point, view_angle_std, crosses, {'polygon': None, 'line': [j, 0]})
        for t in range(len(line_coords) - 1):
            point2 = line_coords[t + 1]
            if view_angle is not None:
                delta_angle = view_angle * math.pi / 180
                if angle(point1, point, point2) < delta_angle:
                    continue
            add_point(point2, point, view_angle_std, crosses, {'polygon': None, 'line': [j, t + 1]})
            point1 = point2

    # adding polygons
    for j in range(polygons.shape[0]):
        polygon = polygons.coords[j]
        if polygon is None:
            continue
        pair = pair_func(point, None, None, polygon)
        if pair is None:
            continue
        if type(pair) == str:
            for t in range(len(polygon) - 1):
                add_point(polygon[t], point, view_angle_std, crosses, {'polygon': [j, t], 'line': None})
            break
        left, right = pair
        left_coords, right_coords = (left, right) if type(left) == (tuple or list) else (polygon[left], polygon[right])
        if view_angle is not None:
            delta_angle = view_angle * math.pi / 180
            if angle(left_coords, point, right_coords) < delta_angle:
                if point_approx:
                    add_point(polygon[0], point, view_angle_std, crosses, {'polygon': [j, -1], 'line': None})
                continue
        add_points(left_coords, right_coords, point, view_angle_std, crosses,
                   {'polygon': [j, left], 'line': None}, {'polygon': [j, right], 'line': None})

    points = list()
    for p in range(angle_count):
        if crosses[p] is not None and crosses[p][1] is not None:
            points.append([crosses[p][1][0], crosses[p][1][1], crosses[p][1][2]])
    return tuple(points)


def find_points(point_data, polygons, multilinestrings, view_angle=None, point_approx=False, pair_func=find_pair_array):
    point = (point_data[0], point_data[1])
    point_polygon_info = point_data[2]['polygon']
    if point_polygon_info is None:
        point_polygon = None
    else:
        point_polygon, point_polygon_point = point_polygon_info[0], point_polygon_info[1]
        if point_polygon_point == -1:
            return first_point(point, polygons, multilinestrings,
                               view_angle=view_angle, point_approx=point_approx, pair_func=pair_func)
    view_angle_std = 1 if view_angle is None or view_angle == 0 else view_angle
    angle_count = math.floor(360 / view_angle_std)
    crosses = [None for p in range(angle_count)]

    # adding linestrings
    point_line_info = point_data[2]['line']
    if point_line_info is None:
        point_line = None
    else:
        point_line, point_line_point = point_line_info[0], point_line_info[1]
    multilinestring_number = multilinestrings.shape[0]
    for j in range(multilinestring_number):
        line_coords = multilinestrings.coords[j]
        if line_coords is None:
            continue
        if point_line is not None and j == point_line:
            if point_line_point > 0:
                add_point(line_coords[point_line_point - 1], point, view_angle_std, crosses,
                          {'polygon': None, 'line': [j, point_line_point - 1]})
            if point_line_point < len(line_coords) - 1:
                add_point(line_coords[point_line_point + 1], point, view_angle_std, crosses,
                          {'polygon': None, 'line': [j, point_line_point + 1]})
            continue
        point1, point1_index = line_coords[0], 0
        add_point(point1, point, view_angle_std, crosses, {'polygon': None, 'line': [j, 0]})
        for t in range(len(line_coords) - 1):
            point2 = line_coords[t + 1]
            if view_angle is not None:
                delta_angle = view_angle * math.pi / 180
                if angle(point1, point, point2) < delta_angle:
                    continue
            add_point(point2, point, view_angle_std, crosses, {'polygon': None, 'line': [j, t + 1]})
            point1 = point2

    # adding polygons
    polygon_number = polygons.shape[0]
    point_polygon_coords = None if point_polygon is None else polygons.coords[point_polygon]
    n = -1 if point_polygon_coords is None else len(point_polygon_coords) - 1
    left_border, right_border = (None, None) if point_polygon is None else \
        (point_polygon_coords[(point_polygon_point - 1) % n],
         point_polygon_coords[(point_polygon_point + 1) % n])
    print(left_border, right_border)
    for j in range(polygon_number):
        polygon = polygons.coords[j]
        if polygon is None:
            continue
        if point_polygon is not None and j == point_polygon:
            non_convex = polygons.geometry[j]
            m = len(non_convex) - 1
            k = -1
            for t in range(n):
                if tuple(polygon[t]) == tuple(point):
                    k = t
                    break
            if k == -1:
                continue
            for t in range(m):
                if t == k or not inner_diag(point_polygon_point, t, non_convex, m):
                    continue
                add_point(non_convex[t], point, view_angle_std, crosses, {'polygon': [j, t], 'line': None})
            continue
        pair = pair_func(point, left_border, right_border, polygon)
        if pair is None or type(pair) == str:
            continue
        left, right = pair
        left_coords, right_coords = (left, right) if type(left) == (tuple or list) else (polygon[left], polygon[right])
        if view_angle is not None:
            delta_angle = view_angle * math.pi / 180
            if angle(left_coords, point, right_coords) < delta_angle:
                if point_approx:
                    add_point(polygon[0], point, view_angle_std, crosses, {'polygon': [j, -1], 'line': None})
                continue
        add_points(left_coords, right_coords, point, view_angle_std, crosses,
                   {'polygon': [j, left], 'line': None}, {'polygon': [j, right], 'line': None})

    points = list()
    for p in range(angle_count):
        if crosses[p] is not None and crosses[p][1] is not None:
            points.append([crosses[p][1][0], crosses[p][1][1], crosses[p][1][2]])
    return tuple(points)


def add_inside_poly(G, point, i, polygon, max_poly_len, plot):
    n = len(polygon) - 1
    k = -1
    for t in range(n):
        if tuple(polygon[t]) == tuple(point):
            k = t
            break
    if k == -1:
        return
    for t in range(n):
        if t == k or not inner_diag(k, t, polygon, n):
            continue
        other_point = polygon[t]
        G.add_node(i * max_poly_len + t, x=other_point[0], y=other_point[1])
        G.add_edge(i * max_poly_len + t, i * max_poly_len + k)
        if plot:
            plt.plot([point[0], other_point[0]], [point[1], other_point[1]])


def build_graph(polygons, multilinestrings, pair_func=find_pair_array,
                plot=False, view_angle=None, point_approx=False, crs='EPSG:4326'):
    fig = plt.figure()
    G = nx.MultiGraph(crs=crs)
    max_poly_len = 10000  # for graph indexing
    polygon_number = polygons.shape[0]
    multilinestring_number = multilinestrings.shape[0] if multilinestrings is not None else 0

    # all polygons cycle
    for i in range(polygon_number):
        coords_1 = polygons.coords[i]
        if coords_1 is None:
            continue
        n = len(coords_1) - 1

        # all points of polygon cycle
        for k in range(n):
            point, left_border, right_border = coords_1[k], coords_1[(k - 1) % n], coords_1[(k + 1) % n]
            G.add_node(i * max_poly_len + k, x=point[0], y=point[1])
            view_angle_std = 1 if view_angle is None or view_angle == 0 else view_angle
            angle_count = math.floor(360 / view_angle_std)
            crosses = [None for p in range(angle_count)]

            # adding linestrings
            for j in range(multilinestring_number):
                line_coords = multilinestrings.coords[j]
                if line_coords is None:
                    continue
                point1, point1_index = line_coords[0], 0
                add_point(point1, point, view_angle_std, crosses, (j + 0.33) * max_poly_len)
                for t in range(len(line_coords) - 1):
                    point2 = line_coords[t + 1]
                    if view_angle is not None:
                        delta_angle = view_angle * math.pi / 180
                        if angle(point1, point, point2) < delta_angle:
                            continue
                    node1 = (j + 0.33) * max_poly_len + point1_index
                    node2 = (j + 0.33) * max_poly_len + t + 1
                    G.add_node(node1, x=point1[0], y=point1[1])
                    G.add_node(node2, x=point2[0], y=point2[1])
                    G.add_edge(node1, node2)
                    add_point(point2, point, view_angle_std, crosses, node2)
                    point1 = point2

            # adding polygons
            for j in range(polygon_number):
                coords_2 = polygons.coords[j]
                if coords_2 is None:
                    continue
                if j == i:
                    add_inside_poly(G, point, i, polygons.geometry[i], max_poly_len, plot)
                    continue
                pair = pair_func(point, left_border, right_border, coords_2)
                if pair is None or type(pair) == str:
                    continue
                left, right = pair
                if type(left) == (tuple or list):
                    left_coords, right_coords, left, right = left, right, 1, 2
                else:
                    left_coords, right_coords = coords_2[left], coords_2[right]
                if view_angle is not None:
                    delta_angle = view_angle * math.pi / 180
                    if angle(left_coords, point, right_coords) < delta_angle:
                        if point_approx:
                            node = (j + 0.66) * max_poly_len
                            G.add_node(node, x=coords_2[0][0], y=coords_2[0][1])
                            G.add_edge(node, i * max_poly_len + k)
                            add_point(coords_2[0], point, view_angle_std, crosses, node)
                        continue
                add_points(left_coords, right_coords, point, view_angle_std, crosses,
                           j * max_poly_len + left, j * max_poly_len + right)

            for p in range(angle_count):
                if crosses[p] is not None and crosses[p][1] is not None:
                    G.add_node(crosses[p][1][2], x=crosses[p][1][0], y=crosses[p][1][1])
                    G.add_edge(crosses[p][1][2], i * max_poly_len + k)
                    if plot:
                        plt.plot([point[0], crosses[p][1][0]], [point[1], crosses[p][1][1]])
    return G, fig
