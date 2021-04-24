from shapely.geometry import LineString
from geometry import point_in_angle

"""
class that builds visibility graph for line segments
currently used algorithm is brute force
in the future 2 more algorithms will be added:
1) O(n log n) rotating sweep line
2) O(n) angle approximation (see first_version.graph)
"""


class SegmentVisibility:

    def __init__(self):
        self.__segments = list()

        # information about view restrictions from own polygon
        self.__restriction_pair = None
        self.__restriction_point = None
        self.__reverse_angle = None  # should be False if restriction angle > pi (point not a part of CH)
    
    def add_pair(self, pair):
        if pair is None:
            return
        self.__segments.append(pair)
    
    def add_line(self, line):
        if line is None:
            return
        for i in range(len(line) - 1):
            self.add_pair((line[i], line[i + 1]))
    
    def set_restriction_angle(self, restriction_pair, restriction_point, reverse_angle):
        self.__restriction_pair = restriction_pair
        self.__restriction_point = restriction_point
        self.__reverse_angle = reverse_angle
    
    def get_edges(self, point):
        segment_number = len(self.__segments)
        visible_edges = list()
        for i in range(segment_number):
            a, b = self.__segments[i]
            a_point, b_point = a[0], b[0]
            if self.__restriction_pair is not None and self.__restriction_point is not None and self.__reverse_angle is not None:
                l_point, r_point = self.__restriction_pair
                # if a point is inside a restriction angle, it will not be returned
                intersects_a = not point_in_angle(a_point, l_point, self.__restriction_point, r_point) != self.__reverse_angle
                intersects_b = not point_in_angle(b_point, l_point, self.__restriction_point, r_point) != self.__reverse_angle
                if intersects_a and intersects_b:  # if both in restriction angle
                    continue
            else:
                intersects_a, intersects_b = False, False
            for j in range(segment_number):
                if j == i:
                    continue
                check_pair = self.__segments[j]
                check_a, check_b = check_pair[0][0], check_pair[1][0]
                if not intersects_a and LineString([point, a_point]).crosses(LineString([check_a, check_b])):
                    intersects_a = True
                if not intersects_b and LineString([point, b_point]).crosses(LineString([check_a, check_b])):
                    intersects_b = True
                if intersects_a and intersects_b:
                    break
            if not intersects_a:
                visible_edges.append(a)
            if not intersects_b:
                visible_edges.append(b)
        return visible_edges
