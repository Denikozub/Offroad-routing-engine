from visibility.visibility_graph import VisibilityGraph


def main():
    filename = "../maps/kozlovo.osm.pbf"
    bbox = [36.2, 56.5, 36.7, 57]

    vgraph = VisibilityGraph()
    vgraph.compute_geometry(bbox=bbox, filename=filename)
    vgraph.prune_geometry(epsilon_polygon=0.003,
                          epsilon_linestring=0.001,
                          bbox_comp=10)

    vgraph.save_geometry("../maps/kozlovo.h5")


if __name__ == "__main__":
    main()
