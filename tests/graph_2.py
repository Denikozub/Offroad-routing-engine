import cProfile
import pstats
import timeit

from offroad_routing.visibility.visibility_graph import VisibilityGraph


def main():
    vgraph = VisibilityGraph()
    vgraph.load_geometry("../maps/kozlovo.h5")

    start = timeit.default_timer()

    with cProfile.Profile() as pr:
        vgraph.build_graph(inside_percent=1,
                           multiprocessing=True,
                           graph=False,
                           map_plot=False)

    stop = timeit.default_timer()
    print('Time: ', stop - start)

    stats = pstats.Stats(pr)
    stats.sort_stats(pstats.SortKey.TIME)
    stats.print_stats()


if __name__ == "__main__":
    main()
