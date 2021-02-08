import numpy as np
import networkx as nx
import math
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


def add_point(new_point, point, view_angle_std, crosses, node):
    x = new_point[0]
    y = new_point[1]
    x_rel = x - point[0]
    y_rel = y - point[1]
    dist = mod((x_rel, y_rel))
    k1 = math.ceil(math.atan2(y_rel, x_rel) * 180 / math.pi / view_angle_std)
    if crosses[k1] is None or crosses[k1][0] > dist:
        crosses[k1] = [dist, [x, y, node]]
    return x, y, x_rel, y_rel, k1


def add_points(point1, point2, point, view_angle_std, crosses, node1, node2):
    x1, y1, x1_rel, y1_rel, k1 = add_point(point1, point, view_angle_std, crosses, node1)
    x2, y2, x2_rel, y2_rel, k2 = add_point(point2, point, view_angle_std, crosses, node2)
    for p in range(min(k1, k2) + 1, max(k1, k2)):
        k_curr = math.tan((p * view_angle_std + 0.00001)*math.pi/180)
        if x1_rel == x2_rel:
            k_segment = 100000
        else:
            k_segment = (y1_rel - y2_rel) / (x1_rel - x2_rel)
        b_segment = y1_rel - k_segment * x1_rel
        x = b_segment / (k_curr - k_segment)
        y = k_curr * x
        if not point_in_angle((x, y), (x1_rel, y1_rel), (0, 0), (x2_rel, y2_rel)):
            continue
        dist = mod((x, y))
        if crosses[p] is None or crosses[p][0] > dist:
            crosses[p] = [dist, None]


def build_graph(polygons, multilinestrings, pair_func=find_pair_array,
                plot=False, view_angle=None, point_approx=False, crs='EPSG:4326'):
    fig = plt.figure()
    G = nx.MultiGraph(crs=crs)
    max_poly_len = 10000  # for graph indexing
    polygon_number = polygons.shape[0]
    multilinestring_number = multilinestrings.shape[0]
    for i in range(polygon_number):
        coords_1 = polygons.coords[i]
        if coords_1 is None:
            continue
        n = len(coords_1) - 1
        for k in range(n):
            point = coords_1[k]
            left_border = coords_1[(k-1) % n]
            right_border = coords_1[(k+1) % n]
            G.add_node(i * max_poly_len + k, x=point[0], y=point[1])
            view_angle_std = 1 if view_angle is None or view_angle == 0 else view_angle
            angle_count = math.floor(360 / view_angle_std)
            crosses = [None for p in range(angle_count)]
            for j in range(multilinestring_number):
                line_coords = multilinestrings.coords[j]
                if line_coords is None:
                    continue
                m = len(line_coords) - 1
                stay = False
                for t in range(m):
                    if not stay:
                        point1 = line_coords[t]
                        point1_index = t
                    point2 = line_coords[t + 1]
                    if view_angle is not None:
                        delta_angle = view_angle * math.pi / 180
                        if angle(point1, point, point2) < delta_angle:
                            stay = True
                            continue
                    node1 = (j + 0.33) * max_poly_len + point1_index
                    node2 = (j + 0.33) * max_poly_len + t + 1
                    G.add_node(node1, x=point1[0], y=point1[1])
                    G.add_node(node2, x=point2[0], y=point2[1])
                    G.add_edge(node1, node2)
                    add_points(point1, point2, point, view_angle_std, crosses, node1, node2)
            for j in range(polygon_number):
                if j == i:  # adding nodes inside a polygon
                    for t in range(n):
                        if t == k:
                            continue
                        other_point = coords_1[t]
                        G.add_node(i * max_poly_len + t, x=other_point[0], y=other_point[1])
                        G.add_edge(i * max_poly_len + t, i * max_poly_len + k)
                        if plot:
                            plt.plot([point[0], other_point[0]], [point[1], other_point[1]])
                    continue
                coords_2 = polygons.coords[j]
                if coords_2 is None:
                    continue
                pair = pair_func(point, left_border, right_border, coords_2)
                if pair is None:
                    continue
                left, right = pair
                left_coords = coords_2[left]
                right_coords = coords_2[right]
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
