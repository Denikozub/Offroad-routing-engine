"""
This is an attempt to approximate a polygon with an ellipse
prune_geometry() method is changed to store coordinates of a bbox instead of a convex hull if parameter ellipse=True
This requires usage of a specialized function find_pair_ellipse() to find a pair of supporting lines
find_pair_ellipse() finds it in O(1) time, which allows to speed up the algorithm
Current implementation does not work properly
"""


def __compare_bounds(self, bounds, bbox_comp):
    return bbox_comp is None or self.bbox_size[0] / fabs(bounds[2] - bounds[0]) <= bbox_comp and \
        self.bbox_size[1] / fabs(bounds[3] - bounds[1]) <= bbox_comp

def __check_bounds(self, obj, bbox_comp, is_polygon):
    bounds = Polygon(obj).bounds if is_polygon else MultiLineString(obj).bounds
    return self.__compare_bounds(bounds, bbox_comp)

def __get_bounds(self, polygon, bbox_comp):
    bounds = polygon.bounds
    if not self.__compare_bounds(bounds, bbox_comp):
        return None
    min_x, min_y, max_x, max_y = bounds
    return (min_x, min_y), (min_x, max_y), (max_x, max_y), (max_x, min_y), (min_x, min_y)

def __get_coord(self, obj, epsilon, bbox_comp, is_polygon):
    if not self.__check_bounds(obj, bbox_comp, is_polygon):
        return None
    coordinates = array(mapping(obj)['coordinates'][0])
    return coordinates if epsilon is None or epsilon <= 0 else rdp.rdp(coordinates, epsilon=epsilon)

@staticmethod
def __convex_hull(polygon_df, keep=False):
    polygon = polygon_df[0]
    if keep or len(polygon) <= 4:
        return polygon, [i for i in range(len(polygon))]
    ch = ConvexHull(polygon)
    points = list(ch.vertices)
    points.append(points[0])
    vertices = ch.points[points]
    return vertices, points

def build_dataframe (self, epsilon=None, bbox_comp=None, length_comp=None, ellipse=False):
if ellipse:
    self.polygons.geometry = self.polygons.geometry.apply(self.__get_bounds, args=[bbox_comp])
else:
    self.polygons.geometry = self.polygons.geometry.apply(self.__get_coord, args=[epsilon, bbox_comp, True])

for i in range(self.multipolygons.shape[0]):
    natural = self.multipolygons.natural.iloc[i]
    for polygon in MultiPolygon(self.multipolygons.geometry.iloc[i]).geoms:
        if ellipse:
            self.polygons = self.polygons.append({'geometry': self.__get_bounds(polygon, bbox_comp),
                                                  'natural': natural}, ignore_index=True)
        else:
            self.polygons = self.polygons.append({'geometry': self.__get_coord(polygon, epsilon, bbox_comp, True),
                                                  'natural': natural}, ignore_index=True)
self.multipolygons = self.multipolygons.iloc[0:0]
self.polygons = self.polygons[self.polygons['geometry'].notna()]
self.polygons = self.polygons.reset_index().drop(columns='index')
self.polygons = self.polygons.join(pd.DataFrame(self.polygons.geometry).apply(self.__convex_hull, axis=1,
        args=[ellipse], result_type='expand').rename(columns={0: 'convex_hull', 1: 'convex_hull_points'}))

self.multilinestrings.geometry = self.multilinestrings.geometry.apply(self.__get_coord, args=[epsilon, bbox_comp, False])
self.multilinestrings = self.multilinestrings[self.multilinestrings['geometry'].notna()]
self.multilinestrings = self.multilinestrings.reset_index().drop(columns='index')

# length_comp length between linestring points comparison
if length_comp is None:
    return
for i in range(self.multilinestrings.shape[0]):
    line_geometry = self.multilinestrings.geometry[i]
    point1 = line_geometry[0]
    new_line = list()
    new_line.append(point1)
    for j in range(len(line_geometry) - 1):
        point2 = line_geometry[j + 1]
        if ((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)**0.5 < min(self.bbox_size[0], self.bbox_size[1]) / length_comp:
            continue
        new_line.append(point2)
        point1 = point2
    self.multilinestrings.geometry[i] = new_line

def find_pair_ellipse(point, polygon, polygon_number=None):
    multipl = 10000000
    a, b = (polygon[2][0] - polygon[1][0]) / 2 * multipl, (polygon[1][1] - polygon[0][1]) / 2 * multipl
    xc, yc = (polygon[2][0] + polygon[1][0]) / 2 * multipl, (polygon[1][1] + polygon[0][1]) / 2 * multipl
    x0, y0 = point[0] * multipl - xc, point[1] * multipl - yc
    y = quad_equation(b**2 + y0**2 * a**2 / x0**2, -2 * y0 * b**2 * a**2 / x0**2, -b**4 + a**2 * b**2 / x0**2)
    if y is None:
        return None
    x1, x2 = (1 - y0 * y[0] / b**2) * a**2 / x0, (1 - y0 * y[1] / b**2) * a**2 / x0
    point1, point2 = ((x1 + xc) / multipl, (y[0] + yc) / multipl), ((x2 + xc) / multipl, (y[1] + yc) / multipl)
    random.seed(1)
    return (point1, polygon_number, random.randint(5000, 9999), True, 0), (point2, polygon_number, random.randint(5000, 9999), True, 0)

