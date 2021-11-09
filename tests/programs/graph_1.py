import timeit

from offroad_routing import VisibilityGraph


def main():
    vgraph = VisibilityGraph()
    vgraph.load_geometry("../maps/user_area.npy")

    start = timeit.default_timer()

    vgraph.build_graph(inside_percent=1, multiprocessing=False)

    stop = timeit.default_timer()
    print('Time: ', stop - start)


if __name__ == "__main__":
    main()
