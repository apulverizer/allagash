from allagash.dataset import SupplyDataset
from allagash.model import Model
import pandas as pd
import pulp


class Coverage:
    def __init__(self, demand_dataset=None, supply_datasets=None, coverage_type='binary', **kwargs):
        self._demand_dataset = demand_dataset
        self._coverage = {}
        if isinstance(supply_datasets, SupplyDataset):
            self._supply_datasets = [supply_datasets]
        else:
            self._supply_datasets = supply_datasets
        self.coverage_type = coverage_type.lower()
        if kwargs.get('build_coverage', True):
            if self.coverage_type == 'binary':
                self._generate_binary_coverage()
            elif self.coverage_type == 'partial':
                self._generate_partial_coverage()
            else:
                raise ValueError(f"Invalid coverage type: '{coverage_type}'")

    @property
    def demand_dataset(self):
        return self._demand_dataset

    @property
    def supply_datasets(self):
        return self._supply_datasets

    @property
    def coverage(self):
        return self._coverage

    @classmethod
    def from_coverage_matrices(cls, demand_dataset, supply_coverage_mapping, coverage_type):
        c = cls(demand_dataset, coverage_type=coverage_type, build_coverage=False)
        for supply_dataset, dataframe in supply_coverage_mapping.items():
            c._supply_datasets.append(supply_dataset)
            c._coverage[supply_dataset] = dataframe
        return c

    def create_model(self, model_type, **kwargs):
        if model_type == 'lscp':
            return self._generate_lscp(**kwargs)
        elif model_type == 'mclp':
            return self._generate_mclp(**kwargs)
        else:
            raise ValueError(f"Invalid model type: '{model_type}'")

    def _generate_lscp(self, delineator="$"):
        demand_vars = {}
        for _, row in self._demand_dataset.df.iterrows():
            name = f"{self._demand_dataset.name}{delineator}{row[self._demand_dataset.unique_field]}"
            demand_vars[name] = pulp.LpVariable(name, 0, 1, pulp.LpInteger)

        supply_vars = {}
        for supply_dataset in self._supply_datasets:
            for _, row in supply_dataset.df.iterrows():
                name = f"{supply_dataset.name}{delineator}{row[supply_dataset.unique_field]}"
                supply_vars[name] = pulp.LpVariable(name, 0, 1, pulp.LpInteger)

        prob = pulp.LpProblem("LSCP", pulp.LpMinimize)
        to_sum = []
        for _, v in supply_vars.items():
            to_sum.append(v)
        prob += pulp.lpSum(to_sum)

        for _, demand in self._demand_dataset.df.iterrows():
            to_sum = []
            for supply, coverage in self._coverage.items():
                rows = coverage.loc[coverage[self._demand_dataset.unique_field] == demand[self._demand_dataset.unique_field]].T
                for i, row in rows.iloc[1:].iterrows():
                    if row.values[0] is True:
                        name = f"{supply.name}{delineator}{i}"
                        to_sum.append(supply_vars[name])
            if not to_sum:
                to_sum = [pulp.LpVariable(f"__dummy{delineator}{demand[self._demand_dataset.unique_field]}", 0, 0, pulp.LpInteger)]
            prob += pulp.lpSum(to_sum) >= 1, f"D{demand[self._demand_dataset.unique_field]}"
        return Model(prob, self, 'lscp', delineator=delineator)

    def _generate_mclp(self, delineator="$", **kwargs):
        max_supply = kwargs['max_supply']
        demand_vars = {}
        for _, row in self._demand_dataset.df.iterrows():
            name = f"{self._demand_dataset.name}{delineator}{row[self._demand_dataset.unique_field]}"
            demand_vars[name] = pulp.LpVariable(name, 0, 1, pulp.LpInteger)

        supply_vars = {}
        for supply_dataset in self._supply_datasets:
            for _, row in supply_dataset.df.iterrows():
                name = f"{supply_dataset.name}{delineator}{row[supply_dataset.unique_field]}"
                supply_vars[name] = pulp.LpVariable(name, 0, 1, pulp.LpInteger)

        # add objective
        prob = pulp.LpProblem("MCLP", pulp.LpMaximize)
        to_sum = []
        for _, demand_var in demand_vars.items():
            d = demand_var.name.split(delineator)[1]
            query = f"{self._demand_dataset.unique_field} == '{d}'"
            v = self._demand_dataset.df.query(query)[self.demand_dataset.demand_field].tolist()[0]
            to_sum.append(v * demand_var)
        prob += pulp.lpSum(to_sum)

        # add coverage constraints
        for _, demand in self._demand_dataset.df.iterrows():
            to_sum = []
            for supply, coverage in self._coverage.items():
                rows = coverage.loc[
                    coverage[self._demand_dataset.unique_field] == demand[self._demand_dataset.unique_field]].T
                for i, row in rows.iloc[1:].iterrows():
                    if row.values[0] is True:
                        name = f"{supply.name}{delineator}{i}"
                        to_sum.append(supply_vars[name])
            demand_name = f"{self._demand_dataset.name}{delineator}{demand[self._demand_dataset.unique_field]}"
            prob += pulp.lpSum(to_sum) - demand_vars[demand_name] >= 0, f"D{demand[self._demand_dataset.unique_field]}"

        # Number of supply locations
        for supply_dataset in self._supply_datasets:
            to_sum = []
            for _, row in supply_dataset.df.iterrows():
                name = f"{supply_dataset.name}{delineator}{row[supply_dataset.unique_field]}"
                to_sum.append(supply_vars[name])
            prob += pulp.lpSum(to_sum) <= max_supply[supply_dataset], f"Num{delineator}{supply_dataset.name}"
        return Model(prob, self, 'mclp', delineator=delineator)

    def _generate_binary_coverage(self):
        self._coverage = {}
        for s in self._supply_datasets:
            df = pd.DataFrame(columns=s.df[s.unique_field])
            df.insert(0, self._demand_dataset.unique_field, value=None)

            data = []
            for _, row in self._demand_dataset.df.iterrows():
                contains = s.df.geometry.contains(row.geometry).tolist()
                r = [row[self._demand_dataset.unique_field]]
                r.extend(contains)
                data.append(r)
            columns = s.df[s.unique_field].tolist()
            columns.insert(0, self._demand_dataset.unique_field)
            df = pd.DataFrame.from_records(data, columns=columns)
            self._coverage[s] = df

    def _generate_partial_coverage(self):
        self._coverage = {}
        for s in self._supply_datasets:
            df = pd.DataFrame(columns=s.df[s.unique_field])
            df.insert(0, self._demand_dataset.unique_field, value=None)

            data = []
            for _, row in self._demand_dataset.df.iterrows():
                demand_area = row.geometry.area
                intersection_area = s.df.geometry.intersection(row.geometry).geometry.area
                partial_coverage = ((intersection_area / demand_area) * row[self.demand_dataset.demand_field]).tolist()
                r = [row[self._demand_dataset.unique_field]]
                r.extend(partial_coverage)
                data.append(r)
            columns = s.df[s.unique_field].tolist()
            columns.insert(0, self._demand_dataset.unique_field)
            df = pd.DataFrame.from_records(data, columns=columns)
            self._coverage[s] = df
