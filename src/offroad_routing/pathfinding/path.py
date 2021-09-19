from typing import TypeVar

from offroad_routing.geometry.algorithms import compare_points

TPoint = TypeVar("TPoint")  # Tuple[float, float]
TPath = TypeVar("TPath")  # List[TPoint]


class Path(object):
    def __init__(self, came_from: dict, start: TPoint, goal: TPoint):
        self.__came_from = came_from
        self.__start = start
        self.__goal = goal
        self.__path = list()
        self.__retrace()

    def __retrace(self) -> None:
        current = self.__goal
        while not compare_points(current, self.__start):
            self.__path.append(current)
            try:
                current = self.__came_from[current]
            except KeyError:
                return
        self.__path.append(self.__start)
        self.__path.reverse()

    def path(self) -> TPath:
        return self.__path.copy()

    def start(self) -> TPoint:
        return self.__start

    def goal(self) -> TPoint:
        return self.__goal
