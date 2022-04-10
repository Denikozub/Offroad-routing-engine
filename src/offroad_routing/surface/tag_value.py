polygon_values = {'wood': 20, 'wetland': 100, 'allotments': 10, 'peat_cutting': 200, 'residential': 10,
                  'highway': 1, 'heath': 15, 'water': 1e5, 'beach': 20, 'scrub': 50, 'grass': 10,
                  'grassland': 10, 'sand': 20, 'bay': 1e5, 'meadow': 10, 'industrial': 1e5,
                  'forest': 20, 'cemetery': 100, 'landfill': 1e5, 'commercial': 1e5,
                  'retail': 1e5, 'garages': 1e5, 'brownfield': 1e5,
                  'basin': 1e5, 'construction': 1e5, 'farmyard': 20, 'farmland': 20,
                  'orchard': 20, 'logging': 1e5, 'flowerbed': 20, 'quarry': 50, 'military': 1e5,
                  'harbour': 1e5, 'reservoir': 1e5, 'cattlegrave': 1e5}
linestring_values = {'tertiary': 1, 'unclassified': 5, 'track': 5, 'road': 1, 'path': 5, 'trunk': 1,
                     'secondary': 1, 'residential': 1, 'service': 1, 'footway': 1, 'steps': 1,
                     'pedestrian': 1, 'secondary_link': 1, 'tertiary_link': 1, 'bridleway': 1}


class TagValue:

    @staticmethod
    def eval_polygons(dataset, column: str) -> None:
        dataset[column] = dataset[column].apply(
            lambda x: [polygon_values[x]])

    @staticmethod
    def eval_lines(dataset, column: str) -> None:
        dataset[column] = dataset[column].apply(
            lambda x: linestring_values[x])
