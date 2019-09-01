from allagash.coverage import Coverage
from allagash.solution import InfeasibleException, UndefinedException
from allagash.model import Model
import pulp
import geopandas
import math
import os
import pytest


class TestLSCP:
    dir_name = os.path.dirname(__file__)

    def test_single_supply(self):
        demand_id_col = "GEOID10"
        supply_id_col = "ORIG_ID"
        d = geopandas.read_file(os.path.join(self.dir_name, "../test_data/demand_point.shp"))
        s = geopandas.read_file(os.path.join(self.dir_name, "../test_data/facility_service_areas.shp"))
        coverage = Coverage.from_geodataframes(d, s, demand_id_col, supply_id_col)
        model = Model.lscp(coverage)
        with pytest.raises((InfeasibleException, UndefinedException)) as e:
            model.solve(pulp.GLPK())

    def test_multiple_supply(self):
        demand_col = "Population"
        demand_id_col = "GEOID10"
        supply_id_col = "ORIG_ID"
        d = geopandas.read_file(os.path.join(self.dir_name, "../test_data/demand_point.shp"))
        s = geopandas.read_file(os.path.join(self.dir_name, "../test_data/facility_service_areas.shp"))
        s2 = geopandas.read_file(os.path.join(self.dir_name, "../test_data/facility2_service_areas.shp"))
        coverage = Coverage.from_geodataframes(d, s, demand_id_col, supply_id_col, demand_col=demand_col)
        coverage2 = Coverage.from_geodataframes(d, s2, demand_id_col, supply_id_col, demand_name=coverage.demand_name, demand_col=demand_col)
        model = Model.lscp([coverage, coverage2])
        solution = model.solve(pulp.GLPK())
        selected_locations = solution.selected_supply(coverage.supply_name)
        selected_locations2 = solution.selected_supply(coverage2.supply_name)
        covered_demand = d.query(f"{demand_id_col} in ({[f'{i}' for i in solution.covered_demand(coverage.demand_name)]})")
        coverage = math.ceil((covered_demand[demand_col].sum() / d[demand_col].sum()) * 100)
        assert(len(selected_locations) == 5)
        assert(len(selected_locations2) == 19)
        assert(coverage == 100)
