import timeit

from visibility.visibility_graph import VisibilityGraph
from pathfinding.astar import AStar
from pathfinding.gpx_track import GpxTrack


def main():
    vgraph = VisibilityGraph()
    vgraph.load_geometry("../maps/user_area.h5")

    start = timeit.default_timer()

    pathfinder = AStar(vgraph)
    path = pathfinder.find((34.02, 59.01), (34.12, 59.09))

    stop = timeit.default_timer()
    print('Time: ', stop - start)

    track = GpxTrack(path)
    track.write_file("track.gpx")
    track.visualize()


if __name__ == "__main__":
    main()
