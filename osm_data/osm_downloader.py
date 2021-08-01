from os import system, remove
from typing import Sequence


class OsmDownloader(object):

    def __init__(self, bbox: Sequence[float]) -> None:
        """
        Download OSM XLM file of given bbox.

        :param bbox: in format min_lon, min_lat, max_lon, max_lat
        """
        self.bbox = bbox
        self.filename = "request_map.osm"
        addr = '"http://www.overpass-api.de/api/xapi_meta?*[bbox=' \
            + str(bbox[0]) + ',' + str(bbox[1]) + ',' + str(bbox[2]) + ',' + str(bbox[3]) + ']"'
        system('curl -g -o ' + self.filename + ' ' + addr)
        
    def __del__(self):
        remove(self.filename)
