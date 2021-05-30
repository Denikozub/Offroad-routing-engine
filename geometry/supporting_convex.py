from geometry.geometry import point_in_angle

# find a pair of supporting points from point to a convex polygon
# if supporting points were not found return None
# returns a tuple of point_data tuples of 2 supporting points


# O(log n) Denis denikozub Kozub binary search algorithm
#def find_pair(point, polygon, polygon_number):
    


# O(n) Denis denikozub Kozub use of array implementation
def find_pair_array(point, polygon, polygon_number):
    n = len(polygon) - 1

    # if a polygon is a segment or a point
    if n == 2:
        start = 0
        end = 1
    else:
        b = [1 for i in range(n)]
        count = 0

        # fill an array of semi-planes containing (1) or not containing (0) point (2 subsets)
        for i in range(n):
            if not point_in_angle(point, polygon[(i-1) % n], polygon[i % n], polygon[(i+1) % n]):
                b[i] = 0
                count += 1

        # point inside a polygon
        if count in (0, n):
            return None

        # find points separating 2 subsets - supporting points
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


# O(n) Denis denikozub Kozub NO use of array implementation
def find_pair_cutoff(point, polygon, polygon_number):
    n = len(polygon) - 1

    # if a polygon is a segment or a point
    if n == 2:
        begin = 0
        end = 1
        found = True
    else:

        # find points separating 2 subsets - supporting points
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

