import json
import xml.etree.ElementTree as ET
from copy import deepcopy
from os import path
from re import findall

import networkx as nx
import requests
from geopandas import clip
from geopandas import read_file
from offroad_routing.osm_data.osm_parser import parse_pbf
from offroad_routing.osm_data.osm_parser import parse_xml
from offroad_routing.surface.tag_value import TagValue
from pandas import concat
from pandas import DataFrame
from pandas import merge
from pyrosm import get_data
from shapely.geometry import box
from shapely.geometry import LineString


class Geometry:
    tag_value = TagValue()

    def __init__(self):
        self.polygons = self.edges = self.nodes = None

    @classmethod
    def load(cls, package_name, directory='.'):
        """
        Load saved geometry from json & geopackage files.

        :param str package_name: saved geometry package name
        :param str directory: saved geometry package directory
        """

        geometry = cls()
        filepath = path.join(directory, package_name)
        geometry.polygons = read_file(filepath + ".gpkg", layer='polygons')
        geometry.edges = read_file(filepath + ".gpkg", layer='edges')
        with open(filepath + ".json") as f:
            geometry.nodes = json.load(f)
        cls.tag_value.eval_polygons(geometry.polygons, "tag")
        cls.tag_value.eval_lines(geometry.edges, "tag")
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
                cls.tag_value.eval_polygons(geometry.polygons, "tag")
                cls.tag_value.eval_lines(geometry.edges, "tag")
                return geometry.cut_bbox(bbox)
            if filename[-8:] == '.osm.pbf':
                geometry.polygons, geometry.edges, geometry.nodes = parse_pbf(
                    filename, bbox)
                cls.tag_value.eval_polygons(geometry.polygons, "tag")
                cls.tag_value.eval_lines(geometry.edges, "tag")
                return geometry
            raise ValueError("Only .xml and .osm.pbf files supported")

        if query is not None:
            filepath = get_data(query, directory=directory)
            geometry.polygons, geometry.edges, geometry.nodes = parse_pbf(
                filepath, bbox)
            cls.tag_value.eval_polygons(geometry.polygons, "tag")
            cls.tag_value.eval_lines(geometry.edges, "tag")
            return geometry

        r = requests.get('http://www.overpass-api.de/api/xapi_meta?*[bbox=' +
                         str(bbox[0]) + ',' + str(bbox[1]) + ',' +
                         str(bbox[2]) + ',' + str(bbox[3]) + ']')
        with open(path.join(directory, str(bbox) + '.xml'), 'w') as f:
            f.write(r.text)
        root = ET.fromstring(r.text)
        geometry.polygons, geometry.edges, geometry.nodes = parse_xml(root)
        cls.tag_value.eval_polygons(geometry.polygons, "tag")
        cls.tag_value.eval_lines(geometry.edges, "tag")
        return geometry.cut_bbox(bbox)

    def save(self, package_name, directory='.'):
        """
        Save computed geometry to json & geopackage files.

        :param str package_name: name for created files to share
        :param str directory: saved geometry package directory
        """

        if len(findall(r"[#%&{}\\<>*?/ $!'\":@]", "ffa?aev")) > 0:
            raise ValueError("Wrong package name")

        filepath = path.join(directory, package_name)
        self.polygons.to_file(filepath + ".gpkg",
                              layer='polygons', driver="GPKG")
        self.edges.to_file(filepath + ".gpkg",
                           layer='edges', driver="GPKG")
        with open(filepath + ".json", 'w') as f:
            json.dump(self.nodes, f)

    def cut_bbox(self, bbox, inplace=False):
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
        polygons = clip(self.polygons, mask, keep_geom_type=True)
        edges = self.edges.iloc[clip(
            self.edges, mask, keep_geom_type=True).index].reset_index(drop=True)
        nodes = {k: v for k, v in self.nodes.items() if k in (
            set(edges.u) | set(edges.v))}

        if not inplace:
            geometry = Geometry()
            geometry.polygons, geometry.edges, geometry.nodes = polygons, edges, nodes
            return geometry

        self.polygons, self.edges, self.nodes = polygons, edges, nodes

    def plot(self):
        """
        Build folium map of all geometry data.

        :rtype: folium.folium.Map
        """

        return concat([self.polygons.geometry, self.edges.geometry]).explore()

    def to_networkx(self):
        """
        Build networkx weighted graph of road network. Weight measured in meters.

        :rtype: networkx.Graph
        """

        G = nx.Graph()
        for _, row in self.edges.iterrows():
            G.add_edge(self.nodes[row.u], self.nodes[row.v], weight=row.length)
        return G

    def minimum_spanning_tree(self, inplace=False):
        """
        Build minimum spanning tree of road graph.

        :param bool inplace: change initial geometry
        :return: None if inplace else new geometry object
        :rtype: Optional[Geometry]
        """

        G = self.to_networkx()
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

    def simplify_roads(self, threshold, inplace=False):
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
            elif row.length < threshold:
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

    @staticmethod
    def __compare_bbox(obj, bbox_comp, bbox_size):
        if bbox_comp is not None:
            bounds = obj.bounds
            bounds_size = (bounds[2] - bounds[0], bounds[3] - bounds[1])
            if bounds_size[0] == 0 or bounds_size[1] == 0:
                return None
            if bbox_size[0] / bounds_size[0] >= bbox_comp and bbox_size[1] / bounds_size[1] >= bbox_comp:
                return None
        return obj

    def simplify_polygons(self, bbox_comp=15, epsilon=None, inplace=False):
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
            self.__compare_bbox, args=[bbox_comp, bbox_size])
        polygons.geometry = polygons.geometry.simplify(
            epsilon, preserve_topology=True)

        if not inplace:
            geometry = Geometry()
            geometry.polygons, geometry.edges, geometry.nodes = polygons, deepcopy(
                self.edges), deepcopy(self.nodes)
            return geometry

        self.polygons = polygons
