import timeit

from offroad_routing import AStar
from offroad_routing import GpxTrack
from offroad_routing import VisibilityGraph


def main():
    vgraph = VisibilityGraph()
    vgraph.load_geometry("../maps/kozlovo.npy")

    start = timeit.default_timer()

    pathfinder = AStar(vgraph)
    path = pathfinder.find((36.21, 56.62), (36.39, 56.66),
                           default_surface='grass', heuristic_multiplier=10)

    stop = timeit.default_timer()
    print('Time: ', stop - start)

    track = GpxTrack(path)
    # track.write_file("track.gpx")
    track.visualize()


if __name__ == "__main__":
    main()
