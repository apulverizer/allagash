import random
import string
import pandas as pd


class Dataset:
    def __init__(self, dataframe, unique_field, name=None):
        """
        The base dataset that :class:`~allagash.dataset.DemandDataset` and :class:`~allagash.dataset.SupplyDataset` are derived from

        :param ~geopandas.GeoDataFrame dataframe: A geodataframe containing the spatial data
        :param str unique_field: A unique field/column name in the geodataframe
        :param str name: An optional name for the dataset
        """
        self._validate(dataframe, name, unique_field)
        self._df = dataframe
        self._unique_field = unique_field
        self._name = name
        if self._name is None:
            self._name = ''.join(random.choices(string.ascii_uppercase, k=6))

    @staticmethod
    def _validate(dataframe, name, unique_field):
        if not isinstance(dataframe, pd.DataFrame):
            raise TypeError(f"Expected 'Dataframe' type for dataaframe, got '{type(dataframe)}'")
        if not isinstance(unique_field, str):
            raise TypeError(f"Expected 'str' type for unique_field, got '{type(unique_field)}'")
        if not isinstance(name, str) and name is not None:
            raise TypeError(f"Expected 'str' or 'None' for name, got '{type(name)}'")
        if unique_field not in dataframe.columns:
            raise ValueError(f"'{unique_field}' not in dataframe")

    @property
    def df(self):
        """

        :return: The geodataframe the dataset is based on
        :rtype: ~geopandas.GeoDataFrame
        """
        return self._df

    @property
    def unique_field(self):
        """

        :return: The field used to identify unique locations
        :rtype: str
        """
        return self._unique_field

    @property
    def name(self):
        """

        :return: The name of the dataset
        :rtype: str
        """
        return self._name


class DemandDataset(Dataset):
    def __init__(self, dataframe, unique_field, demand_field,  name=None):
        """
        The dataset representing the demand to be used when creating a model

        :param ~geopandas.GeoDataFrame dataframe: A geodataframe containing the spatial data
        :param str unique_field: A unique field/column name in the geodataframe
        :param str demand_field: The field representing the quantity of the demand for each location
        :param str name: An optional name for the dataset
        """
        super().__init__(dataframe, unique_field, name=name)
        if not isinstance(demand_field, str):
            raise TypeError(f"Expected 'str' type for demand_field, got '{type(demand_field)}'")
        self._demand_field = demand_field
        self._validate_demand_field()

    @property
    def demand_field(self):
        """

        :return: The field representing the quantity of the demand for each location
        :rtype: str
        """
        return self._demand_field

    def _validate_demand_field(self):
        if self._demand_field not in self.df.columns:
            raise ValueError(f"'{self._demand_field}' not in dataframe")
        if self.df[self._demand_field].dtype not in ['float64', 'int64']:
            raise TypeError(f"'{self._demand_field}' is not a numeric field in dataframe")


class SupplyDataset(Dataset):
    def __init__(self, dataframe, unique_field, name=None):
        """
        The dataset representing the supply to be used when creating a model

        :param ~geopandas.GeoDataFrame dataframe: A geodataframe containing the spatial data
        :param str unique_field: A unique field/column name in the geodataframe
        :param str name: An optional name for the dataset
        """
        super().__init__(dataframe, unique_field, name=name)