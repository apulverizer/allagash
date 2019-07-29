import geopandas


class Dataset:
    def __init__(self, file, unique_field):
        self._file = file
        self._unique_field = unique_field
        self._read_file()

    def _read_file(self):
        self.df = geopandas.read_file(self._file)
        if self._unique_field not in self.df.columns:
            raise ValueError(f"'{self._unique_field}' not in {self._file}")
