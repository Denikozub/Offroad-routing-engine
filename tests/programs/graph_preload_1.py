from offroad_routing.visibility.visibility_graph import VisibilityGraph


def main():
    filename = "../maps/user_area.osm.pbf"
    bbox = [34, 59, 34.2, 59.1]

    vgraph = VisibilityGraph()
    vgraph.compute_geometry(bbox=bbox, filename=filename)
    vgraph.prune_geometry(epsilon_polygon=0.003,
                          epsilon_polyline=0.001,
                          bbox_comp=10,
                          remove_inner=True)

    vgraph.save_geometry("../maps/user_area.npy")


if __name__ == "__main__":
    main()
