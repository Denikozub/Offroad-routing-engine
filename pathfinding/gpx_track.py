from datetime import datetime
import base64

from pathfinding.path import Path


class GpxTrack(object):
    def __init__(self, path: Path):
        self.path = path
        if self.path.path is None:
            self.path.retrace()

    @staticmethod
    def write_head(file):
        print('<?xml version="1.0" encoding="UTF-8"?>', file=file)
        print('<gpx xmlns="http://www.topografix.com/GPX/1/1" ' +
              'creator="https://github.com/Denikozub/Offroad-routing-engine" ' +
              'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" ' +
              'xsi:schemaLocation="http://www.topografix.com/GPX/1/1 ' +
              'http://www.topografix.com/GPX/1/1/gpx.xsd" version="1.1">', file=file)

    def write_start_goal(self, file):
        start, goal = self.path.start, self.path.goal
        print('\t<wpt lat="%f" lon="%f">\n\t\t<name>Start</name>\n\t</wpt>' % (start[1], start[0]), file=file)
        print('\t<wpt lat="%f" lon="%f">\n\t\t<name>Goal</name>\n\t</wpt>' % (goal[1], goal[0]), file=file)

    def write_track(self, file):
        print('\t<trk>\n\t\t<name>%s</name>\n\t\t<trkseg>' % str(datetime.today().strftime('%Y-%m-%d')), file=file)
        for point in self.path.path:
            print('\t\t\t<trkpt lat="%f" lon="%f"></trkpt>' % (point[1], point[0]), file=file)
        print('\t\t</trkseg>\n\t</trk>', file=file)

    def write_file(self, filename: str) -> None:
        assert filename[-4:] == ".gpx"
        file = open(filename, 'w')
        self.write_head(file)
        self.write_start_goal(file)
        self.write_track(file)
        print('</gpx>', file=file)
        file.close()

    def visualize(self) -> None:
        start, goal = self.path.start, self.path.goal
        xml = str([{"n": str(datetime.today().strftime('%Y-%m-%d')),
                    "p": [{"n": "Start", "lt": start[1], "ln": start[0]}, {"n": "Goal", "lt": goal[1], "ln": goal[0]}],
                    "t": [[[lat, lon] for lon, lat in self.path.path]]}]).replace("'", "\"")
        base = base64.encodebytes(bytes(xml, 'utf-8')).decode("utf-8").replace("\n", "")
        print("Go to website: https://nakarte.me/#nktj=%s" % base)
