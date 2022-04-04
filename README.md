# Off-road Navigation System
[__Installation__](https://denikozub.github.io/Offroad-routing-engine/#installation)  
[__Documentation__](https://denikozub.github.io/Offroad-routing-engine/#documentation)  
[__Usage__](https://denikozub.github.io/Offroad-routing-engine/#usage)  
___
by Denis Kozub
- World discretization using _visibility graphs_
- O(nh log n) _reduced_ visibility graph algorithm (see [algorithm explanation](https://github.com/Denikozub/Offroad-routing-engine/blob/main/docs/algorithm.pdf))
- A* pathfinding without graph precomputing
- _Hierarchical approach_ for graph building
- No projected crs, works in any part of the world
- Open source OpenStreetMap data (see [OSM data explanation](https://github.com/Denikozub/Offroad-routing-engine/blob/main/docs/OSM_data.ipynb))
- OMS maps download at runtime
- Road network graph geometry dissolve
- Saving and loading precomputed map data
- Multiprocessing and visualization tools support

<img src="docs/Route.png" alt="" width="800"/>

Scope of application:
- Extending functionality of other routing engines
- Road and facilities design
- Rescue and military operations planning
- Route planning for hiking and tourism
