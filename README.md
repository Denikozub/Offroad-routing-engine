# Off-road Navigation System
[__Documentation__](https://github.com/Denikozub/Offroad-routing-engine#documentation)  
[__Usage__](https://github.com/Denikozub/Offroad-routing-engine#usage)  
[__Graph visualization__](https://denikozub.github.io/Offroad-routing-engine/)
___
by Denis Kozub
- World discretization using _visibility graphs_
- O(nh log n) _reduced_ visibility graph algorithm (see [algorithm explanation](https://github.com/Denikozub/Offroad-routing-engine/blob/main/docs/algorithm.pdf))
- A* pathfinding without graph precomputing
- _Hierarchical approach_ for graph building
- No projected crs, works in any part of the world
- Open source OpenStreetMap data (see [OSM data explanation](https://github.com/Denikozub/Offroad-routing-engine/blob/main/docs/OSM_data.ipynb))
- Downloading OMS maps at runtime
- Saving and loading precomputed map data
- Multiprocessing and visualization tools support

<img src="docs/Route.png" alt="" width="800"/>

Scope of application:
- Extending functionality of other routing engines  
- Road and facilities design  
- Rescue and military operations planning  
- Route planning for hiking and tourism  


# Documentation

### PointData explanation

In order to speed up computation, low-level data transfer approach is used.  
Data about points, polylines and polygons is transferred using tuples instead of structures.

~~~python
TPoint = NewType("Point", Tuple[float, float])  
~~~


Node of the graph is unambiguously set either by its coordinates or by its position in an object.

~~~python
PointData = NewType("PointData", Tuple[TPoint,      # x, y - point coordinates
                                 Optional[int],     # number of object where point belongs
                                 Optional[int],     # number of point in object
                                 Optional[bool],    # object is polygon (True) or linestring (False)
                                 Optional[int]])    # surface weight
~~~


### VisibilityGraph

VisibilityGraph is a class for building a visibility graph on a given area from OSM data  


~~~python
compute_geometry(bbox, filename=None)
~~~

Parse OSM file (area in bounding box) to retrieve information about roads and surface.  
This method uses [pyrosm](https://pypi.org/project/pyrosm/), which requires [geopandas](https://geopandas.org/) to be installed.  
What is more, curl and [osmosis](https://wiki.openstreetmap.org/wiki/Osmosis) are required for downloading the map.  
__bbox__: sequence in format min_lon, min_lat, max_lon, max_lat  
__filename__: None (map will be downloaded) or str in .osm.pbf format  
__return__ None  


~~~python
prune_geometry(epsilon_polygon=None, epsilon_linestring=None, bbox_comp=15, remove_inner=False)
~~~

Transform retrieved data:
* transform geometry to tuple of points
* run Ramer-Douglas-Peucker to geometry objects
* get rid of small objects with bbox_comp parameter
* add data about convex hull for polygons  

Default parameters will be computed for the given area to provide best performance.  
__epsilon_polygon__: None or Ramer-Douglas-Peucker algorithm parameter for polygons  
__epsilon_linestring__: None or Ramer-Douglas-Peucker algorithm parameter for linestrings  
__bbox_comp__: None or int - scale polygon comparison parameter (to size of map bbox)  
__remove_inner__: bool - remove inner polygons for other polygons  
(currently their share of all polygon is too low due to lack of OSM data)  
__return__ None  


~~~python
save_geometry(filename)
~~~

Save computed data to .h5 file  
__filename__: .h5 string filename  
__return__: None


~~~python
load_geometry(filename)
~~~

Load saved data from .h5 file  
__filename__: .h5 string filename  
__return__: None


~~~python
incident_vertices(point_data, inside_percent=1)
~~~

Finds all incident vertices in visibility graph for given point.  
__point_data__: PointData of given point  
__inside_percent__: float (from 0 to 1) - controls the number of inner polygon edges  
__return__ list of PointData of all visible points


~~~python
build_graph(inside_percent=0.4, multiprocessing=True, graph=False, map_plot=False, crs='EPSG:4326')
~~~

Compute [and build] [and plot] visibility graph  
__inside_percent__: float (from 0 to 1) - controls the number of inner polygon edges  
__multiprocessing__: bool - speed up computation for dense areas using multiprocessing  
__graph__: bool - build a networkx.MultiGraph (True) or not (False)  
__map_plot__: plot visibility graph (True) or not (False)  
__crs__: string - coordinate reference system  
__return__ networkx.MultiGraph (None if graph is False), matplotlib.figure.Figure (None if map_plot is None)


### Astar

~~~python
find(start, goal, default_weight=10, heuristic_multiplier=10)
~~~

Run A* algorithm to find path from start to goal.  
__default_weight__: weight for unmapped OSM areas  
__heuristic_multiplier__: variable to alter heuristic value due to total weights  
__return__ path.Path object


### GpxTrack

GpxTrack is a class to help visualize and save computed paths.


~~~python
write_file(filename)
~~~

Save path to .gpx file.  
__filename__: .gpx string filename  
__return__: None


~~~python
visualize()
~~~
Generate link to visualize path using https://nakarte.me  
__return__: None


# Usage

[ipynb notebook](https://github.com/Denikozub/Offroad-routing-engine/blob/main/docs/graph_usage.ipynb)


### Downloading and processing data

There are two ways you can obtain OSM data in osm.pbf format:  
- Download it yourself: [parts of the world](https://download.geofabrik.de/), [cities](https://download.bbbike.org/osm/bbbike/), [adjustable area](https://extract.bbbike.org/) (via mail), [adjustable area](https://export.hotosm.org/en/v3/) (online), [planet](https://planet.maps.mail.ru/pbf/)
- Let the program download it for you

If the map is downloaded you can specify the filename:


```python
from offroad_routing.visibility.visibility_graph import VisibilityGraph

vgraph = VisibilityGraph()
filename = "../maps/kozlovo.osm.pbf"
bbox = [36.2, 56.5, 36.7, 56.7]
vgraph.compute_geometry(bbox=bbox, filename=filename)
```

Or, alternatively, you can only specify the bounding box, and the map will be downloaded automatically ([curl](https://curl.se/) & [osmosis](https://wiki.openstreetmap.org/wiki/Osmosis) required):


```python
bbox = [34, 59, 34.2, 59.1]
vgraph.compute_geometry(bbox=bbox)
```

Data inside this area can be processed using VisibilityGraph with chosen or default parameters.  
If not specified, optimal parameters will be computed by the algorithm.


```python
vgraph.prune_geometry(epsilon_polygon=0.003,
                      epsilon_linestring=0.001,
                      bbox_comp=10)
```

Computed data can also be saved in .h5 file to skip data processing the next time:


```python
vgraph.save_geometry("../maps/user_area.h5")
```

### Using precomputed data and building visibility graph


```python
from offroad_routing.visibility.visibility_graph import VisibilityGraph

vgraph = VisibilityGraph()
vgraph.load_geometry("../maps/user_area.h5")
```

Visibility graph can be built and (optionally) saved as networkx graph and (optionally) visualised using mplleaflet:


```python
%%time
import mplleaflet

G, fig = vgraph.build_graph(inside_percent=0,
                            multiprocessing=False,
                            graph=True,
                            map_plot=True)

print('edges: ', G.number_of_edges())
print('nodes: ', G.number_of_nodes())
mplleaflet.display(fig=fig)
```

<img src="docs/VGraph.png" alt="" width="800"/>


VisibilityGraph may also be used to find incident edges for a single point.  
This feature is used for pathfinding without graph building:


```python
import matplotlib.pyplot as plt
import mplleaflet

start = ((34.02, 59.01), None, None, None, None)
incidents = vgraph.incident_vertices(start)

fig = plt.figure()
plt.scatter(start[0][0], start[0][1], color='r')
for p in incidents:
    plt.scatter(p[0][0], p[0][1], color='b')
mplleaflet.display(fig=fig)
```

### Building routes


```python
from offroad_routing.visibility.visibility_graph import VisibilityGraph
from offroad_routing.pathfinding.astar import AStar

vgraph = VisibilityGraph()
vgraph.load_geometry("../maps/user_area.h5")

pathfinder = AStar(vgraph)
path = pathfinder.find((34.02, 59.01), (34.12, 59.09), default_weight=10, heuristic_multiplier=10)
```

Path can be viewed in coordinate format:


```python
print(path.path())
```

However, specialized tools can be used to save and visualize the path:

The following code saves the path to a gpx file and generates a link to view it online.


```python
from offroad_routing.pathfinding.gpx_track import GpxTrack

track = GpxTrack(path)
track.write_file("track.gpx")
track.visualize()
```

You can check the route [here](https://nakarte.me/#nktj=W3sibiI6ICIyMDIxLTA5LTE5IiwgInAiOiBbeyJuIjogIlN0YXJ0IiwgImx0IjogNTkuMDEsICJsbiI6IDM0LjAyfSwgeyJuIjogIkdvYWwiLCAibHQiOiA1OS4wOSwgImxuIjogMzQuMTJ9XSwgInQiOiBbW1s1OS4wMSwgMzQuMDJdLCBbNTkuMDA3NzI1NSwgMzQuMDEyMDA2M10sIFs1OS4wMDI3NDk4LCAzNC4wMDY1MTM5XSwgWzU5LjAwMDE5NSwgMzQuMDA4MDM1N10sIFs1OS4wMDE1NTg5LCAzNC4wMzA4NDMyXSwgWzU5LjAwMDI3ODcsIDM0LjA0MTcxOV0sIFs1OS4wMDAzNzc2LCAzNC4wNDk3MTU2XSwgWzU5LjAwNjc2NDEsIDM0LjA2MzMzNjFdLCBbNTkuMDA5NzI2MywgMzQuMDY0NTAxMl0sIFs1OS4wMTExMDE4LCAzNC4wNzA5MjAzXSwgWzU5LjAxOTExNjcsIDM0LjA5Nzk1NzZdLCBbNTkuMDE4MjgyOCwgMzQuMTA1MTg4OF0sIFs1OS4wMjM0ODk5LCAzNC4xMTgxNjY5XSwgWzU5LjA0ODE3MDMsIDM0LjE0Mzg1NjldLCBbNTkuMDcwNjk4NSwgMzQuMTQzMDg0NF0sIFs1OS4wNzc1NDY3LCAzNC4xMzM4NzkxXSwgWzU5LjA4MjI2OTEsIDM0LjExNDU5MjRdLCBbNTkuMDg2NDQxNiwgMzQuMTIxNDY4M10sIFs1OS4wOSwgMzQuMTJdXV19XQ==).
    

### Results
Check out the [graph vizualization](https://denikozub.github.io/Offroad-routing-engine/) provided by mplleaflet.  
Computational time for an extremely dense area of 800 km<sup>2</sup> is about 20 seconds with multiprocessing.  
Computational time for a much freer area or 120 km<sup>2</sup> is 1 second.  
Since A* pathfinding does not require building the whole graph, computational time is even lower:
The last example (see above) took only 0.6 seconds, which is 40% faster than building a graph.
