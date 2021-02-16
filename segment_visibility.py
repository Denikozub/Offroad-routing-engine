from geometry import intersects, point_in_angle


class SegmentVisibility:

    segments = list()
    restriction_pair = None
    restriction_point = None
    
    def add_pair(self, pair):
        self.segments.append(pair)
    
    def add_line(self, line):
        for i in range(len(line) - 1):
            self.add_pair((line[i], line[i + 1]))
    
    def get_edges(self, point):
        segment_number = len(self.segments)
        visible_edges = list()
        for i in range(segment_number):
            a, b = self.segments[i]
            a_point, b_point = a[0], a[0]
            if self.restriction_pair is not None and self.restriction_point is not None:
                l_point, r_point = self.restriction_pair
                intersects_a = not point_in_angle(a_point, l_point, self.restriction_point, r_point)
                intersects_b = not point_in_angle(b_point, l_point, self.restriction_point, r_point)
                if intersects_a and intersects_b:
                    continue
            else:
                intersects_a, intersects_b = False, False
            for j in range(segment_number):
                if j == i:
                    continue
                check_pair = self.segments[j]
                check_a, check_b = check_pair[0][0], check_pair[1][0]
                if not intersects_a and intersects(point, a_point, check_a, check_b, segment=True):
                    intersects_a = True
                if not intersects_b and intersects(point, b_point, check_a, check_b, segment=True):
                    intersects_b = True
                if intersects_a and intersects_b:
                    break
            if not intersects_a:
                visible_edges.append(a)
            if not intersects_b:
                visible_edges.append(b)
        return visible_edges