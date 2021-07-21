from visibility_graph import VisibilityGraph

bbox = [34, 59, 34.2, 59.1]

map_data = VisibilityGraph()
map_data.compute_geometry(bbox=bbox)
map_data.build_dataframe(epsilon_polygon=0.003,
                         epsilon_linestring=0.001,
                         bbox_comp=10)

map_data.save_geometry("../maps/user_area.h5")
