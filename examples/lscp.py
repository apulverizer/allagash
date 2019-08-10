from allagash.data import DemandDataset, SupplyDataset
from allagash.coverage.types import CoverageType
from allagash.coverage import Coverage
from allagash.models.types import ModelType
import pulp
import geopandas


if __name__ == "__main__":
    d = DemandDataset(geopandas.read_file("sample_data/demand_point.shp"), "block", "GEOID10", "Population")
    s = SupplyDataset(geopandas.read_file("sample_data/facility_service_areas.shp"), "facility1", "ORIG_ID")
    s2 = SupplyDataset(geopandas.read_file("sample_data/facility2_service_areas.shp"), "facility2", "ORIG_ID")
    coverage = Coverage(d, [s, s2], CoverageType.BINARY)
    model = coverage.create_model(ModelType.LSCP)
    solution = model.solve(pulp.GLPK(msg=0))
    selected_locations = solution.selected_supply(s)
    selected_locations2 = solution.selected_supply(s2)
    print(selected_locations)
    print(selected_locations2)
    covered_locations = solution.covered_demand
    print(covered_locations)
