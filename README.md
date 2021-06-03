# Off-road navigation system
- O(nh log n) on-line _reduced visibility graph_ algorithm
- A* pathfinding _without_ graph precomputing
- Dynamic edge weights
- Huge database of hiking and country roads
- Super fast pathfinding on large areas
- _Hierarchical approach_ for graph building
- OSM maps data
- No projected crs -> more accuracy and speed
- Minimized stored and precomputed data

This is how Google routing engine (and all others) currently [03.06.2021] work. I am ready to change this.
![](docs/Google_maps.png)

Scope of application:
- Extending functionality of other routing engines  
- Road building  
- Rescue and military operations planning  
- Route planning for hiking and tourism  

May also check [documentation](https://github.com/Denikozub/Routing_engine/tree/main/docs#visibilitygraph), [algorithms](https://github.com/Denikozub/Routing_engine/blob/main/docs/algorithm.pdf) and [usage example](https://github.com/Denikozub/Routing_engine/blob/main/docs/example.ipynb)
