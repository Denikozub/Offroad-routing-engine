import json
import xml.etree.ElementTree as ET
from copy import deepcopy
from os import path
from re import findall
from typing import Tuple

import networkx as nx
import numpy as np
import requests
from geopandas import clip
from geopandas import GeoDataFrame
from geopandas import read_file
from offroad_routing.geometry.algorithms import compare_points
from offroad_routing.osm_data.convex_hull import build_convex_hull
from offroad_routing.osm_data.osm_parser import parse_pbf
from offroad_routing.osm_data.osm_parser import parse_xml
from offroad_routing.surface.tag_value import TagValue
from pandas import concat
from pandas import DataFrame
from pandas import merge
from pyrosm import get_data
from shapely.geometry import box
from shapely.geometry import LineString
from shapely.geometry import mapping
from shapely.geometry import Polygon
from shapely.geometry.base import BaseGeometry


class Geometry:
    """
    Class for retrieving, storing and processing OSM geometry data.
    """

    __slots__ = ("polygons", "edges", "nodes", "tag_value")

    def __init__(self):
        self.polygons = self.edges = self.nodes = None
        self.tag_value = TagValue()

    @classmethod
    def load(cls, package_name, directory='.'):
        """
        Load saved geometry from json & geopackage files.

        :param str package_name: saved geometry package name
        :param str directory: saved geometry package directory
        :rtype: Geometry
        """

        geometry = cls()
        filepath = path.join(directory, package_name)
        geometry.polygons = read_file(filepath + ".gpkg", layer='polygons')
        geometry.edges = read_file(filepath + ".gpkg", layer='edges')
        with open(filepath + ".json") as f:
            geometry.nodes = {int(k): tuple(v)
                              for k, v in json.load(f).items()}
        return geometry

    @classmethod
    def parse(cls, *, filename=None, query=None, bbox=None, directory='.'):
        """
        Parse data to get OSM data. Bounding box will always be used if specified.
        Either one of parameters should be set. If filename is not None, query is ignored.

        :param str filename: .osm.pbf or .xml OSM file
        :param str query: dataset available at Geofabrik or BBBike
        :param Optional[Sequence[float]] bbox: area to be parsed in format (min_lon, min_lat, max_lon, max_lat)
        :param str directory: directory for downloaded maps to be saved
        :rtype: Geometry
        """

        if filename is None and query is None and bbox is None:
            raise ValueError("Nothing to parse")
        assert bbox is None or len(bbox) == 4

        geometry = cls()

        if filename is not None:
            if filename[-4:] == '.xml':
                root = ET.parse(filename)
                geometry.polygons, geometry.edges, geometry.nodes = parse_xml(
                    root)
                return geometry.cut_bbox(bbox)
            if filename[-8:] == '.osm.pbf':
                geometry.polygons, geometry.edges, geometry.nodes = parse_pbf(
                    filename, bbox)
                return geometry
            raise ValueError("Only .xml and .osm.pbf files supported")

        if query is not None:
            filepath = get_data(query, directory=directory)
            geometry.polygons, geometry.edges, geometry.nodes = parse_pbf(
                filepath, bbox)
            return geometry

        r = requests.get('http://www.overpass-api.de/api/xapi_meta?*[bbox=' +
                         str(bbox[0]) + ',' + str(bbox[1]) + ',' +
                         str(bbox[2]) + ',' + str(bbox[3]) + ']')
        with open(path.join(directory, str(bbox) + '.xml'), 'w') as f:
            f.write(r.text)
        root = ET.fromstring(r.text)
        geometry.polygons, geometry.edges, geometry.nodes = parse_xml(root)
        return geometry

    def save(self, package_name, directory='.'):
        """
        Save computed geometry to json & geopackage files.

        :param str package_name: name for created files to share
        :param str directory: saved geometry package directory
        """

        if len(findall(r"[#%&{}<>*?/ $!'\":@]", package_name)) > 0:
            raise ValueError("Wrong package name")

        filepath = path.join(directory, package_name)
        self.polygons.to_file(filepath + ".gpkg",
                              layer='polygons', driver="GPKG")
        self.edges.to_file(filepath + ".gpkg",
                           layer='edges', driver="GPKG")
        with open(filepath + ".json", 'w') as f:
            json.dump(self.nodes, f)

    def cut_bbox(self, bbox, *, inplace=False):
        """
        Clip geometry strictly inside bounding box. If bbox is None, nothing is changed.

        :param Optional[Sequence[float]] bbox: bounding box in format (min_lon, min_lat, max_lon, max_lat)
        :param bool inplace: change initial geometry
        :return: None if inplace else new geometry object
        :rtype: Optional[Geometry]
        """

        if bbox is None:
            return None if inplace else deepcopy(self)
        assert len(bbox) == 4

        mask = box(*bbox)
        polygons = clip(self.polygons, mask,
                        keep_geom_type=True).reset_index(drop=True)
        edges = self.edges.iloc[clip(
            self.edges, mask, keep_geom_type=True).index].reset_index(drop=True)
        nodes = {k: v for k, v in self.nodes.items() if k in (
            set(edges.u) | set(edges.v))}

        if not inplace:
            geometry = Geometry()
            geometry.polygons, geometry.edges, geometry.nodes = polygons, edges, nodes
            return geometry

        self.polygons, self.edges, self.nodes = polygons, edges, nodes

    def plot(self, type=None, **kwargs):
        """
        Build folium map of all geometry data.

        :param Optional[str] type: type of geometry to plot: {'polygons', 'roads', None}
        :param kwargs: additional gpd.GeoDataFrame.explore() parameters
        :rtype: folium.folium.Map
        """

        if type not in {'polygons', 'roads', None}:
            raise ValueError("Wrong geometry type")

        if type == 'polygons':
            return self.polygons.explore(**kwargs)
        if type == 'roads':
            return self.edges.explore(**kwargs)
        return concat([self.polygons[['tag', 'geometry']], self.edges[['tag', 'geometry']]]).explore(**kwargs)

    def to_networkx(self):
        """
        Build networkx weighted graph of road network. Weight measured in meters.

        :rtype: nx.Graph
        """

        G = nx.Graph()
        for _, row in self.edges.iterrows():
            G.add_edge(self.nodes[row.u],
                       self.nodes[row.v], weight=row['length'])
        return G

    def minimum_spanning_tree(self, *, inplace=False):
        """
        Build minimum spanning tree of road graph.

        :param bool inplace: change initial geometry
        :return: None if inplace else new geometry object
        :rtype: Optional[Geometry]
        """

        G = nx.Graph()
        for _, row in self.edges.iterrows():
            G.add_edge(row.u, row.v, weight=row['length'])
        mst = DataFrame(nx.minimum_spanning_tree(G).edges, columns=['u', 'v'])
        edges = concat([merge(self.edges, mst, how='inner', left_on=['u', 'v'], right_on=['u', 'v']),
                        merge(self.edges, mst, how='inner', left_on=[
                            'u', 'v'], right_on=['v', 'u'])
                       .drop(columns=['u_x', 'v_x'])
                       .rename(columns={'u_y': 'u', 'v_y': 'v'})]).reset_index(drop=True)

        if not inplace:
            geometry = Geometry()
            geometry.polygons, geometry.edges, geometry.nodes = deepcopy(
                self.polygons), edges, deepcopy(self.nodes)
            return geometry

        self.edges = edges

    def simplify_roads(self, threshold, *, inplace=False):
        """
        Simplify road network by contracting edges shorted than threshold.

        :param float threshold: edge contraction threshold in meters
        :param bool inplace: change initial geometry
        :return: None if inplace else new geometry object
        :rtype: Optional[Geometry]
        """

        assert threshold > 0
        edges, nodes = deepcopy(self.edges), deepcopy(self.nodes)
        for i in edges.index:
            row = edges.loc[i]
            if row.u == row.v:
                edges.drop(i, inplace=True)
            elif row['length'] < threshold:
                edges.u.replace(row.v, row.u, inplace=True)
                edges.v.replace(row.v, row.u, inplace=True)
                edges.drop(i, inplace=True)
                nodes.pop(row.v, None)
        edges.reset_index(drop=True, inplace=True)
        edges.geometry = edges.apply(
            lambda x: LineString((nodes[x.u], nodes[x.v])), axis=1)

        if not inplace:
            geometry = Geometry()
            geometry.polygons, geometry.edges, geometry.nodes = deepcopy(
                self.polygons), edges, nodes
            return geometry

        self.edges, self.nodes = edges, nodes

    def select_road_type(self, types, *, exclude=False, inplace=False):
        """
        Select specific OSM road surface types.

        :param Set[str] types: set of road surface OSM types to leave
        :param bool exclude: exclude specified surface types
        :param bool inplace: change initial geometry
        :return: None if inplace else new geometry object
        :rtype: Optional[Geometry]
        """

        assert isinstance(types, (list, tuple, set))

        if not exclude:
            edges = self.edges[self.edges.tag.isin(
                types)].reset_index(drop=True)
        else:
            edges = self.edges[~self.edges.tag.isin(
                types)].reset_index(drop=True)
        nodes = {k: v for k, v in self.nodes.items() if k in (
            set(edges.u) | set(edges.v))}

        if not inplace:
            geometry = Geometry()
            geometry.polygons, geometry.edges, geometry.nodes = deepcopy(
                self.polygons), edges, nodes
            return geometry

        self.edges, self.nodes = edges, nodes

    @staticmethod
    def __compare_bbox(obj: BaseGeometry, bbox_comp: float, bbox_size: Tuple[float, float]) -> BaseGeometry:
        if bbox_comp is not None:
            bounds = obj.bounds
            bounds_size = (bounds[2] - bounds[0], bounds[3] - bounds[1])
            if bounds_size[0] == 0 or bounds_size[1] == 0:
                return None
            if bbox_size[0] / bounds_size[0] >= bbox_comp and bbox_size[1] / bounds_size[1] >= bbox_comp:
                return None
        return obj

    def simplify_polygons(self, bbox_comp=15, epsilon=None, *, inplace=False):
        """
        Simplify polygons by removing small objects (comparing bbox_comp)
        and running Ramer-Douglas-Peucker (RDP) with epsilon parameter.

        :param float bbox_comp: scale polygon comparison parameter (to size of map bbox)
        :param Optional[float] epsilon: RPD simplification parameter. If None, computed automatically
        :param bool inplace: change initial geometry
        :return: None if inplace else new geometry object
        :rtype: Optional[Geometry]
        """

        assert bbox_comp > 0 and (epsilon is None or epsilon >= 0)
        polygons = deepcopy(self.polygons)

        bounds = polygons.geometry.bounds
        bbox_size = (bounds.maxx.max() - bounds.minx.min(),
                     bounds.maxy.max() - bounds.miny.min())

        if epsilon is None:
            epsilon = (bbox_size[0] ** 2 + bbox_size[1]
                       ** 2) ** 0.5 / bbox_comp / 5

        polygons.geometry = polygons.geometry.apply(
            Geometry.__compare_bbox, args=[bbox_comp, bbox_size])
        polygons = polygons[polygons.geometry.notna()].reset_index(drop=True)
        polygons.geometry = polygons.geometry.simplify(
            epsilon, preserve_topology=True)

        if not inplace:
            geometry = Geometry()
            geometry.polygons, geometry.edges, geometry.nodes = polygons, deepcopy(
                self.edges), deepcopy(self.nodes)
            return geometry

        self.polygons = polygons

    @property
    def stats(self):
        return {
            'number_of_polygons': self.polygons.shape[0],
            'number_of_edges': self.edges.shape[0],
            'number_of_nodes': len(self.nodes),
            'road_length_km': self.edges['length'].sum() / 1000,
            'polygon_tags': set(self.polygons.tag),
            'road_tags': set(self.edges.tag)
        }

    @staticmethod
    def __remove_inner_polygons(polygons: DataFrame):
        polygon_count = polygons.shape[0]
        for i in range(polygon_count):
            polygon = polygons.loc[i, "geometry"]
            for j in range(1, len(polygon)):
                point = polygon[j][0]
                for k in range(i + 1, polygon_count):
                    if polygons.loc[k, "geometry"] is None:
                        if k == polygon_count - 1:
                            polygons.loc[i, "tag"].append(None)
                        continue
                    new_point = polygons.loc[k, "geometry"][0][0]
                    if compare_points(point, new_point):
                        polygons.loc[i, "tag"].append(
                            polygons.loc[k, "tag"])
                        polygons.loc[k, "geometry"] = None
                    elif k == polygon_count - 1:
                        polygons.loc[i, "tag"].append(None)
        polygons.drop(polygons[polygons.geometry.isna()].index, inplace=True)
        polygons.reset_index(drop=True, inplace=True)

    @staticmethod
    def __polygon_coords(polygon: Polygon):
        coordinates = mapping(polygon)['coordinates']
        polygons = list()
        for polygon in coordinates:
            polygons.append(tuple(tuple(point) for point in polygon))
        return tuple(polygons) if len(polygons[0]) >= 3 else None

    @staticmethod
    def __compare_polygon(p1: Polygon, p2: Polygon):
        if p1.exterior == p2.exterior:
            return True
        p1_xy = p1.exterior.coords.xy
        p2_xy = p2.exterior.coords.xy
        return len(p1_xy[0]) == len(p2_xy[0]) and \
            np.all(np.flip(p2_xy[0]) == p1_xy[0]) and \
            np.all(np.flip(p2_xy[1]) == p1_xy[1])

    @staticmethod
    def __remove_equal_polygons(polygons: GeoDataFrame):
        to_delete = list()
        for i, p1 in enumerate(polygons.geometry):
            for j, p2 in enumerate(polygons.geometry):
                if (i != j) and Geometry.__compare_polygon(p1, p2) and (i not in to_delete) and (j not in to_delete):
                    to_delete.append(j)
        polygons.drop(to_delete, inplace=True)
        polygons.reset_index(drop=True, inplace=True)

    def export(self, *, remove_inner=False):
        """
        Export geometry data to polygon and linestring records. Duplicate polygons removed.

        :param bool remove_inner: remove polygons which are inner for other polygons
        :return: polygon and linestring records
        :rtype: Tuple[TPolygonData, TSegmentData]
        """

        polygons = DataFrame(self.polygons[["tag", "geometry"]])
        self.tag_value.eval_polygons(polygons, "tag")
        Geometry.__remove_equal_polygons(polygons)
        polygons['geometry'] = self.polygons.geometry.apply(
            Geometry.__polygon_coords)
        polygons = polygons[polygons['geometry'].notna(
        )].reset_index().drop(columns='index')
        if remove_inner:
            Geometry.__remove_inner_polygons(polygons)
        if polygons.shape[0] > 0:
            polygons = polygons.join(DataFrame(polygons.geometry)
                                     .apply(lambda x: build_convex_hull(x[0][0]), axis=1, result_type='expand')
                                     .rename(columns={0: 'convex_hull', 1: 'convex_hull_points', 2: 'angles'}))

        linestrings = DataFrame(self.edges[["tag"]])
        self.tag_value.eval_lines(linestrings, "tag")
        linestrings['geometry'] = self.edges.apply(
            lambda x: (self.nodes[x.u], self.nodes[x.v]), axis=1)
        return polygons.to_dict('records'), linestrings.to_dict('records')
