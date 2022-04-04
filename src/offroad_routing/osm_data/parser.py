from collections import deque
from math import fabs

from geopandas import GeoDataFrame
from offroad_routing.osm_data.osm_converter import OsmConverter
from offroad_routing.osm_data.tag_value import TagValue
from pandas import concat
from pandas import DataFrame
from pyrosm import OSM
from shapely.geometry import LineString
from shapely.geometry import mapping


class OsmParser:
    __slots__ = ("polygons", "multilinestrings", "tag_value", "bbox_size")

    def __init__(self):
        self.polygons = GeoDataFrame(columns=['tag', 'geometry'])
        self.multilinestrings = GeoDataFrame(columns=['tag', 'geometry'])
        self.tag_value = TagValue()
        self.bbox_size = None

    @staticmethod
    def __dissolve(roads):
        dissolved, tags = list(), list()
        for _, row in roads.iterrows():
            coords = mapping(row.geometry)['coordinates']
            coords = [segment[0] for segment in coords] + [coords[-1][1]]
            for i, line in enumerate(dissolved):
                if line[-1] == coords[0] or line[-1] == coords[-1]:
                    line.extend(
                        coords) if line[-1] == coords[0] else line.extend(reversed(coords))
                    for j, new_line in enumerate(dissolved):
                        if i == j:
                            continue
                        if line[-1] == new_line[0]:
                            line.extend(new_line)
                            dissolved.pop(j)
                            tags.pop(j)
                            break
                        if line[-1] == new_line[-1]:
                            line.extend(reversed(new_line))
                            dissolved.pop(j)
                            tags.pop(j)
                            break
                    break
                elif line[0] == coords[-1] or line[0] == coords[0]:
                    line.extendleft(
                        reversed(coords)) if line[0] == coords[-1] else line.extendleft(coords)
                    for j, new_line in enumerate(dissolved):
                        if i == j:
                            continue
                        if line[0] == new_line[0]:
                            line.extendleft(new_line)
                            dissolved.pop(j)
                            tags.pop(j)
                            break
                        if line[0] == new_line[-1]:
                            new_line.extend(line)
                            dissolved.pop(i)
                            tags.pop(i)
                            break
                    break
            else:
                dissolved.append(deque(coords))
                tags.append(row.highway)
        return GeoDataFrame({'tag': tags, 'geometry': [LineString(line) for line in dissolved]})

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
            self.polygons = concat([self.polygons,
                                    natural.loc[natural.geometry.type == 'Polygon']])
            multipolygons = concat([multipolygons,
                                    natural.loc[natural.geometry.type == 'MultiPolygon']])
            natural.drop(natural.index, inplace=True)

        landuse = osm.get_landuse()
        if landuse is not None:
            landuse = landuse.loc[:, ['landuse', 'geometry']].rename(
                columns={'landuse': 'tag'})
            self.polygons = concat([self.polygons,
                                    landuse.loc[landuse.geometry.type == 'Polygon']])
            multipolygons = concat([multipolygons,
                                    landuse.loc[landuse.geometry.type == 'MultiPolygon']])
            landuse.drop(landuse.index, inplace=True)

        # splitting multipolygons to polygons
        for i in range(multipolygons.shape[0]):
            tag = multipolygons.tag.iloc[i]
            for polygon in multipolygons.geometry.iloc[i].geoms:
                self.polygons = concat([self.polygons,
                                        DataFrame({'tag': tag, 'geometry': polygon}, index=[0])], ignore_index=True)

        roads = osm.get_network()
        if roads is not None:
            self.multilinestrings = self.__dissolve(
                roads[["highway", "geometry"]])

        self.tag_value.eval(self.polygons, self.multilinestrings, "tag")
