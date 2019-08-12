import random
import string


class Dataset:
    def __init__(self, dataframe, unique_field, name=None):
        self.df = dataframe
        self.unique_field = unique_field
        self.name = name
        if self.name is None:
            self.name = ''.join(random.choices(string.ascii_uppercase, k=6))


class DemandDataset(Dataset):
    def __init__(self, dataframe, unique_field, demand_field,  name=None):
        super().__init__(dataframe, unique_field, name=name)
        self._demand_field = demand_field
        self._validate_demand_field()

    def _validate_demand_field(self):
        if self._demand_field not in self.df.columns:
            raise ValueError(f"'{self._demand_field}' not in {self.df}")
        if self.df[self._demand_field].dtype not in ['float64', 'int64']:
            raise ValueError(f"'{self._demand_field}' is not a numeric field in {self.df}")


class SupplyDataset(Dataset):
    def __init__(self, dataframe, unique_field, name=None):
        super().__init__(dataframe, unique_field, name=name)
