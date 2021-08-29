import cProfile
import pstats
import timeit

from visibility.visibility_graph import VisibilityGraph


def main():
    start = timeit.default_timer()

    vgraph = VisibilityGraph()
    vgraph.load_geometry("../maps/kozlovo.h5")

    map_plot = ('r', {0: "royalblue", 1: "r", 2: "k"})
    with cProfile.Profile() as pr:
        G, fig = vgraph.build_graph(inside_percent=0,
                                    multiprocessing=True,
                                    graph=True,
                                    map_plot=map_plot)

    print('edges: ', G.number_of_edges())
    print('nodes: ', G.number_of_nodes())

    stop = timeit.default_timer()
    print('Time: ', stop - start)

    stats = pstats.Stats(pr)
    stats.sort_stats(pstats.SortKey.TIME)
    stats.print_stats()


if __name__ == "__main__":
    main()
