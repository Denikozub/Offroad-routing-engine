from visibility_graph import VisibilityGraph

map_data = VisibilityGraph()
map_data.load_geometry("../maps/kozlovo_36_5645_361_565.h5")

G, fig = map_data.build_graph(inside_percent=0.4,
                              graph=True,
                              map_plot=None)

print('edges: ', G.number_of_edges())
print('nodes: ', G.number_of_nodes())
