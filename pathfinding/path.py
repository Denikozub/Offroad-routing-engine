from geometry.algorithms import compare_points


class Path(object):
    def __init__(self, came_from, start, goal):
        self.came_from = came_from
        self.start = start
        self.goal = goal
        self.path = None

    def retrace(self):
        current = self.goal
        self.path = list()
        while not compare_points(current, self.start):
            self.path.append(current)
            try:
                current = self.came_from[current]
            except KeyError:
                return list()
        self.path.append(self.start)
        self.path.reverse()
