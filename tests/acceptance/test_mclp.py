import math
import os
import geopandas
import pulp
from allagash.coverage import Coverage
from allagash.problem import Problem


class TestMCLP:
    dir_name = os.path.dirname(__file__)

    def test_single_supply(self):
        demand_id_col = "GEOID10"
        supply_id_col = "ORIG_ID"
        demand_col = "Population"
        d = geopandas.read_file(
            os.path.join(self.dir_name, "../test_data/demand_point.shp")
        )
        s = geopandas.read_file(
            os.path.join(self.dir_name, "../test_data/facility_service_areas.shp")
        )
        coverage = Coverage.from_geodataframes(
            d, s, demand_id_col, supply_id_col, demand_col=demand_col
        )
        problem = Problem.mclp(coverage, max_supply={coverage: 5})
        problem.solve(pulp.GLPK())
        covered_demand = d.query(
            f"{demand_id_col} in ({[f'{i}' for i in problem.selected_demand(coverage)]})"
        )
        result = math.ceil(
            (covered_demand[demand_col].sum() / d[demand_col].sum()) * 100
        )
        assert result == 53

    def test_multiple_supply(self):
        demand_id_col = "GEOID10"
        supply_id_col = "ORIG_ID"
        demand_col = "Population"
        d = geopandas.read_file(
            os.path.join(self.dir_name, "../test_data/demand_point.shp")
        )
        s = geopandas.read_file(
            os.path.join(self.dir_name, "../test_data/facility_service_areas.shp")
        )
        s2 = geopandas.read_file(
            os.path.join(self.dir_name, "../test_data/facility2_service_areas.shp")
        )
        coverage = Coverage.from_geodataframes(
            d, s, demand_id_col, supply_id_col, demand_col=demand_col
        )
        coverage2 = Coverage.from_geodataframes(
            d,
            s2,
            demand_id_col,
            supply_id_col,
            demand_col=demand_col,
            demand_name=coverage.demand_name,
        )
        problem = Problem.mclp(
            [coverage, coverage2], max_supply={coverage: 5, coverage2: 10}
        )
        problem.solve(pulp.GLPK())
        selected_locations = problem.selected_supply(coverage)
        selected_locations2 = problem.selected_supply(coverage2)
        covered_demand = d.query(
            f"{demand_id_col} in ({[f'{i}' for i in problem.selected_demand(coverage)]})"
        )
        result = math.ceil(
            (covered_demand[demand_col].sum() / d[demand_col].sum()) * 100
        )
        assert len(selected_locations) == 5
        assert len(selected_locations2) == 10
        assert result == 96
