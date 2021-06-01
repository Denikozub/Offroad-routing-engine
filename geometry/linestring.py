import shapely.geometry
from rdp import rdp


class MultiLineString:

    def __init__(self, src):

        if type(src) == shapely.geometry.multilinestring.MultiLineString:
            coordinates = shapely.geometry.mapping(src)['coordinates']
            points = [pair[0] for pair in coordinates]
            points.append(coordinates[-1][1])
            self.coordinates = points
        else:
            self.coordinates = src

    def __getitem__(self, key):
        return shapely.geometry.Point(self.coordinates[key])

    def size(self):
        return len(self.coordinates)

    def rdp(self, epsilon):
        return MultiLineString(rdp(self.coordinates, epsilon=epsilon))

