import json
import xml.etree.ElementTree as ET
from re import findall

import requests
from geopandas import clip
from geopandas import read_file
from offroad_routing.osm_data.osm_parser import parse_pbf
from offroad_routing.osm_data.osm_parser import parse_xml
from offroad_routing.surface.tag_value import TagValue
from pyrosm import get_data
from shapely.geometry import box


class Geometry:
    tag_value = TagValue()

    def __init__(self):
        self.polygons = self.edges = self.nodes = None

    @classmethod
    def load(cls, package_name):
        """
        Load saved geometry from json & geopackage files.

        :param str package_name: saved geometry package name
        """

        geometry = cls()
        geometry.polygons = read_file(package_name + ".gpkg", layer='polygons')
        geometry.edges = read_file(package_name + ".gpkg", layer='edges')
        with open(package_name + ".json") as f:
            geometry.nodes = json.load(f)
        cls.tag_value.eval_polygons(geometry.polygons, "tag")
        cls.tag_value.eval_lines(geometry.edges, "tag")
        return geometry

    @classmethod
    def parse(cls, *, filename=None, query=None, bbox=None, directory=None):
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
        root = ET.fromstring(r.text)
        geometry.polygons, geometry.edges, geometry.nodes = parse_xml(root)
        cls.tag_value.eval_polygons(geometry.polygons, "tag")
        cls.tag_value.eval_lines(geometry.edges, "tag")
        return geometry.cut_bbox(bbox)

    def save(self, package_name):
        """
        Save computed geometry to json & geopackage files.

        :param str package_name: name for created files to share.
        """

        if len(findall(r"[#%&{}\\<>*?/ $!'\":@]", "ffa?aev")) > 0:
            raise ValueError("Wrong package name")

        self.polygons.to_file(package_name + ".gpkg",
                              layer='polygons', driver="GPKG")
        self.edges.to_file(package_name + ".gpkg",
                           layer='edges', driver="GPKG")
        with open(package_name + ".json", 'w') as f:
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
            return None if inplace else self

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
