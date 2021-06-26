from shapely.geometry import mapping, MultiLineString
from math import fabs
from rdp import rdp


def get_coordinates(obj, epsilon, bbox_comp, bbox_size, obj_type):
    """
    transform shapely.geometry.Polygon or shapely.geometry.MultiLineString to tuple of points
    get rid of small polygons and linestrings and run Ramer-Douglas-Peucker
    :param obj: shapely.geometry.Polygon or shapely.geometry.MultiLineString
    :param epsilon: None or Ramer-Douglas-Peucker algorithm parameter
    :param bbox_comp: None or int or float - scale object comparison parameter (to size of map bbox)
    :param bbox_size: None or tuple of lon, lat size of map bbox
    :param obj_type: 0 - Polygon, 1 - Linestring, 2 - MultiLineString
    :return: None if object did not pass bbox comparison
             tuple of points of object if epsilon is None or epsilon == 0
             tuple of points of object estimated by Ramer-Douglas-Peucker else
    """

    for param in {epsilon, bbox_comp}:
        if param is not None:

            if type(param) not in {float, int}:
                raise TypeError("wrong ", str(param), " type")

            if param < 0:
                raise ValueError("wrong ", str(param), " value")

    iter(bbox_size)

    if type(obj_type) != int:
        raise TypeError("wrong obj_type type")
    
    if obj_type < 0 or obj_type > 2:
        raise ValueError("wrong obj_type value")

    # getting polygon bbox with shapely
    if bbox_comp is not None:
        bounds = obj.bounds
        bounds_size = (fabs(bounds[2] - bounds[0]), fabs(bounds[3] - bounds[1]))

        if bounds_size[0] == 0 or bounds_size[1] == 0:
            return None

        # comparing object sizes
        if bbox_size[0] / bounds_size[0] >= bbox_comp and bbox_size[1] / bounds_size[1] >= bbox_comp:
            return None

    # extracting coordinates from geopandas.GeoDataFrame
    if obj_type == 0:
        coordinates = mapping(obj)['coordinates']
        if type(obj) == MultiLineString:
            coordinates = list(coordinates)
            coordinates.append(coordinates[0])
            return tuple([tuple(point) for point in coordinates]) if epsilon is None or epsilon == 0 else \
                tuple([tuple(point) for point in rdp(coordinates, epsilon=epsilon)])
        polygons = list()
        for polygon in coordinates:
            polygons.append(tuple([tuple(point) for point in polygon]) if epsilon is None or epsilon == 0 else \
                tuple([tuple(point) for point in rdp(polygon, epsilon=epsilon)]))
        return tuple(polygons)
    elif obj_type == 1:
        return mapping(obj)['coordinates']
    else:
        coordinates = mapping(obj)['coordinates']
        points = [pair[0] for pair in coordinates]
        points.append(coordinates[-1][1])
    return tuple([tuple(point) for point in points]) if epsilon is None or epsilon == 0 else \
        tuple([tuple(point) for point in rdp(points, epsilon=epsilon)])

