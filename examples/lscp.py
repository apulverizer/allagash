from allagash.data import DemandDataset, SupplyDataset
from allagash.coverage import generate_coverage
from allagash.coverage.types import CoverageType
from allagash.models.types import ModelType
import pulp


if __name__ == "__main__":
    d = DemandDataset("sample_data/demand_point.shp", "GEOID10", "Population")
    s = SupplyDataset("sample_data/facility.shp", "ID")
    coverage = generate_coverage(d, [s], CoverageType.BINARY)
    model = coverage.create_model(ModelType.LSCP)
    solution = model.solve(pulp.GLPK())
    percent_covered = solution.covered_demand
    selected_locations = solution.selected_supply(s)
    covered_locations = solution.selected_demand(d)
