import shapely.geometry
from rdp import rdp


class Polygon(shapely.geometry.Polygon):

    def __getitem__(self, key):
        return shapely.geometry.Point(self.exterior.coords[key])

    def size(self):
        size = len(self.exterior.coords) - 1
        return size - 1 if self[-1] == self[-2] else size

    def rdp(self, epsilon):
        return Polygon(rdp(self.exterior.coords, epsilon=epsilon))

    def xy(self):
        return zip(*list(self.exterior.coords))
