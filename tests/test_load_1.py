from visibility_graph import VisibilityGraph

bbox = [36.0, 56.45, 36.1, 56.5]

map_data = VisibilityGraph()
map_data.compute_geometry(filename=filename, bbox=bbox)
map_data.build_dataframe(epsilon_polygon=0.003,
                         epsilon_linestring=0.001,
                         bbox_comp=10)

map_data.save_geometry("../maps/kozlovo_36_5645_361_565.h5")
