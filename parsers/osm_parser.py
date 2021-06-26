from parsers.osm_converter import OsmConverter
from math import fabs
from pandas import DataFrame


class OsmParser:

    def __init__(self):
        self.polygons = None
        self.linestrings = None
        self.multilinestrings = None
        self.bbox_size = None
    
    def compute_geometry(self, bbox, filename=None):
        """
        parse OSM file (area in bbox) to retrieve information about needed tags
        :param bbox: in format min_lon, min_lat, max_lon, max_lat
        :param filename: None (map will be downloaded) or in .osm.pbf format
        :return: None
        """

        if filename is not None and type(filename) != str:
            raise TypeError("wrong filename type")

        iter(bbox)

        # download .osm.pbf map        
        if filename is None:
            converter = OsmConverter(bbox)
            filename = converter.filename

        # for Windows compilation
        from pyrosm import OSM
        from geopandas import GeoDataFrame

        # parsing OMS map with pyrosm
        osm = OSM(filename, bounding_box=bbox)
        custom_filter = {'highway' : ['motorway', 'trunk', 'primary', 'secondary', 'tertiary', 'unclassified', 'track', 'road', 'footway', 'path'], 'railway' : ['light_rail', 'rail'], 'natural' : ['wood', 'scrub', 'grassland', 'sand', 'mud', 'wetland', 'water', 'bay', 'beach', 'glacier', 'peninsula', 'dune'], 'landuse' : ['construction', 'industrial', 'residential', 'farmland', ' 	allotments', 'forest', 'farmyard', 'orchard', 'meadow', 'brownfield', 'grass', 'greenfield', 'greenhouse_horticulture', 'landfill', 'military', 'quarry', 'railway', 'village_green'], 'waterway' : True, 'water' : True, 'geological' : True, 'barrier' : ['cable_barrier', 'fence', 'wall'], 'military' : ['danger_area']}
        pois = osm.get_pois(custom_filter=custom_filter)
        df = pois[['geometry']]
        tags = ['natural', 'highway', 'landuse', 'railway', 'waterway', 'water', 'geological', 'barrier', 'military'] # 'building'
        for tag in tags:
            try:
                df = df.join(pois[tag])
            except KeyError:
                pass
        pois = DataFrame(df.iloc[:, 1:].stack()).reset_index()[['level_1', 0]].rename(columns={'level_1' : "key", 0 : "value"})
        pois = GeoDataFrame(pois.join(df.geometry))
        
        # extracting figures
        self.polygons = DataFrame(pois.loc[(pois.geometry.type == 'Polygon') | ((pois.key.isin(['natural', 'water', 'landuse'])) & (pois.geometry.type == 'MultiLineString'))])
        multipolygons = DataFrame(pois.loc[pois.geometry.type == 'MultiPolygon'])
        self.linestrings = DataFrame(pois.loc[(pois.geometry.type == 'LineString') & (~pois.key.isin(['natural', 'water', 'landuse']))])
        self.multilinestrings = DataFrame(pois.loc[(pois.geometry.type == 'MultiLineString') & (~pois.key.isin(['natural', 'water', 'landuse']))])
        
        # splitting multipolygons to polygons
        for i in range(multipolygons.shape[0]):
            key = multipolygons.key.iloc[i]
            value = multipolygons.value.iloc[i]
            for polygon in multipolygons.geometry.iloc[i].geoms:
                self.polygons = self.polygons.append({'key': key,
                                                      'value' : value,
                                                      'geometry': polygon}, ignore_index=True)
        

        # bounding box size
        self.bbox_size = (fabs(bbox[2] - bbox[0]), fabs(bbox[3] - bbox[1]))

