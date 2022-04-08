from typing import NewType
from typing import Tuple

TPoint = NewType('TPoint', Tuple[float, float])
TPolygon = NewType('TPolygon', Tuple[TPoint, ...])
