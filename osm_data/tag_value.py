class TagValue(object):
    def __init__(self): pass

    @staticmethod
    def eval(polygons, multilinestrings, column: str) -> None:
        polygon_values = {'wood': 20, 'wetland': 100, 'allotments': 10, 'peat_cutting': 200, 'residential': 10,
                          'highway': 1, 'heath': 15, 'water': float("inf"), 'beach': 20, 'scrub': 50, 'grass': 10,
                          'grassland': 10, 'sand': 20, 'bay': float("inf"), 'meadow': 10, 'industrial': float("inf"),
                          'forest': 20, 'cemetery': 100, 'landfill': float("inf"), 'commercial': float("inf"),
                          'retail': float("inf"), 'garages': float("inf"), 'brownfield': float("inf"),
                          'basin': float("inf"), 'construction': float("inf"), 'farmyard': 20, 'farmland': 20,
                          'orchard': 20, 'logging': float("inf"), 'flowerbed': 20, 'quarry': 50, 'military': float("inf"),
                          'harbour': float("inf"), 'reservoir': float("inf"), 'cattlegrave': float("inf")}
        multilinestring_values = {'tertiary': 1, 'unclassified': 5, 'track': 5, 'road': 1, 'path': 5, 'trunk': 1,
                                  'secondary': 1, 'residential': 1, 'service': 1, 'footway': 1,  'steps': 1,
                                  'pedestrian': 1, 'secondary_link': 1, 'tertiary_link': 1, 'bridleway': 1}
        polygons[column] = polygons[column].apply(lambda x: polygon_values[x])
        multilinestrings[column] = multilinestrings[column].apply(lambda x: multilinestring_values[x])
