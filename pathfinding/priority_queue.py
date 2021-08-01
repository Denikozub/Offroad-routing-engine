import heapq
from typing import List, Tuple, TypeVar
T = TypeVar("T")


class PriorityQueue(object):
    def __init__(self) -> None:
        self.elements: List[Tuple[float, T]] = []

    def empty(self) -> bool:
        return not self.elements

    def put(self, item: T, priority: float) -> None:
        heapq.heappush(self.elements, (priority, item))

    def get(self) -> T:
        return heapq.heappop(self.elements)[1]
