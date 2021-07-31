from visibility.visibility_graph import VisibilityGraph
from path import Path
from typing import Tuple


class AStar(object):
    def __init__(self, start: Tuple[float, float], end: Tuple[float, float]):
        self.start = start
        self.end = end

    def find(self, vgraph: VisibilityGraph) -> Path:

