from . coverage import Coverage
from .types import CoverageType
from ..data import DemandDataset, SupplyDataset
import pandas as pd


def generate_coverage(demand_dataset: DemandDataset, supply_datasets: [SupplyDataset], coverage_type: CoverageType) -> Coverage:
    if coverage_type == CoverageType.BINARY:
        return _generate_binary_coverage(demand_dataset, supply_datasets)


def _generate_binary_coverage(demand_dataset: DemandDataset, supply_datasets: [SupplyDataset]) -> Coverage:
    d = {}
    for s in supply_datasets:
        df = pd.DataFrame(columns=s.df[s.unique_field])
        df.insert(0, demand_dataset.unique_field, value=None)

        data = []
        for _, row in demand_dataset.df.iterrows():
            contains = supply_datasets.df.geometry.contains(row.geometry).tolist()
            r = [row[demand_dataset.unique_field]]
            r.extend(contains)
            data.append(r)
        columns = supply_datasets.df[s.unique_field].tolist()
        columns.insert(0, demand_dataset.unique_field)
        df = pd.DataFrame.from_records(data, columns=columns)
        d[s]: df

    return Coverage(demand_dataset, supply_datasets, CoverageType.BINARY)

