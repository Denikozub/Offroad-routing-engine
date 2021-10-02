Offroad Routing Engine
======================


Installation
------------

Install from repository::

	pip install "git+https://github.com/Denikozub/Offroad-routing-engine.git#egg=offroad_routing"

Warning: package requires GeoPandas to be installed, which can be problematic on Windows. `This <https://towardsdatascience.com/geopandas-installation-the-easy-way-for-windows-31a666b3610f/>`_ article may help.


VisibilityGraph
---------------

.. autoclass:: offroad_routing.visibility.visibility_graph.VisibilityGraph

	.. automethod:: offroad_routing.visibility.visibility_graph.VisibilityGraph.compute_geometry
	.. automethod:: offroad_routing.visibility.visibility_graph.VisibilityGraph.prune_geometry
	.. automethod:: offroad_routing.visibility.visibility_graph.VisibilityGraph.save_geometry
	.. automethod:: offroad_routing.visibility.visibility_graph.VisibilityGraph.load_geometry
	.. automethod:: offroad_routing.visibility.visibility_graph.VisibilityGraph.incident_vertices
	
	`PointData Explanation`_
	
	.. automethod:: offroad_routing.visibility.visibility_graph.VisibilityGraph.build_graph


AStar
-----

.. autoclass:: offroad_routing.pathfinding.astar.AStar
	:members:
	:special-members: __init__


GpxTrack
--------

.. autoclass:: offroad_routing.pathfinding.gpx_track.GpxTrack
	:members:
	:special-members: __init__


Usage
-----

Check usage example on `GitHub <https://github.com/Denikozub/Offroad-routing-engine#usage/>`_ or in `IPython notebook <https://github.com/Denikozub/Offroad-routing-engine/blob/main/docs/usage.ipynb/>`_.


PointData Explanation
---------------------

In order to speed up computation, low-level data transfer approach is used.  
Data about points, polylines and polygons is transferred using tuples instead of structures.

.. autodata:: offroad_routing.visibility.visibility_graph.TPoint
.. autodata:: offroad_routing.visibility.visibility_graph.PointData


.. toctree::
   :maxdepth: 2
   :caption: Contents:



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
