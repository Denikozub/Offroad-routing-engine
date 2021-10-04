from numpy import save, load, array

from offroad_routing.osm_data.pruner import Pruner


class GeometrySaver(Pruner):

    def __init__(self):
        super().__init__()

    def save_geometry(self, filename: str):
        """
        Save computed geometry to .npy binary file.

        :param filename: .npy filename to be created.
        """
        if filename[-4:] != ".npy":
            raise ValueError("Wrong file format")
        save(filename, [self.polygons, self.multilinestrings])

    def load_geometry(self, filename: str):
        """
        Load saved geometry from .npy file.

        :param filename: .npy filename with saved geometry.
        """
        if filename[-4:] != ".npy":
            raise ValueError("Wrong file format")
        self.polygons, self.multilinestrings = load(filename, allow_pickle=True)
