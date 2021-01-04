import re


class MpParser:

    polyline_good = (0x1, 0x2, 0x4, 0x6, 0x7, 0x8, 0x9, 0xa, 0xb, 0xd, 0xe, 0x16, 0x1a,
                     0x1b, 0x1c, 0x27, 0x28, 0x29, 0x2a, 0x2b, 0x32, 0x33, 0x34, 0x35)
    polyline_bad = (0x3, 0x15, 0x18, 0x19, 0x1e, 0x1f)
    offset_to_type = 16
    offset_to_coord = 7

    def __init__(self, bbox):
        self.bbox = bbox
        self.slazav_map = None

    def open_mp(self):
        file_mp = '../maps/' + self.bbox + '.mp'
        self.slazav_map = open(file_mp, encoding="ISO-8859-1").read()
        polyline_count = self.slazav_map.count('[POLYLINE]')
        return polyline_count

    def parse_polyline(self, polyline):
        polyline[0] = self.slazav_map.find('[POLYLINE]', polyline[0] + 1) + self.offset_to_type
        type_line = int(self.slazav_map[polyline[0]:self.slazav_map.find('\n', polyline[0])], 16)
        if not (type_line in self.polyline_good or type_line in self.polyline_bad):
            return 0, 0
        start_coord = self.slazav_map.find('Data', polyline[0]) + self.offset_to_coord
        coord = re.split('\),\(|,', self.slazav_map[start_coord:(self.slazav_map.find('\n', start_coord) - 1)])
        return coord, type_line
