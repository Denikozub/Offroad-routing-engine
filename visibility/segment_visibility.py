from typing import Sequence, Optional, TypeVar, List, Tuple

from geometry.algorithms import check_ray_segment_intersection, turn, point_in_angle, polar_angle, check_segment_intersection

TPoint = TypeVar("TPoint")  # Tuple[float, float]
PointData = TypeVar("PointData")  # Tuple[TPoint, Optional[int], Optional[int], Optional[bool], Optional[int]]


class SegmentVisibility(object):

    def __init__(self):
        self.__segments = list()
        self.__restriction_pair = None
        self.__restriction_point = None
        self.__reverse_angle = None

    def add_pair(self, pair: Optional[Tuple[PointData, PointData]]) -> None:
        if pair is None:
            return
        assert len(pair) == 2
        self.__segments.append(pair)

    def add_line(self, line: Optional[Sequence[PointData]]) -> None:
        if line is None:
            return
        for i in range(len(line) - 1):
            self.add_pair((line[i], line[i + 1]))

    def set_restriction_angle(self, restriction_pair: Sequence[TPoint],
                              restriction_point: TPoint, reverse_angle: bool) -> None:
        assert len(restriction_pair) == 2

        self.__restriction_pair = restriction_pair
        self.__restriction_point = restriction_point
        self.__reverse_angle = reverse_angle

    def get_edges_brute(self, point: TPoint) -> List[PointData]:
        segment_number = len(self.__segments)
        visible_edges = list()

        # check 2 points (of a segment) at a time
        for i in range(segment_number):
            a, b = self.__segments[i]
            a_point, b_point = a[0], b[0]

            if self.__restriction_pair is not None:
                l_point, r_point = self.__restriction_pair
                a_in_angle = not point_in_angle(a_point, l_point, self.__restriction_point, r_point) != self.__reverse_angle
                b_in_angle = not point_in_angle(b_point, l_point, self.__restriction_point, r_point) != self.__reverse_angle
                if a_in_angle and b_in_angle:
                    continue
            else:
                a_in_angle, b_in_angle = False, False

            # for each of 2 points check intersection with all other segments
            a_is_visible, b_is_visible = not a_in_angle, not b_in_angle
            for j in range(segment_number):
                if j == i:
                    continue
                check_pair = self.__segments[j]
                check_a, check_b = check_pair[0][0], check_pair[1][0]
                a_is_visible = not a_in_angle and not check_segment_intersection(point, a_point, check_a, check_b)
                b_is_visible = not b_in_angle and not check_segment_intersection(point, b_point, check_a, check_b)
                if not a_is_visible and not b_is_visible:
                    break

            if a_is_visible:
                visible_edges.append(a)
            if b_is_visible:
                visible_edges.append(b)
        self.__segments.clear()
        return visible_edges

    def get_edges_sweepline(self, point: TPoint) -> List[PointData]:
        # list of points sorted by angle
        points = list()
        for edge in self.__segments:
            points.append((edge[0], edge[1]))
            points.append((edge[1], edge[0]))
        points.sort(key=lambda x: polar_angle(point, x[0][0]))

        # list of segments intersected by 0-angle ray
        intersected = list()
        for edge in self.__segments:
            if check_ray_segment_intersection(point, (point[0] + 1, point[1]), edge[0][0], edge[1][0], True):
                intersected.insert(0, (edge[0][0], edge[1][0]))

        visible_edges = list()
        for p in points:

            # check if any of the segments in intersected list crosses current segment
            crosses = False
            for segment in intersected:
                if check_segment_intersection(point, p[0][0], segment[0], segment[1]):
                    crosses = True
                    break

            # update intersected list
            if turn(point, p[0][0], p[1][0]) > 0:
                intersected.insert(0, (p[0][0], p[1][0]))
            else:
                try:
                    intersected.remove((p[0][0], p[1][0]))
                except ValueError:
                    pass

            # add suitable points
            if not crosses:

                # if a point is inside a restriction angle, it will not be returned
                if self.__restriction_pair is not None:
                    l_point, r_point = self.__restriction_pair
                    p_in_angle = not point_in_angle(p[0][0], l_point, self.__restriction_point, r_point) != self.__reverse_angle
                    if p_in_angle:
                        continue

                # do not add same points
                try:
                    visible_edges.remove(p[0])
                except ValueError:
                    pass
                visible_edges.append(p[0])

        self.__segments.clear()
        return visible_edges

    """
    Angle approximation Denis Kozub O(n) algorithm
    - only parameter is view_angle=1, it shows the calculation error
    - angle_count = math.floor(360 / view_angle) is the number of angles the surface is divided into
    - crosses = [None for angle in range(angle_count)] is an array to store minimal distances to points for each angle
    - when adding a segment (pair of points) for each segment point calculate its angle in degrees from point
    - for each of 2 angles fill the corresponding element of crosses with distance to the point
    - for each angle between 2 found angles (between means < pi)
    fill the corresponding element of crosses with distance to the segment for each angle
    - when returning visible edges check each element of crosses for None and for laying inside restriction angle
    First problem is that distances have to be calculated using projected crs
    Second problem is that O(n) constant is high (filling each in-between angle may mean up to 180 operations)
    All in all, this part of graph building is not bottle neck, so it will not be implemented soon
    """
