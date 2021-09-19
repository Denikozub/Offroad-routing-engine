from pandas import HDFStore

from offroad_routing.osm_data.pruner import Pruner


class GeometrySaver(Pruner):

    def __init__(self):
        super().__init__()

    def save_geometry(self, filename: str) -> None:
        if filename[-3:] != ".h5":
            raise ValueError("Wrong file format")
        with HDFStore(filename) as store:
            store["polygons"] = self.polygons
            store["multilinestrings"] = self.multilinestrings

    def load_geometry(self, filename: str) -> None:
        if filename[-3:] != ".h5":
            raise ValueError("Wrong file format")
        with HDFStore(filename) as store:
            self.polygons = store["polygons"]
            self.multilinestrings = store["multilinestrings"]
