from typing import Tuple

from geometry.algorithm import dist
from path import Path
from visibility.visibility_graph import VisibilityGraph
from priority_queue import PriorityQueue


class AStar(object):
    def __init__(self, vgraph: VisibilityGraph) -> None:
        self.vgraph = vgraph

    @staticmethod
    def heuristic(node: Tuple[float, float], goal: Tuple[float, float]) -> float:
        return dist(node, goal)

    def find(self, start: Tuple[float, float], goal: Tuple[float, float]) -> Path:
        frontier = PriorityQueue()

