from allagash.models import Model
from allagash.models import ModelType
from ..data import DemandDataset, SupplyDataset
from .types import CoverageType
import pandas as pd
import pulp


class Coverage:
    def __init__(self, demand_dataset: DemandDataset, supply_datasets: [SupplyDataset], coverage_type: CoverageType, delineator: str = "$"):
        self.demand_dataset = demand_dataset
        self.delineator = delineator
        if isinstance(supply_datasets, SupplyDataset):
            self.supply_datasets = [supply_datasets]
        else:
            self.supply_datasets = supply_datasets
        self.coverage_type = coverage_type
        if self.coverage_type == CoverageType.BINARY:
            self._generate_binary_coverage()
        pass

    def create_model(self, model_type: ModelType) -> Model:
        if model_type == ModelType.LSCP:
            return self._generate_lscp()

    def _generate_lscp(self) -> Model:
        demand_vars = {}
        for _, row in self.demand_dataset.df.iterrows():
            name = f"{self.demand_dataset.name}{self.delineator}{row[self.demand_dataset.unique_field]}"
            demand_vars[name] = pulp.LpVariable(name, 0, 1, pulp.LpInteger)

        supply_vars = {}
        for supply_dataset in self.supply_datasets:
            for _, row in supply_dataset.df.iterrows():
                name = f"{supply_dataset.name}{self.delineator}{row[supply_dataset.unique_field]}"
                supply_vars[name] = pulp.LpVariable(name, 0, 1, pulp.LpInteger)

        prob = pulp.LpProblem("LSCP", pulp.LpMinimize)
        to_sum = []
        for _, v in supply_vars.items():
            to_sum.append(v)
        prob += pulp.lpSum(to_sum)

        for _, demand in self.demand_dataset.df.iterrows():
            to_sum = []
            for supply, coverage in self._coverage.items():
                rows = coverage.loc[coverage[self.demand_dataset.unique_field] == demand[self.demand_dataset.unique_field]].T
                for i, row in rows.iloc[1:].iterrows():
                    if row.values[0] is True:
                        name = f"{supply.name}{self.delineator}{i}"
                        to_sum.append(supply_vars[name])
            if not to_sum:
                to_sum = [pulp.LpVariable(f"__dummy{self.delineator}{demand[self.demand_dataset.unique_field]}", 0, 0, pulp.LpInteger)]
            prob += pulp.lpSum(to_sum) >= 1, f"D{demand[self.demand_dataset.unique_field]}"
        prob.writeLP("test.lp")
        return Model(prob, self, ModelType.LSCP)

    def _generate_binary_coverage(self):
        self._coverage = {}
        for s in self.supply_datasets:
            df = pd.DataFrame(columns=s.df[s.unique_field])
            df.insert(0, self.demand_dataset.unique_field, value=None)

            data = []
            for _, row in self.demand_dataset.df.iterrows():
                contains = s.df.geometry.contains(row.geometry).tolist()
                r = [row[self.demand_dataset.unique_field]]
                r.extend(contains)
                data.append(r)
            columns = s.df[s.unique_field].tolist()
            columns.insert(0, self.demand_dataset.unique_field)
            df = pd.DataFrame.from_records(data, columns=columns)
            self._coverage[s] = df
