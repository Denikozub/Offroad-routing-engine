## Iterative algorithm
___
Experimental. Slow (complexity currently not calculated). High precision. Development currently stopped  
Main points:
- We are given point A and point B
- There is a fixed _step length_ that can depend either on map scale or on the route distance (hierarchical approach)
- There is a fixed number of directions on the map. For example, _angle_count_ = 360. This means each step we need to solve a classification task of choosing one of the angles. If a line segment bounding a polygon or forming a line fully lays between two angles (without crossing any of the rays) then distance to the nearest point is taken (currently not finished)
- To solve this task each step a dataframe is build. Class (angle) features:
  - Distance to the nearest surface positive change (surface that is better for moving than the current one) and its type (e.g. road)
  - Distance to the nearest surface negative change and its type (e.g. swamp or river)  
  Currently only polylines are processed. Only points which are not further than the waypoint are added to dataframe
  - Angle between waypoint (0 to 180)
  - Angle between starting point (0 to 180)  
  Working with angles is more reasonable than with distances because step length is fixed and can be small meaning that distances would not differ much
  - Available distance left: available distance (either route planning distance or distance from A to B times constant to allow some looping or a detour) minus distance passed  
  This is used to track a moment to get off the road (prevents riding circles on the road around the waypoint which is in the middle of the forest because it is worse surface)
  - Angle between last step (0 to 180)
  This is used to prevent stepping from foot to foot in front of the river because the algorithm would not want to cross it. Now we would either walk across a bank and then cross it or cross it immediately
- Currently the class only builds first 4 features
- For better accuracy while routing around Moscow [Slazav maps](http://slazav.xyz/maps/) are used. They are made for sports hiking and are much more accurate. Currently only a parser for polylines exists (see parsers/mp_parser)
- GPX tracks database is used for training. A parser (see parsers.gpx_parser) is used to create a dataframe and then (currently not written) calculate all features and a chosen class (from next track point)  

Problems:
- Slazav maps are stored in 6 mb files. In the best case the required bbox is stored in one file. Anyway it still has to be parsed twice (polylines and polygons) for each step. Using OSM maps is an alternative
- Step number should be very high for accurate routing. Processing will take too long, which makes this algorithm unsuitable for users, but I hope to finish it for science purposes  
