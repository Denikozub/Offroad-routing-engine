from parsers.df_builder import DfBuilder
from pandas import HDFStore


class OsmData(DfBuilder):

    def __init__(self):
        super().__init__()

    def save_geometry(self, filename):
        """
        save computed data to filename
        :param filename: standard filename requirements
        :return: None
        """

        if type(filename) != str:
            raise TypeError("wrong filename type")

        store = HDFStore(filename)
        store["polygons"] = self.polygons
        store["multilinestrings"] = self.multilinestrings

    def load_geometry(self, filename):
        """
        load saved data from filename
        :param filename: standard filename requirements
        :return: None
        """

        if type(filename) != str:
            raise TypeError("wrong filename type")

        store = HDFStore(filename)
        self.polygons = store["polygons"]
        self.multilinestrings = store["multilinestrings"]

