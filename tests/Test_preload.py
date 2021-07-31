from visibility_graph import VisibilityGraph

filename = "../maps/kozlovo.osm.pbf"
bbox = [36.2, 56.5, 36.7, 57]

map_data = VisibilityGraph()
map_data.compute_geometry(bbox=bbox, filename=filename)
map_data.prune_geometry(epsilon_polygon=0.003,
                        epsilon_linestring=0.001,
                        bbox_comp=10)

map_data.save_geometry("../maps/kozlovo.h5")
