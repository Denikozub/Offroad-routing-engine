from visibility_graph import VisibilityGraph

filename = "../maps/kozlovo_extended.osm.pbf"
bbox = [36.2, 56.5, 36.7, 57]

map_data = VisibilityGraph()
map_data.compute_geometry(filename=filename, bbox=bbox)
map_data.build_dataframe(epsilon_polygon=0.003,
                         epsilon_linestring=0.001,
                         bbox_comp=10)

map_data.save_geometry("../maps/kozlovo_extended_362_565_367_57.h5")
