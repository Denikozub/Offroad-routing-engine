from offroad_routing.visibility.visibility_graph import VisibilityGraph


def main():
    bbox = [34, 59, 34.2, 59.1]

    vgraph = VisibilityGraph()
    vgraph.compute_geometry(bbox=bbox)
    vgraph.prune_geometry(epsilon_polygon=0.003,
                          epsilon_polyline=0.001,
                          bbox_comp=10)

    vgraph.save_geometry("../maps/user_area.h5")


if __name__ == "__main__":
    main()
