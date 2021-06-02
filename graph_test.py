from visibility_graph import VisibilityGraph
from geometry.supporting_convex import *
# import mplleaflet

map_data = VisibilityGraph()
# map_data.load_geometry("kozlovo_extended_362_565_367_57")
map_data.load_geometry("kozlovo_36_5645_361_565")

map_plot = ('r', {0: "royalblue", 1: "r", 2: "k"})
G, fig = map_data.build_graph(find_pair_cutoff,
                              add_edges_inside=False,
                              inside_percent=0.4,
                              graph=True,
                              map_plot=None)

print('edges: ', G.number_of_edges())
print('nodes: ', G.number_of_nodes())
# mplleaflet.display(fig=fig)
