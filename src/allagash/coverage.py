import pandas as pd
import random
import string


class Coverage:
    def __init__(self, dataframe, demand_col=None, demand_name=None, supply_name=None, coverage_type="binary"):
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
        self._coverage_type = coverage_type

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
