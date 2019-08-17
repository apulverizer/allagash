from pandas.api.types import is_string_dtype
import operator


class Solution:
    def __init__(self, model):
        self._model = model
        self._problem = model.problem
        self._coverage = model.coverage

    @property
    def model(self):
        return self._model

    def selected_supply(self, supply_dataset, operation=operator.eq, value=1, output_type='dataframe'):
        ids = []
        for var in self._problem.variables():
            if var.name.split(self._model.delineator)[0] == supply_dataset.name:
                if operation(var.varValue, value):
                    ids.append(var.name.split(self._model.delineator)[1])
        if output_type == 'list':
            return ids
        if is_string_dtype(supply_dataset.df[supply_dataset.unique_field]):
            query = f"""{supply_dataset.unique_field} in ({','.join([f"'{i}'" for i in ids])})"""
        else:
            query = f"{supply_dataset.unique_field} in ({','.join(ids)})"
        return supply_dataset.df.query(query, inplace=False)

    @property
    def covered_demand(self):
        if self._model.model_type == 'lscp':
            return self._coverage.demand_dataset.df.copy(deep=True)
        elif self._model.model_type == 'mclp':
            ids = []
            for var in self._problem.variables():
                if var.name.split(self._model.delineator)[0] == self._model.coverage.demand_dataset.name:
                    if var.varValue >= 1:
                        ids.append(var.name.split(self._model.delineator)[1])
            if is_string_dtype(self._model.coverage.demand_dataset.df[self._model.coverage.demand_dataset.unique_field]):
                query = f"""{self._model.coverage.demand_dataset.unique_field} in ({','.join([f"'{i}'" for i in ids])})"""
            else:
                query = f"{self._model.coverage.demand_dataset.unique_field} in ({','.join(ids)})"
            return self._model.coverage.demand_dataset.df.query(query, inplace=False)
