import pandas as pd
import numpy as np
import math
import matplotlib.pyplot as plt
import parsers.mp_parser as mpp


class Iterative:

    def __init__(self, bbox, curr, wpt, start, angle_count, curr_type, decline, plot=None):
        self.bbox = bbox
        self.curr = curr
        self.wpt = wpt
        self.start = start
        self.angle_count = angle_count
        self.curr_type = curr_type
        self.decline = decline
        self.plot = plot

    @staticmethod
    def rel_dist(x, y):
        return math.sqrt(x ** 2 + y ** 2)

    @staticmethod
    def vec(a, b):
        return np.array(b) - np.array(a)

    @staticmethod
    def mod(v):
        return (v[0] ** 2 + v[1] ** 2) ** 0.5

    def point_in_angle(self, p, a, b, c):
        delta = 0.00000001
        if (b == a) or (b == c) or (b == p):
            return 0
        return math.fabs(math.acos(np.dot(self.vec(b, a), self.vec(b, c)) /
                                   (self.mod(self.vec(b, a)) * self.mod(self.vec(b, c)))) -
                         math.acos(np.dot(self.vec(b, a), self.vec(b, p)) /
                                   (self.mod(self.vec(b, a)) * self.mod(self.vec(b, p)))) -
                         math.acos(np.dot(self.vec(b, p), self.vec(b, c)) /
                                   (self.mod(self.vec(b, p)) * self.mod(self.vec(b, c))))) < delta

    def fill_dist(self, x1, y1, x2, y2, type_line, df, plot_xy):
        dist_to_wpt = self.rel_dist(self.wpt[0], self.wpt[1])
        if (self.rel_dist(x1, y1) > dist_to_wpt) and (self.rel_dist(x2, y2) > dist_to_wpt):
            return
        # if self.plot:
            # plt.plot([y1 + self.curr[1], y2 + self.curr[1]], [x1 + self.curr[0], x2 + self.curr[0]], color='red')
        for i in range(self.angle_count):
            k_curr = math.tan((i * 360 / self.angle_count + self.decline)*math.pi/180)
            # delta_angle = math.tan(math.pi/180)
            if x1 == x2:
                k_segment = 1000
            else:
                k_segment = (y1 - y2) / (x1 - x2)
            # if abs(k_segment - k_curr) < delta_angle:
            # go there + check quarter
            b_segment = y1 - k_segment * x1
            x = b_segment / (k_curr - k_segment)
            y = k_curr * x
            if not self.point_in_angle((x, y), (x1, y1), (0, 0), (x2, y2)):
                continue
            dist_from_curr = self.rel_dist(x, y)
            if dist_from_curr > dist_to_wpt:
                continue
            if (type_line in mpp.MpParser.polyline_good) and (self.curr_type <= 0):
                if math.isnan(df.dist_good[i]) or (df.dist_good[i] > dist_from_curr):
                    df.dist_good[i] = dist_from_curr
                    if self.plot:
                        plot_xy.good_x[i] = x + self.curr[0]
                        plot_xy.good_y[i] = y + self.curr[1]
                        # plt.scatter(plot_xy.good_y[i], plot_xy.good_x[i], color='orange')
                    if (not math.isnan(df.dist_bad[i])) and (df.dist_bad[i] > df.dist_good[i]):
                        df.dist_bad[i] = np.nan
                        if self.plot:
                            plot_xy.bad_x[i] = np.nan
                            plot_xy.bad_y[i] = np.nan
            if (type_line in mpp.MpParser.polyline_bad) and (self.curr_type >= 0):
                if (math.isnan(df.dist_bad[i]) or (df.dist_bad[i] > dist_from_curr)) \
                        and (dist_from_curr < df.dist_good[i]):
                    df.dist_bad[i] = dist_from_curr
                    if self.plot:
                        plot_xy.bad_x[i] = x + self.curr[0]
                        plot_xy.bad_y[i] = y + self.curr[1]
                        # plt.scatter(plot_xy.bad_y[i], plot_xy.bad_x[i], color='blue')

    def creat_df(self):
        parser = mpp.MpParser(self.bbox)
        polyline_count = parser.open_mp()

        df = pd.DataFrame(index=[i for i in range(self.angle_count)],
                          columns=['dist_bad', 'dist_good', 'angle_wpt', 'angle_from'])

        polyline = []
        polyline.append(0)
        if self.plot:
            plot_xy = pd.DataFrame(index=[i for i in range(self.angle_count)],
                                   columns=['good_x', 'good_y', 'bad_x', 'bad_y'])
        else:
            plot_xy = None
        for i in range(polyline_count):
            coord, type_line = parser.parse_mp(polyline)
            if coord == 0:
                continue
            j = 2
            length = len(coord)
            while j < length:
                self.fill_dist(float(coord[j - 2]) - self.curr[0], float(coord[j - 1]) - self.curr[1],
                               float(coord[j]) - self.curr[0], float(coord[j + 1]) - self.curr[1], type_line, df, plot_xy)
                j += 2
        fig = None
        if self.plot:
            fig = plt.figure()
            plt.scatter(self.curr[1], self.curr[0], color='black');
            plt.scatter(self.wpt[1] + self.curr[1], self.wpt[0] + self.curr[0], color='black');
            plt.plot([self.curr[1], self.wpt[1] + self.curr[1]], [self.curr[0], self.wpt[0] + self.curr[0]], color='black');
            for i in range(self.angle_count):
                if not math.isnan(plot_xy.bad_y[i]):
                    plt.scatter(plot_xy.bad_y[i], plot_xy.bad_x[i], color='blue');
                if not math.isnan(plot_xy.good_y[i]):
                    plt.scatter(plot_xy.good_y[i], plot_xy.good_x[i], color='orange');
        return df, fig

    def fill_df(self, df):
        for i in range(self.angle_count):
            angle = abs(math.atan2(self.wpt[1], self.wpt[0]) * 180 / math.pi - i * 360 / self.angle_count)
            df.angle_wpt[i] = angle if angle < 180 else (360 - angle)
            angle = abs(math.atan2(self.start[1], self.start[0]) * 180 / math.pi - i * 360 / self.angle_count)
            df.angle_from[i] = angle if angle < 180 else (360 - angle)
        df.dist_bad *= 10000
        df.dist_good *= 10000
