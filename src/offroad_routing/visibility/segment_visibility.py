from typing import Sequence, Optional, TypeVar, List, Tuple
from collections import OrderedDict

from offroad_routing.geometry.algorithms import \
    check_ray_segment_intersection, turn, point_in_angle, polar_angle, check_segment_intersection

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
        visible_edges = list()
        
        # check 2 points (of a segment) at a time
        for i, (a, b) in enumerate(self.__segments):
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
            for j, check_pair in enumerate(self.__segments):
                if j == i:
                    continue
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
            points.append((edge[0], edge[1]))  # keep info about pair and PointData
            points.append((edge[1], edge[0]))  # keep info about pair and PointData
        points.sort(key=lambda x: polar_angle(point, x[0][0]))

        # list of segments intersected by 0-angle ray
        intersected = OrderedDict()
        for edge in self.__segments:
            if check_ray_segment_intersection(point, (point[0] + 1, point[1]), edge[0][0], edge[1][0], True):
                index1 = str((edge[0][1], edge[0][2], edge[0][3] | 0))
                index2 = str((edge[1][1], edge[1][2], edge[1][3] | 0))
                intersected[index1 + index2] = (edge[0][0], edge[1][0])
        self.__segments.clear()

        visible_edges = dict()
        for p in points:
            # check if any of the segments in intersected list crosses current segment
            for segment in reversed(intersected.values()):
                if check_segment_intersection(point, p[0][0], segment[0], segment[1]):
                    break
            else:
                if self.__restriction_pair is None:
                    visible_edges[str(p[0][1]) + str(p[0][2]) + str(p[0][3] | 0)] = p[0]
                else:
                    l_point, r_point = self.__restriction_pair
                    if point_in_angle(p[0][0], l_point, self.__restriction_point, r_point) != self.__reverse_angle:
                        visible_edges[str(p[0][1]) + str(p[0][2]) + str(p[0][3] | 0)] = p[0]

            # update intersected list
            index1 = str((p[0][1], p[0][2], p[0][3] | 0))
            index2 = str((p[1][1], p[1][2], p[1][3] | 0))
            if turn(point, p[0][0], p[1][0]) > 0:
                intersected[index1 + index2] = (p[0][0], p[1][0])
            else:
                intersected.pop(index1 + index2, None)

        return list(visible_edges.values())

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
