from geometry.algorithm import compare_points


class Path(object):
    def __init__(self, came_from, start, goal):
        self.came_from = came_from
        self.start = start
        self.goal = goal

    def retrace(self):
        current = self.goal
        path = list()
        while not compare_points(current, self.start):
            path.append(current)
            try:
                current = self.came_from[current]
            except KeyError:
                return list()
        path.append(self.start)  # optional
        path.reverse()  # optional
        return path
