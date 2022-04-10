from networkx import astar_path
from offroad_routing.geometry.algorithms import compare_points
from offroad_routing.geometry.algorithms import point_distance
from offroad_routing.geometry.geom_types import TPoint
from offroad_routing.pathfinding.path import Path
from offroad_routing.pathfinding.priority_queue import PriorityQueue
from offroad_routing.visibility.visibility_graph import VisibilityGraph
from osmnx import get_nearest_node


class AStar:
    """
    Find off-road routes using A* algorithm and visibility graph.
    """

    __slots__ = ("__vgraph",)

    def __init__(self, vgraph):
        """
        :param VisibilityGraph vgraph: visibility graph with computed geometry
        """
        self.__vgraph = vgraph

    @staticmethod
    def __heuristic(node: TPoint, goal: TPoint, heuristic_multiplier: int) -> float:
        return point_distance(node, goal) * heuristic_multiplier

    def __find_notbuilt(self, start, goal, heuristic_multiplier):
        # PointData format
        start_data = (start, None, None, None, None)
        goal_data = (goal, None, None, None, None)

        # vgraph nodes incident to goal point (defined by object and position in the object)
        goal_neighbours = self.__vgraph.incident_vertices(goal_data)
        if len(goal_neighbours) == 0:
            raise RuntimeError("Goal point has no neighbours on the graph")
        goal_data = (goal, None, None, None, goal_neighbours[0][4])
        goal_neighbours = [(i[1], i[2], i[3]) for i in goal_neighbours]

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

            neighbours = self.__vgraph.incident_vertices(current)

            # if current is goal neighbour add it to neighbour list
            goal_neighbour = (current[1], current[2],
                              current[3]) in goal_neighbours
            if goal_neighbour:
                neighbours.insert(0, goal_data)

            for neighbour in neighbours:
                neighbour_point, neighbour_weight = neighbour[0], neighbour[4]
                new_cost = cost_so_far[current_point] + point_distance(current_point,
                                                                       neighbour_point) * neighbour_weight

                # neighbour not visited or shorter path found
                if neighbour_point not in cost_so_far or new_cost < cost_so_far[neighbour_point]:
                    cost_so_far[neighbour_point] = new_cost
                    priority = new_cost + \
                        AStar.__heuristic(
                            goal, neighbour_point, heuristic_multiplier)
                    frontier.put(neighbour, priority)
                    came_from[neighbour_point] = current_point

        return Path.retrace(came_from, start, goal)

    def __node_coordinates(self, node):
        coords = self.__vgraph.graph.nodes[node]
        return coords['x'], coords['y']

    def __find_prebuilt(self, start, goal):
        source_node = get_nearest_node(
            self.__vgraph.graph, (start[1], start[0]))
        target_node = get_nearest_node(self.__vgraph.graph, (goal[1], goal[0]))
        path = astar_path(self.__vgraph.graph, source_node,
                          target_node, weight='weight')
        return Path([self.__node_coordinates(node) for node in path], start, goal)

    def find(self, start, goal, heuristic_multiplier=10):
        """
        Find route from point start to point goal.

        :param TPoint start: start point
        :param TPoint goal: goal point
        :param int heuristic_multiplier: multiplier to weight heuristic \
        (http://theory.stanford.edu/~amitp/GameProgramming/Heuristics.html#scale)
        :rtype: offroad_routing.pathfinding.path.Path
        """

        prebuilt = self.__vgraph.stats['number_of_edges'] > 0
        return self.__find_notbuilt(start, goal, heuristic_multiplier) \
            if not prebuilt else self.__find_prebuilt(start, goal)
