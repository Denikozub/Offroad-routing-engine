from offroad_routing import VisibilityGraph


def main():
    filename = "../maps/kozlovo.osm.pbf"
    bbox = [36.2, 56.5, 36.7, 56.7]

    vgraph = VisibilityGraph()
    vgraph.compute_geometry(bbox=bbox, filename=filename)
    vgraph.prune_geometry(epsilon_polygon=0.003,
                          epsilon_polyline=0.001,
                          bbox_comp=10,
                          remove_inner=True)

    vgraph.save_geometry("../maps/kozlovo.npy")


if __name__ == "__main__":
    main()
