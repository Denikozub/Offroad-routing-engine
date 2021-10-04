import timeit

from offroad_routing.visibility.visibility_graph import VisibilityGraph
from offroad_routing.pathfinding.astar import AStar
from offroad_routing.pathfinding.gpx_track import GpxTrack


def main():
    vgraph = VisibilityGraph()
    vgraph.load_geometry("../maps/kozlovo.npy")

    start = timeit.default_timer()

    pathfinder = AStar(vgraph)
    path = pathfinder.find((36.21, 56.51), (36.5, 56.69), default_weight=10, heuristic_multiplier=10)

    stop = timeit.default_timer()
    print('Time: ', stop - start)

    track = GpxTrack(path)
    # track.write_file("track.gpx")
    track.visualize()


if __name__ == "__main__":
    main()
