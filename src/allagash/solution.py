from pandas.api.types import is_string_dtype
import operator
from allagash.model import Model
from allagash.dataset import SupplyDataset


class Solution:
    def __init__(self, model):
        if not isinstance(model, Model):
            raise TypeError(f"Expected 'Model' type for model, got '{type(model)}'")
        self._model = model
        self._problem = model.problem
        self._coverage = model.coverage

    @property
    def model(self):
        return self._model

    def selected_supply(self, supply_dataset, operation=operator.eq, value=1, output_format='dataframe'):
        if not isinstance(supply_dataset, SupplyDataset):
            raise TypeError(f"Expected 'SupplyDataset' type for supply_dataset, got '{type(supply_dataset)}'")
        if not callable(operation):
            raise TypeError(f"Expected callable for operation, got '{type(operation)}'")
        if not isinstance(value, (int, float)):
            raise TypeError(f"Expected 'int' or 'float' for value, got '{type(value)}'")
        if not isinstance(output_format, str):
            raise TypeError(f"Expected 'str' for output_format, got '{type(output_format)}'")
        if output_format.lower() not in ['dataframe', 'list']:
            raise ValueError(f"Invalid output_format: '{output_format}'")
        ids = []
        for var in self._problem.variables():
            if var.name.split(self._model.delineator)[0] == supply_dataset.name:
                if operation(var.varValue, value):
                    ids.append(var.name.split(self._model.delineator)[1])
        if output_format == 'list':
            return ids
        if is_string_dtype(supply_dataset.df[supply_dataset.unique_field]):
            query = f"""{supply_dataset.unique_field} in ({','.join([f"'{i}'" for i in ids])})"""
        else:
            query = f"{supply_dataset.unique_field} in ({','.join(ids)})"
        return supply_dataset.df.query(query, inplace=False)

    def covered_demand(self, output_format='dataframe'):
        if not isinstance(output_format, str):
            raise TypeError(f"Expected 'str' for output_format, got '{type(output_format)}'")
        if output_format.lower() not in ['dataframe', 'list']:
            raise ValueError(f"Invalid output_format: '{output_format}'")
        if self._model.model_type == 'lscp':
            ids = self._model.coverage.demand_dataset.df[self._model.coverage.demand_dataset.unique_field].tolist()
        else:
            ids = []
            for var in self._problem.variables():
                if var.name.split(self._model.delineator)[0] == self._model.coverage.demand_dataset.name:
                    if var.varValue >= 1:
                        ids.append(var.name.split(self._model.delineator)[1])
        if output_format == 'list':
            return ids
        if is_string_dtype(self._model.coverage.demand_dataset.df[self._model.coverage.demand_dataset.unique_field]):
            query = f"""{self._model.coverage.demand_dataset.unique_field} in ({','.join([f"'{i}'" for i in ids])})"""
        else:
            query = f"{self._model.coverage.demand_dataset.unique_field} in ({','.join(ids)})"
        return self._model.coverage.demand_dataset.df.query(query, inplace=False)
