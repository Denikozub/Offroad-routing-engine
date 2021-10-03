# Off-road Navigation System
[__Installation__](https://denikozub.github.io/Offroad-routing-engine/#installation)  
[__Documentation__](https://denikozub.github.io/Offroad-routing-engine/#documentation)  
[__Usage__](https://github.com/Denikozub/Offroad-routing-engine#usage)
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


# Usage

[ipynb notebook](https://github.com/Denikozub/Offroad-routing-engine/blob/main/docs/usage.ipynb)


### Downloading and processing data

There are two ways you can obtain OSM data in osm.pbf format:  
- Download it yourself: [parts of the world](https://download.geofabrik.de/), [cities](https://download.bbbike.org/osm/bbbike/), [adjustable area](https://extract.bbbike.org/) (via mail), [adjustable area](https://export.hotosm.org/en/v3/) (online), [planet](https://planet.maps.mail.ru/pbf/)
- Let the program download it for you

If the map is downloaded, you can specify the filename and parse it:


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

Parsed data can be pruned with chosen or default parameters.
If not specified, optimal parameters will be computed by the algorithm.

```python
vgraph.prune_geometry(epsilon_polygon=0.003,
                      epsilon_polyline=0.001,
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

Visibility graph can be built and visualized using osmnx:


```python
import osmnx as ox

G = vgraph.build_graph(inside_percent=0, multiprocessing=False)
ox.plot_graph(G)
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

Computational time for an extremely dense area of 800 km<sup>2</sup> is about 20 seconds with multiprocessing.  
Computational time for a much freer area or 120 km<sup>2</sup> is 1 second.  
Since A* pathfinding does not require building the whole graph, computational time is even lower:
The last example (see above) took only 0.6 seconds, which is 40% faster than building a graph.
