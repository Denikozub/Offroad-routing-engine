from offroad_routing import Geometry


def main():
    filename = "../maps/user_area.osm.pbf"
    bbox = [34, 59, 34.2, 59.1]
    geom = Geometry.parse(filename=filename, bbox=bbox)
    geom.simplify_roads(100, inplace=True)
    geom.simplify_polygons(15, inplace=True)
    geom.save('user_area', '../maps')


if __name__ == "__main__":
    main()
