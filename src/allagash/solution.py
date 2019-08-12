from allagash.model import ModelType
from pandas.api.types import is_string_dtype
import operator


class Solution:
    def __init__(self, model):
        self.model = model
        self._problem = model.problem
        self._coverage = model.coverage

    def selected_supply(self, supply_dataset, operation=operator.eq, value=1):
        ids = []
        for var in self._problem.variables():
            if var.name.split(self._coverage.delineator)[0] == supply_dataset.name:
                if operation(var.varValue, value):
                    ids.append(var.name.split(self._coverage.delineator)[1])
        if is_string_dtype(supply_dataset.df[supply_dataset.unique_field]):
            query = f"""{supply_dataset.unique_field} in ({','.join([f"'{i}'" for i in ids])})"""
        else:
            query = f"{supply_dataset.unique_field} in ({','.join(ids)})"
        return supply_dataset.df.query(query, inplace=False)

    @property
    def covered_demand(self):
        if self.model.model_type == ModelType.LSCP:
            return self._coverage.demand_dataset.df.copy(deep=True)
        elif self.model.model_type == ModelType.MCLP:
            ids = []
            for var in self._problem.variables():
                if var.name.split(self._coverage.delineator)[0] == self.model.coverage.demand_dataset.name:
                    if var.varValue >= 1:
                        ids.append(var.name.split(self._coverage.delineator)[1])
            if is_string_dtype(self.model.coverage.demand_dataset.df[self.model.coverage.demand_dataset.unique_field]):
                query = f"""{self.model.coverage.demand_dataset.unique_field} in ({','.join([f"'{i}'" for i in ids])})"""
            else:
                query = f"{self.model.coverage.demand_dataset.unique_field} in ({','.join(ids)})"
            return self.model.coverage.demand_dataset.df.query(query, inplace=False)
