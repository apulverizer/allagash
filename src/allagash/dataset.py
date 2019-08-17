import random
import string


class Dataset:
    def __init__(self, dataframe, unique_field, name=None):
        self._df = dataframe
        self._unique_field = unique_field
        self._name = name
        if self._name is None:
            self._name = ''.join(random.choices(string.ascii_uppercase, k=6))

    @property
    def df(self):
        return self._df

    @property
    def unique_field(self):
        return self._unique_field

    @property
    def name(self):
        return self._name


class DemandDataset(Dataset):
    def __init__(self, dataframe, unique_field, demand_field,  name=None):
        super().__init__(dataframe, unique_field, name=name)
        self._demand_field = demand_field
        self._validate_demand_field()

    @property
    def demand_field(self):
        return self._demand_field

    def _validate_demand_field(self):
        if self._demand_field not in self.df.columns:
            raise ValueError(f"'{self._demand_field}' not in {self.df}")
        if self.df[self._demand_field].dtype not in ['float64', 'int64']:
            raise ValueError(f"'{self._demand_field}' is not a numeric field in {self.df}")


class SupplyDataset(Dataset):
    def __init__(self, dataframe, unique_field, name=None):
        super().__init__(dataframe, unique_field, name=name)
