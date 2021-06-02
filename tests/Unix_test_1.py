from visibility_graph import VisibilityGraph
import mplleaflet

map_data = VisibilityGraph()
map_data.load_geometry("../maps/kozlovo_36_5645_361_565.h5")

map_plot = ('r', {0: "royalblue", 1: "r", 2: "k"})
G, fig = map_data.build_graph(inside_percent=0,
                              graph=True,
                              map_plot=map_plot)

print('edges: ', G.number_of_edges())
print('nodes: ', G.number_of_nodes())
mplleaflet.display(fig=fig)
