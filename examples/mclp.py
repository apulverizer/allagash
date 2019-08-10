from allagash.dataset import SupplyDataset, DemandDataset
from allagash.coverage import Coverage, CoverageType
from allagash.model import ModelType
import pulp
import geopandas


if __name__ == "__main__":
    d = DemandDataset(geopandas.read_file("sample_data/demand_point.shp"), "GEOID10", "Population")
    s = SupplyDataset(geopandas.read_file("sample_data/facility_service_areas.shp"), "ORIG_ID")
    s2 = SupplyDataset(geopandas.read_file("sample_data/facility2_service_areas.shp"), "ORIG_ID")
    coverage = Coverage(d, [s, s2], CoverageType.BINARY)
    model = coverage.create_model(ModelType.MCLP, max_supply={s: 7, s2: 15})
    solution = model.solve(pulp.GLPK(msg=0))
    selected_locations = solution.selected_supply(s)
    selected_locations2 = solution.selected_supply(s2)
    covered_locations = solution.covered_demand
    print(f'{(covered_locations["Population"].sum() / d.df["Population"].sum()*100):0.2f}')
