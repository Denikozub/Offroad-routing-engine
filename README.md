# Off-road Navigation & Analysis System
[__Installation__](https://denikozub.github.io/Offroad-routing-engine/#installation)  
[__Documentation__](https://denikozub.github.io/Offroad-routing-engine/#documentation)  
[__Usage__](https://denikozub.github.io/Offroad-routing-engine/#usage)  
___
by Denis Kozub
- World discretization using _visibility graphs_
- O(nh log n) reduced visibility graph algorithm (see [algorithm explanation](https://github.com/Denikozub/Offroad-routing-engine/blob/main/docs/algorithm.pdf))
- A* pathfinding with & without graph precomputing
- _Hierarchical approach_ for road network and natural objects processing
- Open source OpenStreetMap data (see [OSM data explanation](https://github.com/Denikozub/Offroad-routing-engine/blob/main/docs/OSM_data.ipynb))
- Geometry module for map data parsing, processing and saving
- Multiprocessing and visualization tools
- Works in any part of the world

<img src="docs/Route.png" alt="" width="800"/>

Scope of application:
- Extending functionality of other routing engines
- Road and facilities design
- Rescue operations planning
- Route planning for hiking and tourism
