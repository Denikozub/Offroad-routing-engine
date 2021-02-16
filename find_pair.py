from geometry import point_in_angle, intersects


def find_pair_array(point, polygon, polygon_number):
    n = len(polygon) - 1
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
    return ((polygon[start], polygon_number, start), (polygon[end], polygon_number, end))


def find_pair_cutoff(point, polygon, polygon_number):
    n = len(polygon) - 1
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
    return None if not found else ((polygon[begin], polygon_number, begin), (polygon[end], polygon_number, end))


def quad_equation(a, b, c):
    if a == 0:
        return -c / b
    d = b**2 - 4 * a * c
    if d < 0:
        return None
    elif d == 0:
        return -b / (2 * a), -b / (2 * a)
    return (-b + math.sqrt(d)) / (2 * a), (-b - math.sqrt(d)) / (2 * a)


def find_pair_ellipse(point, polygon, polygon_number):
    multipl = 10000000
    a, b = (polygon[2][0] - polygon[1][0]) / 2 * multipl, (polygon[1][1] - polygon[0][1]) / 2 * multipl
    xc, yc = (polygon[2][0] + polygon[1][0]) / 2 * multipl, (polygon[1][1] + polygon[0][1]) / 2 * multipl
    x0, y0 = point[0] * multipl - xc, point[1] * multipl - yc
    y = quad_equation(b**2 + y0**2 * a**2 / x0**2, -2 * y0 * b**2 * a**2 / x0**2, -b**4 + a**2 * b**2 / x0**2)
    if y is None:
        return None
    x1, x2 = (1 - y0 * y[0] / b**2) * a**2 / x0, (1 - y0 * y[1] / b**2) * a**2 / x0
    point1, point2 = ((x1 + xc) / multipl, (y[0] + yc) / multipl), ((x2 + xc) / multipl, (y[1] + yc) / multipl)
    return ((point1, None, None), (point2, None, None))


def find_line_brute_force(point, polygon, polygon_number, polygon_point_number=None):
    n = len(polygon) - 1
    result = list()
    for i in range(n):
        pi = polygon[i]
        if polygon_point_number is not None and i == polygon_point_number:
            continue
        found = True
        for j in range(n):
            if j in (i - 1, i) or (polygon_point_number is not None and j in (polygon_point_number - 1, polygon_point_number)):
                continue
            if intersects(point, pi, polygon[j], polygon[j + 1]):
                found = False
                break
        if found:
            result.append(i)
            if len(result) == 2:
                break
    if len(result) != 2:
        return None
    point1, point2 = result
    if polygon_point_number is not None:
        return (polygon[point1], polygon[point2])
    line = list()
    for i in range(point1, point2 + 1):
        line.append((polygon[i], polygon_number, i))
    return line
    
