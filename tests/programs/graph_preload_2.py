from offroad_routing import VisibilityGraph


def main():
    filename = "../maps/kozlovo.osm.pbf"
    bbox = [36.2, 56.61, 36.4, 56.67]

    vgraph = VisibilityGraph()
    vgraph.compute_geometry(bbox=bbox, filename=filename)
    vgraph.prune_geometry(remove_inner=True)

    vgraph.save_geometry("../maps/kozlovo.npy")


if __name__ == "__main__":
    main()
