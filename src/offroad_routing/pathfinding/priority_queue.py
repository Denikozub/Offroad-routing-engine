import heapq
from typing import TypeVar
T = TypeVar("T")


class PriorityQueue(object):
    def __init__(self) -> None:
        self.__elements = list()

    def empty(self) -> bool:
        return not self.__elements

    def put(self, item: T, priority: float) -> None:
        heapq.heappush(self.__elements, (priority, item))

    def get(self) -> T:
        return heapq.heappop(self.__elements)[1]
