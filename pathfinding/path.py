from typing import TypeVar

from geometry.algorithms import compare_points

TPoint = TypeVar("TPoint")  # Tuple[float, float]


class Path(object):
    def __init__(self, came_from: dict, start: TPoint, goal: TPoint):
        self.came_from = came_from
        self.start = start
        self.goal = goal
        self.path = None

    def retrace(self) -> None:
        self.path = list()
        current = self.goal
        while not compare_points(current, self.start):
            self.path.append(current)
            try:
                current = self.came_from[current]
            except KeyError:
                return
        self.path.append(self.start)
        self.path.reverse()
