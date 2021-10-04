import timeit

from offroad_routing.visibility.visibility_graph import VisibilityGraph
from offroad_routing.pathfinding.astar import AStar
from offroad_routing.pathfinding.gpx_track import GpxTrack


def main():
    vgraph = VisibilityGraph()
    vgraph.load_geometry("../maps/user_area.npy")

    start = timeit.default_timer()

    pathfinder = AStar(vgraph)
    path = pathfinder.find((34.02, 59.01), (34.12, 59.09), default_weight=10, heuristic_multiplier=10)

    stop = timeit.default_timer()
    print('Time: ', stop - start)

    track = GpxTrack(path)
    # track.write_file("track.gpx")
    track.visualize()


if __name__ == "__main__":
    main()
