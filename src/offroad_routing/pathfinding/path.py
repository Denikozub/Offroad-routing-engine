from offroad_routing.geometry.algorithms import compare_points
from offroad_routing.geometry.geom_types import TPath
from offroad_routing.geometry.geom_types import TPoint


class Path:

    __slots__ = ("__came_from", "__start", "__goal", "__path")

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
                raise Exception("Could not retrace path!")
        self.__path.append(self.__start)
        self.__path.reverse()

    @property
    def path(self) -> TPath:
        return self.__path.copy()

    @property
    def start(self) -> TPoint:
        return self.__start

    @property
    def goal(self) -> TPoint:
        return self.__goal
