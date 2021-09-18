import cProfile
import pstats
import timeit

from visibility.visibility_graph import VisibilityGraph


def main():
    vgraph = VisibilityGraph()
    vgraph.load_geometry("../maps/kozlovo.h5")

    start = timeit.default_timer()

    with cProfile.Profile() as pr:
        G, fig = vgraph.build_graph(inside_percent=0,
                                    multiprocessing=False,
                                    graph=True,
                                    map_plot=None)

    stop = timeit.default_timer()

    print('edges: ', G.number_of_edges())
    print('nodes: ', G.number_of_nodes())

    print('Time: ', stop - start)

    stats = pstats.Stats(pr)
    stats.sort_stats(pstats.SortKey.TIME)
    stats.print_stats()


if __name__ == "__main__":
    main()
