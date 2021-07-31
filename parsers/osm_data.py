from parsers.pruner import Pruner
from pandas import HDFStore


class OsmData(Pruner):

    def __init__(self):
        super().__init__()

    def save_geometry(self, filename: str) -> None:
        store = HDFStore(filename)
        store["polygons"] = self.polygons
        store["multilinestrings"] = self.multilinestrings

    def load_geometry(self, filename: str) -> None:
        store = HDFStore(filename)
        self.polygons = store["polygons"]
        self.multilinestrings = store["multilinestrings"]
