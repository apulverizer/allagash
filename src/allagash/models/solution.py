from .. data import SupplyDataset
import operator
from pandas.api.types import is_string_dtype
from pulp import LpProblem
import pandas as pd


class Solution:
    def __init__(self, problem: LpProblem, coverage: 'Coverage'):
        self._problem = problem
        self._coverage = coverage


class LSCPSolution(Solution):
    def __init__(self, problem, coverage):
        super().__init__(problem, coverage)

    def selected_supply(self, supply_dataset: SupplyDataset, operation: operator = operator.eq, value: int = 1) -> pd.DataFrame:
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
    def covered_demand(self) -> pd.DataFrame:
        return self._coverage.demand_dataset.df.copy(deep=True)
