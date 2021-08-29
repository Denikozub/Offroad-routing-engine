from math import fabs
from typing import Union, Optional, Tuple, TypeVar

from rdp import rdp
from shapely.geometry import mapping, Polygon, MultiLineString

from geometry.algorithms import turn

TPoint = TypeVar("TPoint")  # Tuple[float, float]
TPolygon = TypeVar("TPolygon")  # Sequence[TPoint]


def get_coordinates(obj: Union[Polygon, MultiLineString], epsilon: float, bbox_comp: Optional[int],
                    bbox_size: Tuple[float, float], is_polygon: bool) \
        -> Union[Tuple[TPoint, ...], Tuple[TPolygon, ...], None]:
    """
    Transform shapely.geometry.Polygon or shapely.geometry.MultiLineString to tuple of points.
    Get rid of small polygons and linestrings and run Ramer-Douglas-Peucker.

    :param epsilon: Ramer-Douglas-Peucker algorithm parameter
    :param bbox_comp: scale object comparison parameter (to size of map bbox)
    :param bbox_size: lon, lat difference of map bbox
    :param is_polygon: object type is Polygon (True) or MultiLineString (False)
    :return: None if object did not pass bbox comparison,
             tuple of points of object if epsilon is None or epsilon == 0,
             tuple of points of object estimated by Ramer-Douglas-Peucker else
    """

    assert epsilon >= 0
    assert bbox_comp is None or bbox_comp >= 0

    if bbox_comp is not None:
        bounds = obj.bounds
        bounds_size = (fabs(bounds[2] - bounds[0]), fabs(bounds[3] - bounds[1]))

        if bounds_size[0] == 0 or bounds_size[1] == 0:
            return None

        if bbox_size[0] / bounds_size[0] >= bbox_comp and bbox_size[1] / bounds_size[1] >= bbox_comp:
            return None

    # extracting coordinates from geopandas.GeoDataFrame
    if is_polygon:
        coordinates = mapping(obj)['coordinates']
        polygons = list()
        for polygon in coordinates:
            new_polygon = [tuple(point) for point in polygon] if epsilon is None or epsilon == 0 else \
                    [tuple(point) for point in rdp(polygon, epsilon=epsilon)]

            # counter-clockwise polygons
            if len(new_polygon) >= 3 and turn(polygon[0], polygon[1], polygon[2]) < 0:
                new_polygon.reverse()
            polygons.append(tuple(new_polygon))
        return tuple(polygons)
    else:
        coordinates = mapping(obj)['coordinates']
        points = [pair[0] for pair in coordinates]
        points.append(coordinates[-1][1])
        coordinates = points
    return tuple([tuple(point) for point in coordinates]) if epsilon is None or epsilon == 0 else \
        tuple([tuple(point) for point in rdp(coordinates, epsilon=epsilon)])
