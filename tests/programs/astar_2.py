import timeit

from offroad_routing import AStar
from offroad_routing import Geometry
from offroad_routing import GpxTrack
from offroad_routing import VisibilityGraph


def main():
    geom = Geometry.load('kozlovo', '../maps')
    vgraph = VisibilityGraph(*geom.export(remove_inner=True))

    start = timeit.default_timer()

    pathfinder = AStar(vgraph)
    path = pathfinder.find((36.21, 56.62), (36.39, 56.66), heuristic_multiplier=10)

    stop = timeit.default_timer()
    print('Time: ', stop - start)

    track = GpxTrack(path)
    # track.write_file("track.gpx")
    track.visualize()
    # track.plot()


if __name__ == "__main__":
    main()
