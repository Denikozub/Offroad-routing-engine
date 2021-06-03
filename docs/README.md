# VisibilityGraph
Denis denikozub Kozub

Class for building a visibility graph on a given area from OSM data  

~~~
compute_geometry(self, filename, bbox)
~~~
parse OSM file area in bbox to retrieve information about roads and surface  
__filename__: .osm.pbf format  
__bbox__: None of in format min_lon, min_lat, max_lon, max_lat  
__return__ None  

~~~
build_dataframe(self, epsilon_polygon, epsilon_linestring, bbox_comp)
~~~
transform retrieved data:
* transform geometry to tuple of points
* run Ramer-Douglas-Peucker to geometry
* get rid of small polygons with bbox_comp parameter
* add data about convex hull for polygons  

__epsilon_polygon__: None or Ramer-Douglas-Peucker algorithm parameter for polygons  
__epsilon_linestring__: None or Ramer-Douglas-Peucker algorithm parameter for linestrings  
__bbox_comp__: bbox_comp: None or int or float - scale polygon comparison parameter (to size of map bbox)  
__return__ None  

~~~
incident_vertices(self, point_data, inside_percent=1)
~~~
finds all incident vertices in visibility graph for given point  
__point_data__: _point_data_ of given point  
__inside_percent__: float parameter setting the probability of an inner edge to be added (from 0 to 1)  
__return__ list of point_data of all visible points  
_point_data_ is a tuple where:  
* 0 element: point coordinates - tuple of x, y
* 1 element: number of object where point belongs
* 2 element: number of point in object
* 3 element: if object is polygon (1) or linestring (0)
* 4 element: surface type (0 - edge between objects, 1 - edge inside polygon, 2 - road edge)


~~~
build_graph(self, inside_percent=1, graph=False, map_plot=None, crs='EPSG:4326')
~~~
compute [and build] [and plot] visibility graph
__inside_percent__: float parameter setting the probability of an inner edge to be added (from 0 to 1)  
__graph__: bool parameter indicating whether to build a networkx graph  
__map_plot__: None or iterable of 2 elements: colors to plot visibility graph
* 0 element: color to plot polygons  
* 1 element: dict of 3 elements: colors to plot edges  
    * 0: edges between objects
    * 1: edges inside polygon
    * 2: road edges  

__crs__: string parameter: coordinate reference system  
__return__ None
