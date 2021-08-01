import timeit

import mplleaflet

from visibility.visibility_graph import VisibilityGraph


def main():
    start = timeit.default_timer()

    map_data = VisibilityGraph()
    map_data.load_geometry("../maps/user_area.h5")

    map_plot = ('r', {0: "royalblue", 1: "r", 2: "k"})
    G, fig = map_data.build_graph(inside_percent=0,
                                  graph=True,
                                  map_plot=map_plot)

    print('edges: ', G.number_of_edges())
    print('nodes: ', G.number_of_nodes())
    mplleaflet.display(fig=fig)

    stop = timeit.default_timer()
    print('Time: ', stop - start)


if __name__ == "__main__":
    main()
