from shapely.geometry import mapping
from math import fabs
from rdp import rdp


def get_coord_polygon(polygon, epsilon, bbox_comp, bbox_size):
    """
    transform shapely.geometry.Polygon to tuple of points, get rid of small polygons and run Ramer-Douglas-Peucker
    :param polygon: shapely.geometry.Polygon
    :param epsilon: None or Ramer-Douglas-Peucker algorithm parameter
    :param bbox_comp: None or int or float - scale polygon comparison parameter (to size of map bbox)
    :param bbox_size: None or tuple of lon, lat size of map bbox
    :return: None if polygon did not pass bbox comparison
             tuple of points of polygon if epsilon is None or epsilon == 0
             tuple of points of polygon estimated by Ramer-Douglas-Peucker else
    """

    for param in {epsilon, bbox_comp}:
        if param is not None:

            if type(param) not in {float, int}:
                raise TypeError("wrong ", str(param), " type")

            if param < 0:
                raise ValueError("wrong ", str(param), " value")

    iter(bbox_size)

    # getting polygon bbox with shapely
    if bbox_comp is not None:
        bounds = polygon.bounds
        bounds_size = (fabs(bounds[2] - bounds[0]), fabs(bounds[3] - bounds[1]))

        if bounds_size[0] == 0 or bounds_size[1] == 0:
            return None

        # comparing object sizes
        if bbox_size[0] / bounds_size[0] >= bbox_comp and bbox_size[1] / bounds_size[1] >= bbox_comp:
            return None

    # extracting coordinates from geopandas.GeoDataFrame
    coordinates = mapping(polygon)['coordinates'][0]
    return tuple([tuple(point) for point in coordinates]) if epsilon is None or epsilon == 0 else \
        tuple([tuple(point) for point in rdp(coordinates, epsilon=epsilon)])


def get_coord_linestring(linestring, epsilon):
    """
    transform shapely.geometry.MultiLineString to tuple of points and run Ramer-Douglas-Peucker
    :param linestring: shapely.geometry.MultiLineString
    :param epsilon: None or Ramer-Douglas-Peucker algorithm parameter
    :return: tuple of points of linestring if epsilon is None or epsilon == 0
             tuple of points of linestring estimated by Ramer-Douglas-Peucker else
    """

    if epsilon is not None:

        if type(epsilon) not in {float, int}:
            raise TypeError("wrong epsilon type")

        if epsilon < 0:
            raise ValueError("wrong epsilon value")

    # extracting coordinates from geopandas.GeoDataFrame
    coordinates = mapping(linestring)['coordinates']
    points = [pair[0] for pair in coordinates]
    points.append(coordinates[-1][1])
    coordinates = points
    return tuple([tuple(point) for point in coordinates]) if epsilon is None or epsilon == 0 else \
        tuple([tuple(point) for point in rdp(coordinates, epsilon=epsilon)])
