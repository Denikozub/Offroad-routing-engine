from typing import List

from geopandas import GeoDataFrame
from offroad_routing.geometry.algorithms import compare_points
from offroad_routing.geometry.geom_types import TPath
from offroad_routing.geometry.geom_types import TPoint
from shapely.geometry import LineString


class Path:

    __slots__ = ("__start", "__goal", "__path")

    def __init__(self, path: List[TPoint], start: TPoint, goal: TPoint):
        self.__path = path
        self.__start = start
        self.__goal = goal

    @classmethod
    def retrace(cls, came_from: dict, start: TPoint, goal: TPoint) -> "Path":
        path, current = list(), goal
        while not compare_points(current, start):
            path.append(current)
            try:
                current = came_from[current]
            except KeyError:
                raise Exception("Could not retrace path!")
        path.append(start)
        path.reverse()
        return cls(path, start, goal)

    @property
    def path(self) -> TPath:
        return self.__path.copy()

    @property
    def start(self) -> TPoint:
        return self.__start

    @property
    def goal(self) -> TPoint:
        return self.__goal

    def to_gpd(self) -> GeoDataFrame:
        return GeoDataFrame({'geometry': (LineString(self.__path),)}, crs='epsg:4326')
