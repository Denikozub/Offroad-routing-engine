import networkx as nx
import matplotlib.pyplot as plt
from geometry import *


def find_pair_array(point, left_border, right_border, coord):
    n = len(coord) - 1
    b = [1 for i in range(n)]
    count = 0
    for i in range(n):
        if not point_in_angle(point, coord[(i-1) % n], coord[i % n], coord[(i+1) % n]) and \
                not point_in_angle(coord[i % n], left_border, point, right_border):
            b[i] = 0
            count += 1
    if count == 0 or count == n:
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
                not point_in_angle(coord[i % n], left_border, point, right_border):
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
    if not point_in_angle(point1, left_border, point, right_border):
        if not point_in_angle(point2, left_border, point, right_border):
            return None
        return point2, point2
    if not point_in_angle(point2, left_border, point, right_border):
        return point1, point1
    return point1, point2


def add_point(new_point, point, view_angle_std, crosses, node):
    dist_point = dist(point, new_point)
    k1 = math.ceil(angle_horizontal(point, new_point) * 180 / math.pi / view_angle_std)
    if crosses[k1] is None or crosses[k1][0] > dist_point:
        crosses[k1] = [dist_point, [new_point[0], new_point[1], node]]
    return k1


def add_points(point1, point2, point, view_angle_std, crosses, node1, node2):
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


def add_inside_poly(G, k, point, i, polygon, n, max_poly_len, plot):
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
            point, left_border, right_border = coords_1[k], coords_1[(k-1) % n], coords_1[(k+1) % n]
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
                if j == i:
                    add_inside_poly(G, k, point, i, polygons.geometry[i], n, max_poly_len, plot)
                    continue
                coords_2 = polygons.coords[j]
                if coords_2 is None:
                    continue
                pair = pair_func(point, left_border, right_border, coords_2)
                if pair is None:
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
