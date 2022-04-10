Offroad Routing Engine
**********************

This module is made for downloading, parsing and processing OSM maps, pathfinding and visibility graph building using hierarchical approach, saving and visualizing results.
Main goal was to fully optimize geometry algorithms and achieve lowest computational time possible. Low-level data transfer approach has been used and
a unique algorithm, created specifically for off-road routing, has been implemented. See `algorithm explanation <https://github.com/Denikozub/Offroad-routing-engine/blob/main/docs/algorithm.pdf>`_.

.. figure::  ../docs/map.png
   :align:   center


Installation
============

Install from repository::

	pip install -e "git+https://github.com/Denikozub/Offroad-routing-engine.git#egg=offroad_routing"

It is recommended to install packages using conda. Pip warning: package requires GeoPandas to be installed, which can be problematic on Windows. `This <https://towardsdatascience.com/geopandas-installation-the-easy-way-for-windows-31a666b3610f/>`_ article may help.
Dependency warning: you may additionally need to pip install cykhash==1.0.2, rtree and reinstall pyproj with pip.


Usage
=====

You can follow by running the code in `IPython notebook <https://github.com/Denikozub/Offroad-routing-engine/blob/main/docs/usage.ipynb>`_.


Processing and pruning data
+++++++++++++++++++++++++++

More information available at `Geometry`_ documentation.

There are several ways to obtain OSM data:

- specify .xml (.osm) file to be parsed
- specify .osm.pbf file to be parsed (resources: `parts of the world <https://download.geofabrik.de/>`_, `cities <https://download.bbbike.org/osm/bbbike/>`_, `adjustable area <https://extract.bbbike.org/>`_ (via mail), `adjustable area <https://export.hotosm.org/en/v3/>`_ (online), `planet <https://planet.maps.mail.ru/pbf/>`_)
- specify bounding box for map data to be dowloaded and parsed
- specify `region / city / country <https://pyrosm.readthedocs.io/en/latest/basics.html#protobuf-file-what-is-it-and-how-to-get-one>`_ query for map data to be downloaded and parsed

::

	import warnings
	warnings.filterwarnings("ignore")

::

	from offroad_routing import Geometry

	filename = "../maps/user_area.osm.pbf"
	bbox = [34, 59, 34.2, 59.1]
	geom = Geometry.parse(filename=filename, bbox=bbox)

Geometry data can be explored and visualized using folium, which allows multiple maps to be combined in one layer::

	print(geom.stats)
	geom.plot()

Geometry can be cut to a bounding box, if needed::

	geom.cut_bbox([34.01, 59.01, 34.19, 59.09])

Road network geometry can be simplified and visualized separately. Available options:

- remove small edges using edge contraction
- build minimum spanning tree
- select specific road surface types

::

	geom.select_road_type({'path'}, exclude=True, inplace=True)
	geom.minimum_spanning_tree(inplace=True)
	geom.simplify_roads(200, inplace=True)
	geom.plot('roads')

Polygon geometry can also be simplified and visualized separately, small polygons will be removed::

	geom.simplify_polygons(15, inplace=True)
	geom.plot('polygons')

Geometry can be saved to file and loaded afterwards using Geometry.load()::

	geom.save('new_map', '../maps')


Building visibility graph
+++++++++++++++++++++++++

More information available at `VisibilityGraph`_ documentation.

VisibilityGraph uses special geometry representation for maximum speed, so processed geometry needs to be exported::

	from offroad_routing import VisibilityGraph

	geom = Geometry.load('user_area', '../maps')
	vgraph = VisibilityGraph(*geom.export())

Even though vgraph can be used to find routes without pre-building whole graph,
visibility graph can be fully built and saved to memory for further use::

	vgraph.build(inside_percent=1, multiprocessing=False)
	print(vgraph.stats)

Visibility graph can also be visualised using folium::

	vgraph.plot()

Pre-built graph can be exported to networkx.MultiGraph and used for further analysis::

	import osmnx as ox

	G = vgraph.graph
	ox.plot_graph(G)


Pathfinding and visualization
+++++++++++++++++++++++++++++

More information available at `AStar`_ documentation.

If vgraph.build() had been run, pre-built graph is used for pathfinding.
Otherwise, incident vertices are computed at runtime, which allows to explore less graph nodes (in combination with A*)::

	from offroad_routing import VisibilityGraph, AStar

	pathfinder = AStar(vgraph)
	path = pathfinder.find((34.02, 59.01), (34.12, 59.09), heuristic_multiplier=10)

Path can be viewed in coordinate format::

	print(path.path())

More information available at `GpxTrack`_ documentation.

However, specialized tools can be used to save and visualize the path.
The following code saves the path to a gpx file and generates a link to view it online::

	from offroad_routing import GpxTrack

	track = GpxTrack(path)
	track.write_file("track.gpx")
	track.visualize()

You can check the route `here <https://nakarte.me/#nktj=W3sibiI6ICIyMDIxLTA5LTE5IiwgInAiOiBbeyJuIjogIlN0YXJ0IiwgImx0IjogNTkuMDEsICJsbiI6IDM0LjAyfSwgeyJuIjogIkdvYWwiLCAibHQiOiA1OS4wOSwgImxuIjogMzQuMTJ9XSwgInQiOiBbW1s1OS4wMSwgMzQuMDJdLCBbNTkuMDA3NzI1NSwgMzQuMDEyMDA2M10sIFs1OS4wMDI3NDk4LCAzNC4wMDY1MTM5XSwgWzU5LjAwMDE5NSwgMzQuMDA4MDM1N10sIFs1OS4wMDE1NTg5LCAzNC4wMzA4NDMyXSwgWzU5LjAwMDI3ODcsIDM0LjA0MTcxOV0sIFs1OS4wMDAzNzc2LCAzNC4wNDk3MTU2XSwgWzU5LjAwNjc2NDEsIDM0LjA2MzMzNjFdLCBbNTkuMDA5NzI2MywgMzQuMDY0NTAxMl0sIFs1OS4wMTExMDE4LCAzNC4wNzA5MjAzXSwgWzU5LjAxOTExNjcsIDM0LjA5Nzk1NzZdLCBbNTkuMDE4MjgyOCwgMzQuMTA1MTg4OF0sIFs1OS4wMjM0ODk5LCAzNC4xMTgxNjY5XSwgWzU5LjA0ODE3MDMsIDM0LjE0Mzg1NjldLCBbNTkuMDcwNjk4NSwgMzQuMTQzMDg0NF0sIFs1OS4wNzc1NDY3LCAzNC4xMzM4NzkxXSwgWzU5LjA4MjI2OTEsIDM0LjExNDU5MjRdLCBbNTkuMDg2NDQxNiwgMzQuMTIxNDY4M10sIFs1OS4wOSwgMzQuMTJdXV19XQ==>`_.

Path can also be visualized using folium and combibed with other maps::

	track.plot()


Documentation
=============

Geometry
+++++++++++++++

	`Geometry types`_

.. autoclass:: offroad_routing.Geometry

	.. automethod:: offroad_routing.Geometry.parse
	.. automethod:: offroad_routing.Geometry.load
	.. automethod:: offroad_routing.Geometry.save
	.. automethod:: offroad_routing.Geometry.plot
	.. automethod:: offroad_routing.Geometry.cut_bbox
	.. automethod:: offroad_routing.Geometry.minimum_spanning_tree
	.. automethod:: offroad_routing.Geometry.simplify_roads
	.. automethod:: offroad_routing.Geometry.select_road_type
	.. automethod:: offroad_routing.Geometry.simplify_polygons
	.. automethod:: offroad_routing.Geometry.to_networkx
	.. automethod:: offroad_routing.Geometry.export


VisibilityGraph
+++++++++++++++

	`Geometry types`_

.. autoclass:: offroad_routing.VisibilityGraph

	.. automethod:: offroad_routing.VisibilityGraph.__init__
	.. automethod:: offroad_routing.VisibilityGraph.incident_vertices
	.. automethod:: offroad_routing.VisibilityGraph.build
	.. automethod:: offroad_routing.VisibilityGraph.plot


AStar
+++++

.. autoclass:: offroad_routing.AStar
	:members:
	:special-members: __init__


GpxTrack
++++++++

.. autoclass:: offroad_routing.GpxTrack
	:members:
	:special-members: __init__


Geometry types
+++++++++++++++++++++

In order to speed up computation, low-level data transfer approach is used.
Data about points, polylines and polygons is transferred using tuples instead of structures.

.. autodata:: offroad_routing.geometry.geom_types.TPoint
.. autodata:: offroad_routing.geometry.geom_types.TPolygon
.. autodata:: offroad_routing.geometry.geom_types.TMultiPolygon
.. autodata:: offroad_routing.geometry.geom_types.TSegment
.. autodata:: offroad_routing.geometry.geom_types.TAngles
.. autodata:: offroad_routing.geometry.geom_types.TPath
.. autodata:: offroad_routing.geometry.geom_types.TPolygonData
.. autodata:: offroad_routing.geometry.geom_types.TSegmentData
.. autodata:: offroad_routing.geometry.geom_types.PointData


.. toctree::
   :maxdepth: 2
   :caption: Contents:



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
