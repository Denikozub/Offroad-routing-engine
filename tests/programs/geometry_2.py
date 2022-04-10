from offroad_routing import Geometry


def main():
    filename = "../maps/kozlovo.osm.pbf"
    bbox = [36.2, 56.61, 36.4, 56.67]
    geom = Geometry.parse(filename=filename, bbox=bbox)
    geom = geom.select_road_type({'service', 'residential'}, exclude=True)
    geom = geom.simplify_roads(50)
    geom = geom.minimum_spanning_tree()
    geom = geom.simplify_polygons(15)
    geom.save('kozlovo', '../maps')


if __name__ == "__main__":
    main()
