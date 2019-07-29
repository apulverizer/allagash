from .dataset import Dataset


class DemandDataset(Dataset):
    def __init__(self, file, unique_field, demand_field):
        super().__init__(file, unique_field)
        self._demand_field = demand_field
        self._validate_demand_field()

    def _validate_demand_field(self):
        if self._demand_field not in self.df.columns:
            raise ValueError(f"'{self._demand_field}' not in {self._file}")
        if self.df[self._demand_field].dtype not in ['float64', 'int64']:
            raise ValueError(f"'{self._demand_field}' is not a numeric field in {self._file}")
