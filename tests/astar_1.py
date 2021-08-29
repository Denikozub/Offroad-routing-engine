import timeit

from visibility.visibility_graph import VisibilityGraph
from pathfinding.astar import AStar


def main():
    start = timeit.default_timer()

    vgraph = VisibilityGraph()
    vgraph.load_geometry("../maps/user_area.h5")

    pathfinder = AStar(vgraph)
    path = pathfinder.find((34.02, 59.01), (34.12, 59.09))
    path.retrace()
    print(path.path)

    stop = timeit.default_timer()
    print('Time: ', stop - start)


if __name__ == "__main__":
    main()
