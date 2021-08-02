from typing import TypeVar, Optional

from geometry.algorithm import dist, compare_points
from pathfinding.path import Path
from visibility.visibility_graph import VisibilityGraph
from pathfinding.priority_queue import PriorityQueue

TPoint = TypeVar("TPoint")  # Tuple[float, float]
PointData = TypeVar("PointData")  # Tuple[TPoint, Optional[int], Optional[int], Optional[bool], Optional[int]]


class AStar(object):
    def __init__(self, vgraph: VisibilityGraph) -> None:
        self.vgraph = vgraph

    @staticmethod
    def heuristic(node: TPoint, goal: TPoint) -> float:
        return dist(node, goal)

    def find(self, start: TPoint, goal: TPoint) -> Optional[Path]:

        # PointData format
        start_data = (start, None, None, None, None)
        goal_data = (goal, None, None, None, None)

        # vgraph nodes incident to goal point
        goal_neighbours = [(i[1], i[2], i[3]) for i in self.vgraph.incident_vertices(goal_data)]
        if not goal_neighbours:
            return None

        frontier = PriorityQueue()
        frontier.put(start_data, 0)
        came_from = dict()
        came_from[start_data[0]] = None
        cost_so_far = dict()
        cost_so_far[start_data[0]] = 0

        while not frontier.empty():
            current = frontier.get()
            current_point = current[0]

            if compare_points(current_point, goal):
                break

            neighbours = self.vgraph.incident_vertices(current)

            # add goal as one of neighbours
            goal_neighbour = (current[1], current[2], current[3]) in goal_neighbours
            if goal_neighbour:
                neighbours.insert(0, goal_data)

            for neighbour in neighbours:
                neighbour_point = neighbour[0]
                new_cost = cost_so_far[current_point] + dist(current_point, neighbour_point)
                if neighbour_point not in cost_so_far or new_cost < cost_so_far[neighbour_point]:
                    cost_so_far[neighbour_point] = new_cost
                    priority = new_cost + self.heuristic(goal, neighbour_point)
                    frontier.put(neighbour, priority)
                    came_from[neighbour_point] = current_point

        return Path(came_from, start, goal)

