import networkx as nx
import matplotlib.pyplot as plt
from geometry import *


def find_pair_array(point, left_border, right_border, coord, reverse=False):
    n = len(coord) - 1
    b = [1 for i in range(n)]
    count = 0
    for i in range(n):
        if not point_in_angle(point, coord[(i-1) % n], coord[i % n], coord[(i+1) % n]):
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
    start_in_angle = point_in_angle(coord[start], left_border, point, right_border) if left_border is not None else False
    end_in_angle = point_in_angle(coord[end], left_border, point, right_border) if left_border is not None else False
    if left_border is not None and reverse:
        start_in_angle = not start_in_angle
        end_in_angle = not end_in_angle
    return {'point': start, 'in_angle': start_in_angle}, {'point': end, 'in_angle': end_in_angle}


def find_pair_cutoff(point, left_border, right_border, coord, reverse=False):
    n = len(coord) - 1
    begin = end = -1
    found = False
    for i in range(n):
        if not point_in_angle(point, coord[(i-1) % n], coord[i % n], coord[(i+1) % n]):
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
    if not found:
        return None
    min_left = min(begin, end)
    max_right = max(begin, end)
    left_in_angle = point_in_angle(coord[min_left], left_border, point, right_border) if left_border is not None else False
    right_in_angle = point_in_angle(coord[max_right], left_border, point, right_border) if left_border is not None else False
    if left_border is not None and reverse:
        left_in_angle = not left_in_angle
        right_in_angle = not right_in_angle
    return {'point': min_left, 'in_angle': left_in_angle}, {'point': max_right, 'in_angle': right_in_angle}


def quad_equation(a, b, c):
    if a == 0:
        return -c / b
    d = b**2 - 4 * a * c
    if d < 0:
        return None
    elif d == 0:
        return -b / (2 * a), -b / (2 * a)
    return (-b + math.sqrt(d)) / (2 * a), (-b - math.sqrt(d)) / (2 * a)


def find_pair_ellipse(point, left_border, right_border, coord, reverse=False):
    multipl = 10000000
    a, b = (coord[2][0] - coord[1][0]) / 2 * multipl, (coord[1][1] - coord[0][1]) / 2 * multipl
    xc, yc = (coord[2][0] + coord[1][0]) / 2 * multipl, (coord[1][1] + coord[0][1]) / 2 * multipl
    x0, y0 = point[0] * multipl - xc, point[1] * multipl - yc
    y = quad_equation(b**2 + y0**2 * a**2 / x0**2, -2 * y0 * b**2 * a**2 / x0**2, -b**4 + a**2 * b**2 / x0**2)
    if y is None:
        return None
    x1, x2 = (1 - y0 * y[0] / b**2) * a**2 / x0, (1 - y0 * y[1] / b**2) * a**2 / x0
    point1, point2 = ((x1 + xc) / multipl, (y[0] + yc) / multipl), ((x2 + xc) / multipl, (y[1] + yc) / multipl)
    left_in_angle = point_in_angle(point1, left_border, point, right_border) if left_border is not None else False
    right_in_angle = point_in_angle(point2, left_border, point, right_border) if left_border is not None else False
    if left_border is not None and reverse:
        left_in_angle = not left_in_angle
        right_in_angle = not right_in_angle
    return {'point': point1, 'in_angle': left_in_angle}, {'point': point2, 'in_angle': right_in_angle}


def find_pair_non_convex(point, left_border, right_border, coord, reverse=False):
    n = len(coord) - 1
    left, right = None, None
    for i in range(n):
        pi = coord[i]
        if tuple(pi) == tuple(point):
            continue
        if left is None:
            left_found = True
            for j in range(n):
                if j == i:
                    continue
                if turn(point, pi, coord[j]) > 0:
                    left_found = False
                    break
            if left_found:
                left = i
                if right is not None:
                    break
                else:
                    continue
        if right is None:
            right_found = True
            for j in range(n):
                if j == i:
                    continue
                if turn(point, pi, coord[j]) < 0:
                    right_found = False
                    break
            if right_found:
                right = i
                if left is not None:
                    break
                else:
                    continue
    if left is None:
        return 'inside'
    if right is None:
        right = left
    min_left = min(left, right)
    max_right = max(left, right)
    left_in_angle = point_in_angle(coord[min_left], left_border, point, right_border) if left_border is not None else False
    right_in_angle = point_in_angle(coord[max_right], left_border, point, right_border) if left_border is not None else False
    if left_border is not None and reverse:
        left_in_angle = not left_in_angle
        right_in_angle = not right_in_angle
    return {'point': min_left, 'in_angle': left_in_angle}, {'point': max_right, 'in_angle': right_in_angle}


def add_point(new_point_info, point, view_angle_std, crosses, node=None):
    new_point = new_point_info[0]
    k1 = math.floor(angle_horizontal(point, new_point) * 180 / math.pi / view_angle_std)
    if not new_point_info[1]:
        dist_point = dist(point, new_point)
        if crosses[k1] is None or crosses[k1][0] > dist_point:
            crosses[k1] = [dist_point, [new_point[0], new_point[1], node]]
    return k1


def add_points(point1_info, point2_info, point, view_angle_std, crosses, node1=None, node2=None):
    point1, point2 = point1_info[0], point2_info[0]
    k1 = add_point(point1_info, point, view_angle_std, crosses, node1)
    k2 = add_point(point2_info, point, view_angle_std, crosses, node2)
    x1, y1 = vec(point, point1)
    x2, y2 = vec(point, point2)
    k12 = 10 ** 10 if x1 == x2 else (y1 - y2) / (x1 - x2)
    b12 = y1 - k12 * x1
    k_min = min(k1, k2)
    k_max = max(k1, k2)
    if k_max - k_min < 180 / view_angle_std:  # !!!!!!!!! FIX !!!!!!!!!
        for p in range(k_min + 1, k_max):
            k_curr = math.tan((p * view_angle_std * math.pi + 0.0000001) / 180)
            x = b12 / (k_curr - k12)
            y = k_curr * x
            dist_point = mod((x, y))
            if crosses[p] is None or crosses[p][0] > dist_point:
                crosses[p] = [dist_point, None]
    else:
        for p in range(0, k_min):
            k_curr = math.tan((p * view_angle_std * math.pi + 0.0000001) / 180)
            x = b12 / (k_curr - k12)
            y = k_curr * x
            dist_point = mod((x, y))
            if crosses[p] is None or crosses[p][0] > dist_point:
                crosses[p] = [dist_point, None]
        for p in range(k_max + 1, len(crosses)):
            k_curr = math.tan((p * view_angle_std * math.pi + 0.0000001) / 180)
            x = b12 / (k_curr - k12)
            y = k_curr * x
            dist_point = mod((x, y))
            if crosses[p] is None or crosses[p][0] > dist_point:
                crosses[p] = [dist_point, None]


def add_inside_poly(G, point, i, polygon, k, max_poly_len, plot, cv):
    n = len(polygon) - 1
    for t in range(n):
        if t == k or (not cv and not inner_diag(k, t, polygon, n)):
            continue
        other_point = polygon[t]
        G.add_node(i * max_poly_len + t, x=other_point[0], y=other_point[1])
        G.add_edge(i * max_poly_len + t, i * max_poly_len + k)
        if plot:
            plt.plot([point[0], other_point[0]], [point[1], other_point[1]])


def find_borders(k, point, polygon):
    n = len(polygon) - 1
    result = list()
    for i in range(n):
        pi = polygon[i]
        if i == k:
            continue
        found = True
        for j in range(n):
            if j == i or j + 1 == i or j == k or j + 1 == k:
                continue
            pl = polygon[j]
            pr = polygon[j + 1]
            if intersects(point, pi, pl, pr):
                found = False
                break
        if found:
            result.append(i)
            if len(result) == 2:
                return result
    return result if len(result) == 2 else None


def build_graph(polygons, multilinestrings, pair_func=find_pair_non_convex, cv=False,
                plot=False, view_angle=None, point_approx=False, crs='EPSG:4326'):
    if not cv:
        pair_func=find_pair_non_convex
    fig = plt.figure()
    G = nx.Graph(crs=crs)
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
            point = coords_1[k]
            reverse = False
            if n <= 2:
                left_border, right_border = None, None
            elif cv or n == 3:
                left_border, right_border = coords_1[(k - 1) % n], coords_1[(k + 1) % n]
            else:
                # pair = find_pair_non_convex(point, None, None, coords_1)
                pair = find_borders(k, point, coords_1)
                if pair is None:  # or type(pair) == str:
                    continue
                # left, right = pair[0]['point'], pair[1]['point']
                left, right = pair[0], pair[1]
                left_border, right_border = coords_1[left], coords_1[right]
                for j in range(n):
                    if j != k and j != left and j != right:
                        different_point = j
                        break
                reverse = not point_in_angle(coords_1[different_point], left_border, point, right_border)
            G.add_node(i * max_poly_len + k, x=point[0], y=point[1])
            view_angle_std = 1 if view_angle is None or view_angle < 1 else view_angle
            angle_count = math.floor(360 / view_angle_std)
            crosses = [None for p in range(angle_count)]

            # adding linestrings
            for j in range(multilinestring_number):
                line_coords = multilinestrings.coords[j]
                if line_coords is None:
                    continue
                point1, point1_index = line_coords[0], 0
                for t in range(len(line_coords) - 1):
                    point2 = line_coords[t + 1]
                    if view_angle is not None:
                        delta_angle = view_angle * math.pi / 180
                        if angle(point1, point, point2) < delta_angle:
                            continue
                    node1 = (j + 0.5) * max_poly_len + point1_index
                    node2 = (j + 0.5) * max_poly_len + t + 1
                    G.add_node(node1, x=point1[0], y=point1[1])
                    G.add_node(node2, x=point2[0], y=point2[1])
                    G.add_edge(node1, node2)
                    add_points((point1, False), (point2, False), point, view_angle_std, crosses, node1, node2)
                    point1 = point2

            # adding polygons
            for j in range(polygon_number):
                coords_2 = polygons.coords[j]
                if coords_2 is None:
                    continue
                if j == i:
                    add_inside_poly(G, point, i, coords_1, k, max_poly_len, plot, cv)
                    continue
                pair = pair_func(point, left_border, right_border, coords_2, reverse)
                if pair is None or type(pair) == str:
                    if not cv:
                        crosses = [None for p in range(angle_count)]
                        break
                    else:
                        continue
                left, right = pair
                if type(left['point']) == (tuple or list):
                    left_coords, right_coords, left, right, left_in_angle, right_in_angle = \
                        left['point'], right['point'], 1, 2, False, False
                else:
                    left_in_angle, right_in_angle = left['in_angle'], right['in_angle']
                    left, right = left['point'], right['point']
                    left_coords, right_coords = coords_2[left], coords_2[right]
                if view_angle is not None:
                    delta_angle = view_angle * math.pi / 180
                    if not left_in_angle and not right_in_angle and angle(left_coords, point, right_coords) < delta_angle:
                        if point_approx:
                            node = j * max_poly_len
                            G.add_node(node, x=coords_2[0][0], y=coords_2[0][1])
                            G.add_edge(node, i * max_poly_len + k)
                            add_point((coords_2[0], False), point, view_angle_std, crosses, node)
                        continue
                add_points((left_coords, left_in_angle), (right_coords, right_in_angle), point, view_angle_std,
                           crosses, j * max_poly_len + left, j * max_poly_len + right)

            for p in range(angle_count):
                if crosses[p] is not None and crosses[p][1] is not None:
                    G.add_node(crosses[p][1][2], x=crosses[p][1][0], y=crosses[p][1][1])
                    G.add_edge(crosses[p][1][2], i * max_poly_len + k)
                    if plot:
                        plt.plot([point[0], crosses[p][1][0]], [point[1], crosses[p][1][1]])
    return G, fig
