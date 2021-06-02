from scipy.spatial import ConvexHull
from geometry.algorithm import angle


def convex_hull(polygon):
    """
    builds a convex hull of a polygon
    :param polygon: iterable of points (polygon[0] == polygon[-1])
    :return: tuple of 3 elements:
        tuple of convex hull points
        tuple of their indexes in initial polygon
        tuple of polar angles from first point to others or None if polygon is a segment or a point
    """

    iter(polygon)

    polygon_size = len(polygon) - 1

    # polygon is a segment or a point
    if polygon_size <= 2:
        return polygon, [i for i in range(len(polygon) - 1)], None

    # polygon is a triangle
    if polygon_size == 3:
        starting_point = polygon[0]
        angles = [angle(starting_point, vertex) for vertex in polygon]
        angles.pop(0)
        angles.pop()
        return polygon, tuple([i for i in range(len(polygon) - 1)]), tuple(angles)

    # getting convex hull with scipy
    ch = ConvexHull(polygon)
    points = list(ch.vertices)
    points.append(points[0])
    vertices = ch.points[points]
    vertices = tuple([tuple(point) for point in vertices])
    points.pop()

    # calculating angles for O(n log n) algorithm
    starting_point = vertices[0]
    angles = [angle(starting_point, vertex) for vertex in vertices]
    angles.pop(0)
    angles.pop()
    return vertices, tuple(points), tuple(angles)