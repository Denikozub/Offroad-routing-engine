from os import system, remove
from parsers.osm_downloader import OsmDownloader


class OsmConverter(OsmDownloader):

    def __init__(self, bbox):
        super().__init__(bbox)
        system('osmosis --read-xml ' + self.filename + ' --write-pbf ' + self.filename + '.pbf')
        remove(self.filename)
        self.filename += '.pbf'

