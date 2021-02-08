from pyrosm import OSM
from shapely.geometry import mapping, MultiPolygon, Polygon
from geometry import mod, vec
import pandas as pd
import numpy as np
import rdp


class OsmParser:

    def __init__(self, filename, bbox):
        osm = OSM(filename, bounding_box=bbox)
        natural = osm.get_natural(extra_attributes=['nodes'])  # Additional attributes: natural.tags.unique()
        self.polygons = natural.loc[:, ['natural', 'geometry']].loc[natural.geometry.type == 'Polygon']
        self.multipolygons = natural.loc[:, ['natural', 'geometry']].loc[natural.geometry.type == 'MultiPolygon']
        self.multilinestrings = natural.loc[:, ['natural', 'geometry']].loc[natural.geometry.type == 'MultiLineString']
        self.bbox = bbox

    def check_bounds(self, obj, bbox_comp):
        bounds = obj.bounds
        return (self.bbox[2] - self.bbox[0]) / (bounds[2] - bounds[0]) <= bbox_comp and \
               (self.bbox[3] - self.bbox[1]) / (bounds[3] - bounds[1]) <= bbox_comp

    def get_coord(self, obj, epsilon, bbox_comp):
        if bbox_comp is not None and not self.check_bounds(obj, bbox_comp):
            return None
        if epsilon is None or epsilon == 0:
            return np.array(mapping(obj)['coordinates'][0])
        return rdp.rdp(np.array(mapping(obj)['coordinates'][0]), epsilon=epsilon)

    @staticmethod
    def get_centroid(polygon):
        return Polygon(polygon).centroid

    def build_dataframe(self, epsilon, bbox_comp):
        self.polygons.geometry = self.polygons.geometry.convex_hull  # check for efficiency and rewrite if needed
        polygons = pd.DataFrame(self.polygons)
        polygons.geometry = polygons.geometry.apply(self.get_coord, args=[epsilon, bbox_comp])
        polygons = polygons.reset_index().rename(columns={'geometry': 'coords'}).drop(columns='index')

        multipolygons = pd.DataFrame(self.multipolygons)
        for i in range(multipolygons.shape[0]):
            multi_natural = multipolygons.natural.iloc[i]
            for polygon in MultiPolygon(multipolygons.geometry.iloc[i]).geoms:
                convex_polygon = polygon.convex_hull  # check for efficiency and rewrite if needed
                polygons = polygons.append({'coords': self.get_coord(convex_polygon, epsilon, bbox_comp),
                                            'natural': multi_natural}, ignore_index=True)

        multilinestrings = pd.DataFrame(self.multilinestrings)
        multilinestrings.geometry = multilinestrings.geometry.apply(self.get_coord, args=[epsilon, bbox_comp])
        multilinestrings = multilinestrings.reset_index().rename(columns={'geometry': 'coords'}).drop(columns='index')
        for i in range(multilinestrings.shape[0]):
            line_coords = multilinestrings.coords[i]
            if line_coords is None:
                continue
            point1 = line_coords[0]
            new_line = list()
            new_line.append(point1)
            for j in range(len(line_coords) - 1):
                point2 = line_coords[j + 1]
                if mod(vec(point1, point2)) < min(self.bbox[2] - self.bbox[0], self.bbox[3] - self.bbox[1]) / bbox_comp:
                    continue
                new_line.append(point2)
                point1 = point2
            multilinestrings.coords[i] = new_line

        return polygons, multilinestrings
