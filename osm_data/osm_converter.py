from os import system, remove
from osm_data.osm_downloader import OsmDownloader
from typing import Sequence


class OsmConverter(OsmDownloader):

    def __init__(self, bbox: Sequence[float]) -> None:
        """
        Convert file from OSM XML to PBF
        :param bbox: in format min_lon, min_lat, max_lon, max_lat
        """
        super().__init__(bbox)
        system('osmosis --read-xml ' + self.filename + ' --write-pbf ' + self.filename + '.pbf')
        remove(self.filename)
        self.filename += '.pbf'
