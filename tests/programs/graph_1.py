import timeit

from offroad_routing import Geometry
from offroad_routing import VisibilityGraph


def main():
    geom = Geometry.load('user_area', '../maps')
    vgraph = VisibilityGraph(*geom.export(remove_inner=True))

    start = timeit.default_timer()

    vgraph.build(inside_percent=1, multiprocessing=False)

    stop = timeit.default_timer()
    print('Time: ', stop - start)

    print(vgraph.stats)


if __name__ == "__main__":
    main()
