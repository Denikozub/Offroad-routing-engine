from geopandas import GeoDataFrame
from offroad_routing.geometry.algorithms import point_distance
from pandas import concat
from pandas import DataFrame
from pyrosm import OSM
from shapely.geometry import LineString
from shapely.geometry import MultiLineString
from shapely.geometry import Polygon


def parse_pbf(filename, bbox):
    """
    Parse .osm.pbf OSM file, return data about features natural, landuse and highway.

    :param str filename: .osm.pbf OSM file
    :param Optional[Sequence[float]] bbox: area to be parsed in format (min_lon, min_lat, max_lon, max_lat)
    :return: polygons, road edges, road nodes
    :rtype: Tuple[GeoDataFrame, GeoDataFrame, Dict[int, TPoint]]
    """

    osm = OSM(filename, bounding_box=bbox)
    multipolygons = GeoDataFrame(columns=['tag', 'geometry'])
    polygons = GeoDataFrame(columns=['tag', 'geometry'])

    natural = osm.get_natural()
    if natural is not None:
        natural = natural.loc[:, ['natural', 'geometry']].rename(
            columns={'natural': 'tag'})
        polygons = concat(
            [polygons, natural.loc[natural.geometry.type == 'Polygon']])
        multipolygons = concat(
            [multipolygons, natural.loc[natural.geometry.type == 'MultiPolygon']])

    landuse = osm.get_landuse()
    if landuse is not None:
        landuse = landuse.loc[:, ['landuse', 'geometry']].rename(
            columns={'landuse': 'tag'})
        polygons = concat(
            [polygons, landuse.loc[landuse.geometry.type == 'Polygon']])
        multipolygons = concat(
            [multipolygons, landuse.loc[landuse.geometry.type == 'MultiPolygon']])

    for i in range(multipolygons.shape[0]):
        tag = multipolygons.tag.iloc[i]
        for polygon in multipolygons.geometry.iloc[i].geoms:
            polygons = concat([polygons, DataFrame(
                {'tag': tag, 'geometry': polygon}, index=[0])], ignore_index=True)

    nodes, edges = osm.get_network(nodes=True)
    if edges is not None:
        nodes = DataFrame(nodes[["id", "geometry"]])
        nodes.geometry = nodes.geometry.apply(lambda x: (x.x, x.y))
        nodes = nodes.set_index('id').to_dict()['geometry']
        edges = edges[["highway", "geometry", "u", "v", "length"]].rename(columns={
                                                                          "highway": "tag"})

    polygons.crs = 'epsg:4326'
    return polygons, edges, nodes


def parse_xml(root, features=('landuse', 'natural', 'highway')):
    """
    Parse .xml OSM file, return data about features natural, landuse and highway.

    :param ET.Element root: xml root
    :param Tuple[str, ...] features: feature tags to be parsed
    :return: polygons, road edges, road nodes
    :rtype: Tuple[GeoDataFrame, GeoDataFrame, Dict[int, TPoint]]
    """

    features = set(features)
    nodes, ways, roads, polygons = dict(), dict(), list(), list()
    for child in root:

        if child.tag == 'node':
            node = child.attrib
            nodes[int(node['id'])] = (float(node['lon']), float(node['lat']))

        elif child.tag == 'way':
            way, tag = list(), None
            for part in child:
                if part.tag == 'nd':
                    way.append(int(part.attrib['ref']))
                elif part.attrib['k'] in features:
                    tag = part.attrib['v']
            if way[0] == way[-1]:
                geometry = Polygon([nodes[pt]
                                    for pt in way if pt in nodes.keys()])
                if tag is None:
                    ways[child.attrib['id']] = geometry
                else:
                    polygons.append((tag, geometry))
            else:
                geometry = LineString([nodes[pt]
                                       for pt in way if pt in nodes.keys()])
                if tag is None:
                    ways[child.attrib['id']] = geometry
                else:
                    roads.append((tag, way))

        elif child.tag == 'relation':
            relation, tag = (list(), list()), None
            for part in child:
                if part.tag == 'member':
                    if part.attrib['role'] == 'outer':
                        relation[0].append(part.attrib['ref'])
                    else:
                        relation[1].append(part.attrib['ref'])
                elif part.attrib['k'] == 'type' and part.attrib['v'] != 'multipolygon':
                    tag = None
                    break
                elif part.attrib['k'] in features:
                    tag = part.attrib['v']
            if tag is not None:
                if len(relation[0]) == 1:
                    outer = ways[relation[0][0]]
                else:
                    outer = MultiLineString(
                        [ways[way] for way in relation[0] if way in ways.keys()]).convex_hull
                inner = [ways[way] for way in relation[1]
                         if way in ways.keys() and isinstance(ways[way], Polygon)]
                geometry = Polygon(outer, inner)
                if not geometry.is_empty:
                    polygons.append((tag, geometry))

    polygons = GeoDataFrame(
        polygons, columns=['tag', 'geometry'], crs='epsg:4326')
    roads = DataFrame(roads, columns=['tag', 'geometry'])
    roads.geometry = roads.geometry.apply(
        lambda x: [[x[i], x[i + 1]] for i in range(len(x) - 1)])
    roads = roads.explode('geometry').reset_index(drop=True)
    roads[['u', 'v']] = DataFrame(roads.geometry.tolist(), index=roads.index)
    roads.geometry = roads.apply(
        lambda x: LineString((nodes[x.u], nodes[x.v])), axis=1)
    roads['length'] = roads.apply(lambda x: point_distance(
        nodes[x.u], nodes[x.v]), axis=1) * 1000
    roads = GeoDataFrame(roads, crs='epsg:4326')
    nodes = {k: v for k, v in nodes.items() if k in (
        set(roads.u) | set(roads.v))}

    return polygons, roads, nodes
