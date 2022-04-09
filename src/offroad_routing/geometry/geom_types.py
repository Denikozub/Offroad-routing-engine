from typing import List
from typing import NewType
from typing import Optional
from typing import Tuple
from typing import TypedDict

TPoint = NewType('TPoint', Tuple[float, float])
TPolygon = NewType('TPolygon', Tuple[TPoint, ...])
TMultiPolygon = NewType('TMultiPolygon', Tuple[TPolygon, ...])
TSegment = NewType('TSegment', Tuple[TPoint, TPoint])
TAngles = NewType('TAngles', Tuple[float, ...])
TPath = NewType('TPath', List[TPoint])


class TPolygonRec(TypedDict):
    tag: List[int]
    geometry: TMultiPolygon
    convex_hull: TPolygon
    convex_hull_points: Tuple[int]
    angles: TAngles


class TSegmentRec(TypedDict):
    tag: List[int]
    geometry: TSegment


TPolygonData = NewType('TPolygonRec', List[TPolygonRec])
TSegmentData = NewType('TSegmentData', List[TSegmentRec])
PointData = NewType(
    'PointData', Tuple[TPoint, Optional[int], Optional[int], Optional[bool], Optional[int]])

"""
0. point coordinates (lon, lat)
1. number of object where point belongs
2. number of point in object
3. object is polygon (True) or polyline (False)
4. surface weight

Node of the graph is unambiguously set either by its coordinates or by its position in an object.
"""
