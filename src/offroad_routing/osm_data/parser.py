from math import fabs

from geopandas import GeoDataFrame
from offroad_routing.osm_data.osm_converter import OsmConverter
from offroad_routing.osm_data.tag_value import TagValue
from pyrosm import OSM
from shapely.geometry import mapping


class OsmParser:

    __slots__ = ("polygons", "multilinestrings", "tag_value", "bbox_size")

    def __init__(self):
        self.polygons = GeoDataFrame(columns=['tag', 'geometry'])
        self.multilinestrings = GeoDataFrame(columns=['tag', 'geometry'])
        self.tag_value = TagValue()
        self.bbox_size = None

    @staticmethod
    def __get_first_point(line):
        coords = mapping(line)['coordinates']
        return coords[0][0] if isinstance(coords[0][0], tuple) else coords[0]

    @staticmethod
    def __get_last_point(line):
        coords = mapping(line)['coordinates']
        return coords[-1][1] if isinstance(coords[0][0], tuple) else coords[1]

    def __dissolve(self, src_roads):
        roads = src_roads.copy()
        current = 1
        points = dict()
        for index, row in roads.iterrows():
            start = self.__get_first_point(row.geometry)
            end = self.__get_last_point(row.geometry)
            for number, borders in points.items():
                if start in borders:
                    roads.at[index, "id"] = number
                    borders.add(end)
                    break
                if end in borders:
                    roads.at[index, "id"] = number
                    borders.add(start)
                    break
            else:
                roads.at[index, "id"] = current
                points[current] = set()
                points[current].add(start)
                points[current].add(end)
                current += 1
        return roads.dissolve(by="id").reset_index().drop(columns=["id"])

    def compute_geometry(self, bbox, filename=None):
        """
        Parse OSM file (area in bbox) to retrieve information about geometry.

        :param Sequence[float] bbox: area to be parsed in format (min_lon, min_lat, max_lon, max_lat)
        :param Optional[str] filename: map file in .osm.pbf format or None (map will be downloaded)
        """
        assert len(bbox) == 4
        self.bbox_size = (fabs(bbox[2] - bbox[0]), fabs(bbox[3] - bbox[1]))

        if filename is None:
            converter = OsmConverter(bbox)
            filename = converter.filename

        osm = OSM(filename, bounding_box=bbox)
        multipolygons = GeoDataFrame(columns=['tag', 'geometry'])

        natural = osm.get_natural()
        if natural is not None:
            natural = natural.loc[:, ['natural', 'geometry']].rename(
                columns={'natural': 'tag'})
            self.polygons = self.polygons.append(
                natural.loc[natural.geometry.type == 'Polygon'])
            multipolygons = multipolygons.append(
                natural.loc[natural.geometry.type == 'MultiPolygon'])
            natural.drop(natural.index, inplace=True)

        landuse = osm.get_landuse()
        if landuse is not None:
            landuse = landuse.loc[:, ['landuse', 'geometry']].rename(
                columns={'landuse': 'tag'})
            self.polygons = self.polygons.append(
                landuse.loc[landuse.geometry.type == 'Polygon'])
            multipolygons = multipolygons.append(
                landuse.loc[landuse.geometry.type == 'MultiPolygon'])
            landuse.drop(landuse.index, inplace=True)

        # splitting multipolygons to polygons
        for i in range(multipolygons.shape[0]):
            tag = multipolygons.tag.iloc[i]
            for polygon in multipolygons.geometry.iloc[i].geoms:
                self.polygons = self.polygons.append(
                    {'tag': tag, 'geometry': polygon}, ignore_index=True)

        roads = osm.get_network()
        if roads is not None:
            roads = self.__dissolve(roads[["highway", "geometry"]])
            self.multilinestrings = GeoDataFrame(roads
                                                 .loc[roads.geometry.type == 'MultiLineString']).rename(
                columns={'highway': 'tag'})

        self.tag_value.eval(self.polygons, self.multilinestrings, "tag")
