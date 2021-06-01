import shapely.geometry
from rdp import rdp
from scipy.spatial import ConvexHull
from geometry.algorithm import angle


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

    def ch(self):

        # polygon is a segment
        if self.size() == 2:
            return self, [i for i in range(self.size())], None

        # polygon is a triangle
        if self.size() == 3:
            starting_point = self[0]
            angles = [angle(starting_point, vertice) for vertice in self]
            angles.pop(0)
            angles.pop()
            return self, [i for i in range(self.size())], angles

        # getting convex hull with scipy
        ch = ConvexHull(self.exterior.coords)
        points = list(ch.vertices)
        points.append(points[0])
        vertices = Polygon(ch.points[points])
        points.pop()

        # calculating angles for O(n log n) algorithm
        starting_point = vertices[0]
        angles = [angle(starting_point, vertice) for vertice in vertices]
        angles.pop(0)
        angles.pop()
        return vertices, points, angles

