from os import system, remove


class OsmDownloader:

    def __init__(self, bbox):
        self.bbox = bbox
        self.filename = "maps/request_map.osm"
        addr = '"http://www.overpass-api.de/api/xapi_meta?*[bbox=' \
            + str(bbox[0])  + ',' + str(bbox[1]) + ',' + str(bbox[2]) + ',' + str(bbox[3]) + ']"'
        system('curl -g -o ' + self.filename + ' ' + addr)
        
    def __del__(self):
        remove(self.filename)

