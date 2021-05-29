from shapely.geometry import LineString
from geometry import compare_points, ray_intersects_segment, turn, point_in_angle
from math import atan2

"""
class that builds visibility graph for line segments
1) brute force O(n^2)
2) rotational sweep line O(n log n)
3) angle approximation O(n)
"""


class SegmentVisibility:

    def __init__(self):
        self.__segments = list()

        # information about view restrictions from own polygon
        self.__restriction_pair = None
        self.__restriction_point = None

        # should be False if restriction angle > pi (point not a part of CH)
        self.__reverse_angle = None

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

    def get_edges_brute(self, point):
        segment_number = len(self.__segments)
        visible_edges = list()

        # check 2 points (of a segment) at a time
        for i in range(segment_number):
            a, b = self.__segments[i]
            a_point, b_point = a[0], b[0]

            # if a point is inside a restriction angle, it will not be returned
            if self.__restriction_pair is not None and self.__restriction_point is not None and self.__reverse_angle is not None:
                l_point, r_point = self.__restriction_pair
                intersects_a = not point_in_angle(a_point, l_point, self.__restriction_point, r_point) != self.__reverse_angle
                intersects_b = not point_in_angle(b_point, l_point, self.__restriction_point, r_point) != self.__reverse_angle
                if intersects_a and intersects_b:  # if both in restriction angle
                    continue

            # restriction angle not used
            else:
                intersects_a, intersects_b = False, False

            # for each of 2 points check intersection with all other segments
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

            # if only one of the points is visible it will be added
            if not intersects_a:
                visible_edges.append(a)
            if not intersects_b:
                visible_edges.append(b)
        return visible_edges

    def get_edges_sweepline(self, point):

        # list of points sorted by angle
        points = list()
        for edge in self.__segments:
            points.append((edge[0], edge[1]))
            points.append((edge[1], edge[0]))
        points.sort(key=lambda x: atan2(x[0][0][1] - point[1], x[0][0][0] - point[0]))

        # list of segments intersected by 0-angle ray
        intersected = list()
        for edge in self.__segments:
            if ray_intersects_segment(point, (point[0] - 1, point[1]), edge[0][0], edge[1][0], True):
                # intersected[edge[0][0]] = edge[1][0]
                intersected.insert(0, (edge[0][0], edge[1][0]))

        # sweep line algorithm
        visible_edges = list()
        for p in points:

            # check if any of the segments in intersected list crosses current segment
            good = True
            for segment in intersected:
                # if LineString([point, p[0][0]]).crosses(LineString([segment, intersected[segment]])):
                if LineString([point, p[0][0]]).crosses(LineString([segment[0], segment[1]])):
                    good = False
                    break

            # update intersected list
            if turn(point, p[0][0], p[1][0]) > 0:
                # intersected[p[0][0]] = p[1][0]
                intersected.insert(0, (p[0][0], p[1][0]))
            else:
                try:
                    # intersected.pop(p[0][0])
                    intersected.remove((p[0][0], p[1][0]))
                except ValueError: pass

            # add suitable points
            if good:

                # if a point is inside a restriction angle, it will not be returned
                if self.__restriction_pair is not None and self.__restriction_point is not None and self.__reverse_angle is not None:
                    l_point, r_point = self.__restriction_pair
                    if not point_in_angle(p[0][0], l_point, self.__restriction_point, r_point) != self.__reverse_angle:
                        continue

                # do not add same points
                try:
                    visible_edges.remove(p[0])
                except ValueError: pass
                visible_edges.append(p[0])

        return visible_edges

    """
    Angle approximation O(n) algorithm
    - only parameter is view_angle=1, it shows the calculation error
    - angle_count = math.floor(360 / view_angle) is the number of angles the surface is devided into
    - crosses = [None for angle in range(angle_count)] is an array to store minimal distances to points for each angle
    - when adding a segment (pair of points) for each segment point calculate its angle in degrees from point
    - for each of 2 angles fill the corresponding element of crosses with distance to the point
    - for each angle between 2 found angles (between means < pi) fill the corresponding element of crosses with distance to the segment for each angle
    - when returning visible edges check each element of crosses for None and for laying inside restriction angle
    First problem is that distances have to be calculated using projected crs
    Second problem is that O(n) constant is high (filling each in-between angle may nean up to 180 operations)
    All in all, this part of graph building is not bottle neck, so it will not be implemented soon
    """

