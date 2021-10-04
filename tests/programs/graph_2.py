import cProfile
import pstats
import timeit

from offroad_routing.visibility.visibility_graph import VisibilityGraph


def main():
    vgraph = VisibilityGraph()
    vgraph.load_geometry("../maps/kozlovo.npy")

    start = timeit.default_timer()

    with cProfile.Profile() as pr:
        G = vgraph.build_graph(inside_percent=0, multiprocessing=False)

    stop = timeit.default_timer()
    print('Time: ', stop - start)

    print(G.number_of_edges(), G.number_of_nodes())

    stats = pstats.Stats(pr)
    stats.sort_stats(pstats.SortKey.TIME)
    stats.print_stats()


if __name__ == "__main__":
    main()
