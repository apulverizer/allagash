import pandas as pd
import random
import string


class Coverage:
    def __init__(self, dataframe, demand_col=None, demand_name=None, supply_name=None, coverage_type="binary"):
        self._validate_init(coverage_type, dataframe, demand_col, demand_name, supply_name)
        self._demand_col = demand_col
        self._dataframe = dataframe
        if not demand_name:
            self._demand_name = ''.join(random.choices(string.ascii_uppercase, k=6))
        else:
            self._demand_name = demand_name
        if not supply_name:
            self._supply_name = ''.join(random.choices(string.ascii_uppercase, k=6))
        else:
            self._supply_name = supply_name
        self._coverage_type = coverage_type.lower()

    @staticmethod
    def _validate_init(coverage_type, dataframe, demand_col, demand_name, supply_name):
        if not isinstance(dataframe, pd.DataFrame):
            raise TypeError(f"Expected 'Dataframe' type for dataframe, got '{type(dataframe)}'")
        if not isinstance(demand_col, str) and demand_col is not None:
            raise TypeError(f"Expected 'str' type for demand_col, got '{type(demand_col)}'")
        if not isinstance(demand_name, str) and demand_name is not None:
            raise TypeError(f"Expected 'str' type for demand_name, got '{type(demand_name)}'")
        if not isinstance(supply_name, str) and supply_name is not None:
            raise TypeError(f"Expected 'str' type for supply_name, got '{type(supply_name)}'")
        if not isinstance(coverage_type, str):
            raise TypeError(f"Expected 'str' type for coverage_type, got '{type(coverage_type)}'")
        if demand_col and demand_col not in dataframe.columns:
            raise ValueError(f"'{demand_col}' not in dataframe")
        if coverage_type.lower() not in ("binary", "partial"):
            raise ValueError(f"Invalid coverage type '{coverage_type}'")
        if coverage_type.lower() == "partial" and demand_col is None:
            raise ValueError(f"'demand_col' is required when generating partial coverage")

    @property
    def df(self):
        return self._dataframe

    @property
    def demand_name(self):
        return self._demand_name

    @property
    def supply_name(self):
        return self._supply_name

    @property
    def coverage_type(self):
        return self._coverage_type

    @property
    def demand_col(self):
        return self._demand_col

    @classmethod
    def from_geodataframes(cls, demand_df, supply_df, demand_id_col, supply_id_col, demand_name=None, supply_name=None, demand_col=None, coverage_type="binary"):
        cls._validate_from_geodataframes(coverage_type, demand_col, demand_df, demand_id_col, demand_name, supply_df,
                                         supply_id_col)

        data = []
        if coverage_type.lower() == 'binary':
            for index, row in demand_df.iterrows():
                contains = supply_df.geometry.contains(row.geometry).tolist()
                if demand_col:
                    contains.insert(0, row[demand_col])
                data.append(contains)
        elif coverage_type.lower() == 'partial':
            for index, row in demand_df.iterrows():
                demand_area = row.geometry.area
                intersection_area = supply_df.geometry.intersection(row.geometry).geometry.area
                partial_coverage = ((intersection_area / demand_area) * row[demand_col]).tolist()
                if demand_col:
                    partial_coverage.inset(0, row[demand_col])
                data.append(partial_coverage)
        else:
            raise ValueError(f"Invalid coverage type '{coverage_type}'")
        columns = supply_df[supply_id_col].tolist()
        if demand_col:
            columns.insert(0, demand_col)
        df = pd.DataFrame.from_records(data, index=demand_df[demand_id_col], columns=columns)
        return Coverage(df,
                        demand_col=demand_col,
                        demand_name=demand_name,
                        supply_name=supply_name,
                        coverage_type=coverage_type)

    @classmethod
    def _validate_from_geodataframes(cls, coverage_type, demand_col, demand_df, demand_id_col, demand_name, supply_df,
                                     supply_id_col):
        if not isinstance(demand_df, pd.DataFrame):
            raise TypeError(f"Expected 'Dataframe' type for demand_df, got '{type(demand_df)}'")
        if not isinstance(supply_df, pd.DataFrame):
            raise TypeError(f"Expected 'Dataframe' type for supply_df, got '{type(supply_df)}'")
        if not isinstance(demand_id_col, str):
            raise TypeError(f"Expected 'str' type for demand_id_col, got '{type(demand_id_col)}'")
        if not isinstance(supply_id_col, str):
            raise TypeError(f"Expected 'str' type for demand_id_col, got '{type(supply_id_col)}'")
        if not isinstance(demand_name, str) and demand_name is not None:
            raise TypeError(f"Expected 'str' type for demand_name, got '{type(demand_name)}'")
        if not isinstance(coverage_type, str):
            raise TypeError(f"Expected 'str' type for coverage_type, got '{type(coverage_type)}'")
        if demand_col and demand_col not in demand_df.columns:
            raise ValueError(f"'{demand_col}' not in dataframe")
        if coverage_type.lower() not in ("binary", "partial"):
            raise ValueError(f"Invalid coverage type '{coverage_type}'")
        if coverage_type.lower() == "partial" and demand_col is None:
            raise ValueError(f"'demand_col' is required when generating partial coverage")
