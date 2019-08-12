from allagash.dataset import SupplyDataset
from allagash.model import Model, ModelType
import pandas as pd
import pulp
from enum import Enum


class CoverageType(Enum):
    BINARY = 0
    PARTIAL = 1
    TRAUMAH = 2


class Coverage:
    def __init__(self, demand_dataset, supply_datasets, coverage_type, delineator="$", generate_coverage=True):
        self.demand_dataset = demand_dataset
        self.delineator = delineator
        self._coverage = {}
        if isinstance(supply_datasets, SupplyDataset):
            self.supply_datasets = [supply_datasets]
        else:
            self.supply_datasets = supply_datasets
        self.coverage_type = coverage_type
        if generate_coverage:
            if self.coverage_type == CoverageType.BINARY:
                self._generate_binary_coverage()
            elif self.coverage_type == CoverageType.PARTIAL:
                self._generate_partial_coverage()

    @staticmethod
    def from_existing_dataframes(demand_dataset, supply_coverage_mapping, coverage_type, delineator="$"):
        c = Coverage(demand_dataset, [], coverage_type, delineator=delineator, generate_coverage=False)
        for supply_dataset, dataframe in supply_coverage_mapping.items():
            c.supply_datasets.append(supply_dataset)
            c._coverage[supply_dataset] = dataframe
        return c

    def create_model(self, model_type, **kwargs):
        if model_type == ModelType.LSCP:
            return self._generate_lscp(**kwargs)
        elif model_type == ModelType.MCLP:
            return self._generate_mclp(**kwargs)

    def _generate_lscp(self, **kwargs):
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
        return Model(prob, self, ModelType.LSCP)

    def _generate_mclp(self, **kwargs):
        max_supply = kwargs['max_supply']
        demand_vars = {}
        for _, row in self.demand_dataset.df.iterrows():
            name = f"{self.demand_dataset.name}{self.delineator}{row[self.demand_dataset.unique_field]}"
            demand_vars[name] = pulp.LpVariable(name, 0, 1, pulp.LpInteger)

        supply_vars = {}
        for supply_dataset in self.supply_datasets:
            for _, row in supply_dataset.df.iterrows():
                name = f"{supply_dataset.name}{self.delineator}{row[supply_dataset.unique_field]}"
                supply_vars[name] = pulp.LpVariable(name, 0, 1, pulp.LpInteger)

        # add objective
        prob = pulp.LpProblem("MCLP", pulp.LpMaximize)
        to_sum = []
        for _, demand_var in demand_vars.items():
            d = demand_var.name.split(self.delineator)[1]
            query = f"{self.demand_dataset.unique_field} == '{d}'"
            v = self.demand_dataset.df.query(query)[self.demand_dataset._demand_field].tolist()[0]
            to_sum.append(v * demand_var)
        prob += pulp.lpSum(to_sum)

        # add coverage constraints
        for _, demand in self.demand_dataset.df.iterrows():
            to_sum = []
            for supply, coverage in self._coverage.items():
                rows = coverage.loc[
                    coverage[self.demand_dataset.unique_field] == demand[self.demand_dataset.unique_field]].T
                for i, row in rows.iloc[1:].iterrows():
                    if row.values[0] is True:
                        name = f"{supply.name}{self.delineator}{i}"
                        to_sum.append(supply_vars[name])
            demand_name = f"{self.demand_dataset.name}{self.delineator}{demand[self.demand_dataset.unique_field]}"
            prob += pulp.lpSum(to_sum) - demand_vars[demand_name] >= 0, f"D{demand[self.demand_dataset.unique_field]}"

        # Number of supply locations
        for supply_dataset in self.supply_datasets:
            to_sum = []
            for _, row in supply_dataset.df.iterrows():
                name = f"{supply_dataset.name}{self.delineator}{row[supply_dataset.unique_field]}"
                to_sum.append(supply_vars[name])
            prob += pulp.lpSum(to_sum) <= max_supply[supply_dataset], f"Num{self.delineator}{supply_dataset.name}"
        return Model(prob, self, ModelType.MCLP)

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

    def _generate_partial_coverage(self):
        self._coverage = {}
        for s in self.supply_datasets:
            df = pd.DataFrame(columns=s.df[s.unique_field])
            df.insert(0, self.demand_dataset.unique_field, value=None)

            data = []
            for _, row in self.demand_dataset.df.iterrows():
                demand_area = row.geometry.area
                intersection_area = s.df.geometry.intersection(row.geometry).geometry.area
                partial_coverage = ((intersection_area / demand_area) * row[self.demand_dataset._demand_field]).tolist()
                r = [row[self.demand_dataset.unique_field]]
                r.extend(partial_coverage)
                data.append(r)
            columns = s.df[s.unique_field].tolist()
            columns.insert(0, self.demand_dataset.unique_field)
            df = pd.DataFrame.from_records(data, columns=columns)
            self._coverage[s] = df
