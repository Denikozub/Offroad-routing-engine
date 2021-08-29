from math import fabs
from typing import Sequence, Optional

from pandas import DataFrame

from osm_data.osm_converter import OsmConverter


class OsmParser(object):

    def __init__(self):
        self.polygons = DataFrame(columns=['tag', 'geometry'])
        self.multilinestrings = DataFrame(columns=['tag', 'geometry'])
        self.bbox_size = None
    
    def compute_geometry(self, bbox: Sequence[float], filename: Optional[str] = None) -> None:
        """
        Parse OSM file (area in bbox) to retrieve information about needed tags.

        :param bbox: in format min_lon, min_lat, max_lon, max_lat
        :param filename: None (map will be downloaded) or in .osm.pbf format
        """

        if filename is None:
            converter = OsmConverter(bbox)
            filename = converter.filename

        # for Windows compilation
        from pyrosm import OSM

        osm = OSM(filename, bounding_box=bbox)
        multipolygons = DataFrame(columns=['tag', 'geometry'])
        
        natural = osm.get_natural()
        if natural is not None:
            natural = natural.loc[:, ['natural', 'geometry']].rename(columns={'natural': 'tag'})
            self.polygons = self.polygons.append(DataFrame(natural.loc[natural.geometry.type == 'Polygon']))
            multipolygons = multipolygons.append((natural.loc[natural.geometry.type == 'MultiPolygon']))
            natural.drop(natural.index, inplace=True)
        
        landuse = osm.get_landuse()
        if landuse is not None:
            landuse = landuse.loc[:, ['landuse', 'geometry']].rename(columns={'landuse': 'tag'})
            self.polygons = self.polygons.append(DataFrame(landuse.loc[landuse.geometry.type == 'Polygon']))
            multipolygons = multipolygons.append(DataFrame(landuse.loc[landuse.geometry.type == 'MultiPolygon']))
            landuse.drop(landuse.index, inplace=True)
        
        # splitting multipolygons to polygons
        for i in range(multipolygons.shape[0]):
            tag = multipolygons.tag.iloc[i]
            for polygon in multipolygons.geometry.iloc[i].geoms:
                self.polygons = self.polygons.append({'tag': tag, 'geometry': polygon}, ignore_index=True)

        roads = osm.get_network()
        if roads is not None:
            self.multilinestrings = DataFrame(roads.loc[:, ['highway', 'geometry']]
                    .loc[roads.geometry.type == 'MultiLineString']).rename(columns={'highway': 'tag'})
            roads.drop(roads.index, inplace=True)

        self.bbox_size = (fabs(bbox[2] - bbox[0]), fabs(bbox[3] - bbox[1]))
