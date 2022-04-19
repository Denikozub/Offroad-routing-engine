import base64
from datetime import datetime

from offroad_routing.pathfinding.path import Path


class GpxTrack:
    """
    Save and visualize off-road path on the map.
    """

    __slots__ = ("__path",)

    def __init__(self, path: Path):
        """
        :param Path path: initialised and retraced path
        """
        self.__path = path

    @staticmethod
    def __write_head(file):
        print('<?xml version="1.0" encoding="UTF-8"?>', file=file)
        print('<gpx xmlns="http://www.topografix.com/GPX/1/1" ' +
              'creator="https://github.com/Denikozub/Offroad-routing-engine" ' +
              'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" ' +
              'xsi:schemaLocation="http://www.topografix.com/GPX/1/1 ' +
              'http://www.topografix.com/GPX/1/1/gpx.xsd" version="1.1">', file=file)

    def __write_start_goal(self, file):
        start, goal = self.__path.start, self.__path.goal
        print(f'\t<wpt lat="{start[1]:f}" lon="{start[0]:f}">\n\t\t<name>Start</name>\n\t</wpt>', file=file)
        print(f'\t<wpt lat="{goal[1]:f}" lon="{goal[0]:f}">\n\t\t<name>Goal</name>\n\t</wpt>', file=file)

    def __write_track(self, file):
        print('\t<trk>\n\t\t<name>%s</name>\n\t\t<trkseg>' % str(datetime.today().strftime('%Y-%m-%d')), file=file)
        for point in self.__path.path:
            print(f'\t\t\t<trkpt lat="{point[1]:f}" lon="{point[0]:f}"></trkpt>', file=file)
        print('\t\t</trkseg>\n\t</trk>', file=file)

    def write_file(self, filename):
        """
        Save path to gpx file.

        :param str filename: name of the file to save track into (.gpx)
        """
        assert filename[-4:] == ".gpx"
        file = open(filename, 'w')
        GpxTrack.__write_head(file)
        self.__write_start_goal(file)
        self.__write_track(file)
        print('</gpx>', file=file)
        file.close()

    def visualize(self):
        """
        Generate link to visualize path using https://nakarte.me
        """
        start, goal = self.__path.start, self.__path.goal
        xml = str([{"n": str(datetime.today().strftime('%Y-%m-%d')),
                    "p": [{"n": "Start", "lt": start[1], "ln": start[0]}, {"n": "Goal", "lt": goal[1], "ln": goal[0]}],
                    "t": [[[lat, lon] for lon, lat in self.__path.path]]}]).replace("'", "\"")
        base = base64.encodebytes(bytes(xml, 'utf-8')).decode("utf-8").replace("\n", "")
        print("Go to website: https://nakarte.me/#nktj=%s" % base)

    def plot(self, **kwargs):
        if 'color' not in kwargs.keys():
            kwargs['color'] = 'red'
        return self.__path.to_gpd().explore(**kwargs)
