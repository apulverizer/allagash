from allagash.dataset import SupplyDataset, DemandDataset
from allagash.model import Model
import pandas as pd
import pulp


class Coverage:
    def __init__(self, demand_dataset, supply_datasets=None, coverage_type='binary', **kwargs):
        """
        A representation of the spatial relationship between a :class:`~allagash.dataset.DemandDataset` and
        one or more :class:`~allagash.dataset.SupplyDataset`

        :param ~allagash.dataset.DemandDataset demand_dataset: A :class:`~allagash.dataset.DemandDataset` representing the locations that should be covered.
        :param list supply_datasets: A list of :class:`~allagash.dataset.SupplyDataset` representing the locations that can cover the demand
        :param str coverage_type: The type of coverage to generate. Options are a either `binary` or `partial`
        """
        self._validate(demand_dataset, supply_datasets, coverage_type, **kwargs)
        self._demand_dataset = demand_dataset
        self._coverage = {}
        if isinstance(supply_datasets, SupplyDataset):
            self._supply_datasets = [supply_datasets]
        elif supply_datasets is None:
            self._supply_datasets = []
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

    @staticmethod
    def _validate(demand_dataset, supply_datasets, coverage_type, **kwargs):
        if not isinstance(demand_dataset, DemandDataset):
            raise TypeError(f"Expected 'DemandDataset' type for demand_dataset, got '{type(demand_dataset)}'")
        if not isinstance(supply_datasets, (list, SupplyDataset)) and supply_datasets is not None :
            raise TypeError(f"Expected 'SupplyDataset' or 'list' type for supply_datasets, got '{type(supply_datasets)}'")
        if not isinstance(coverage_type, str) and coverage_type is not None:
            raise TypeError(f"Expected 'str' or 'None' for coverage_type, got '{type(coverage_type)}'")

    @property
    def demand_dataset(self):
        """

        :return: The demand dataset used in the coverage
        :rtype: ~allagash.dataset.DemandDataset
        """
        return self._demand_dataset

    @property
    def supply_datasets(self):
        """

        :return: The list of supply datasets used in the coverage
        :rtype: list
        """
        return self._supply_datasets

    @classmethod
    def from_coverage_dataframe(cls, demand_dataset, supply_coverage_mapping, coverage_type='binary'):
        """
        Creates a :class:`~allagash.coverage.Coverage` from one or more existing :class:`~pandas.DataFrame` representing a coverage matrix.
        Columns represent each supply location. Rows represent each demand location. The cell value represents if or how much of that demand location is covered by the supply location.

        :param ~allagash.dataset.DemandDataset demand_dataset: A dataset representing the locations that should be covered
        :param dict supply_coverage_mapping: A dictionary where each key represents a :class:`~allagash.dataset.SupplyDataset` and each value is a :class:`~pandas.DataFrame`
        :param str coverage_type: The type of coverage to generate. Options are either `binary` or `partial`
        :return: A new coverage object
        :rtype: ~allagash.coverage.Coverage
        """
        c = cls(demand_dataset, coverage_type=coverage_type, build_coverage=False)
        for supply_dataset, dataframe in supply_coverage_mapping.items():
            c._supply_datasets.append(supply_dataset)
            c._coverage[supply_dataset] = dataframe
        return c

    def create_model(self, model_type, delineator="$", **kwargs):
        """
        Creates a :class:`~allagash.model.Model` from the coverage. This model can then be solved.

        :param str model_type: The type of model to build. Options are either `mclp` or `lscp`
        :param str delineator: A string used to split a variable in the model into two sections for parsing
        :param kwargs: Additional parameters determined by the type of model being created
        :return: A model based on the coverage that can be solved
        :rtype: ~allagash.model.Model
        """
        if model_type == 'lscp':
            return Model(self._generate_lscp_problem(delineator), self, model_type, delineator)
        elif model_type == 'mclp':
            return Model(self._generate_mclp_problem(delineator, **kwargs), self, model_type, delineator)
        else:
            raise ValueError(f"Invalid model_type: '{model_type}'")

    def _generate_lscp_problem(self, delineator="$"):
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
                rows = coverage.loc[
                    coverage[self._demand_dataset.unique_field] == demand[self._demand_dataset.unique_field]].T
                for i, row in rows.iloc[1:].iterrows():
                    if row.values[0] is True:
                        name = f"{supply.name}{delineator}{i}"
                        to_sum.append(supply_vars[name])
            if not to_sum:
                to_sum = [pulp.LpVariable(f"__dummy{delineator}{demand[self._demand_dataset.unique_field]}", 0, 0,
                                          pulp.LpInteger)]
            prob += pulp.lpSum(to_sum) >= 1, f"D{demand[self._demand_dataset.unique_field]}"
        return prob

    def _generate_mclp_problem(self, delineator="$", **kwargs):
        max_supply = kwargs.get('max_supply', None)
        if max_supply is None:
            raise ValueError("'max_supply' is required")
        if not isinstance(max_supply, dict):
            raise TypeError(f"Expected 'dict' type for max_supply, got '{type(max_supply)}'")
        if len(max_supply.keys()) <= 0:
            raise ValueError("'max_supply' must contain at least one key/value pair")
        for key, value in max_supply.items():
            if not isinstance(key, SupplyDataset):
                raise TypeError(f"Expected 'SupplyDataset' type for max_supply key, got '{type(key)}'")
            if not isinstance(value, int):
                raise TypeError(f"Expected 'int' type for max_supply value, got '{type(value)}'")
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
        return prob

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
