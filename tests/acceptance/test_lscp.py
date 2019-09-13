import math
import os
import arcgis
import geopandas
import pulp
import pytest
from allagash.coverage import Coverage
from allagash.problem import Problem, InfeasibleException, UndefinedException


class TestLSCP:
    dir_name = os.path.dirname(__file__)

    def test_single_supply(self):
        demand_id_col = "GEOID10"
        supply_id_col = "ORIG_ID"
        d = geopandas.read_file(os.path.join(self.dir_name, "../test_data/demand_point.shp"))
        s = geopandas.read_file(os.path.join(self.dir_name, "../test_data/facility_service_areas.shp"))
        coverage = Coverage.from_geodataframes(d, s, demand_id_col, supply_id_col)
        problem = Problem.lscp(coverage)
        with pytest.raises((InfeasibleException, UndefinedException)) as e:
            problem.solve(pulp.GLPK())

    def test_single_supply_arcgis(self):
        demand_id_col = "GEOID10"
        supply_id_col = "ORIG_ID"
        d = arcgis.GeoAccessor.from_featureclass(os.path.join(self.dir_name, "../test_data/demand_point.shp"))
        s = arcgis.GeoAccessor.from_featureclass(os.path.join(self.dir_name, "../test_data/facility_service_areas.shp"))
        coverage = Coverage.from_spatially_enabled_dataframes(d, s, demand_id_col, supply_id_col)
        problem = Problem.lscp(coverage)
        with pytest.raises((InfeasibleException, UndefinedException)) as e:
            problem.solve(pulp.GLPK())

    def test_multiple_supply(self):
        demand_col = "Population"
        demand_id_col = "GEOID10"
        supply_id_col = "ORIG_ID"
        d = geopandas.read_file(os.path.join(self.dir_name, "../test_data/demand_point.shp"))
        s = geopandas.read_file(os.path.join(self.dir_name, "../test_data/facility_service_areas.shp"))
        s2 = geopandas.read_file(os.path.join(self.dir_name, "../test_data/facility2_service_areas.shp"))
        coverage = Coverage.from_geodataframes(d, s, demand_id_col, supply_id_col, demand_col=demand_col)
        coverage2 = Coverage.from_geodataframes(d, s2, demand_id_col, supply_id_col, demand_name=coverage.demand_name, demand_col=demand_col)
        problem = Problem.lscp([coverage, coverage2])
        problem.solve(pulp.GLPK())
        selected_locations = problem.selected_supply(coverage)
        selected_locations2 = problem.selected_supply(coverage2)
        covered_demand = d.query(f"{demand_id_col} in ({[f'{i}' for i in problem.selected_demand(coverage)]})")
        coverage = math.ceil((covered_demand[demand_col].sum() / d[demand_col].sum()) * 100)
        assert(len(selected_locations) >= 5)
        assert(len(selected_locations2) >= 17)
        assert(coverage == 100)

    def test_multiple_supply_arcgis(self):
        demand_col = "Population"
        demand_id_col = "GEOID10"
        supply_id_col = "ORIG_ID"
        d = arcgis.GeoAccessor.from_featureclass(os.path.join(self.dir_name, "../test_data/demand_point.shp"))
        s = arcgis.GeoAccessor.from_featureclass(os.path.join(self.dir_name, "../test_data/facility_service_areas.shp"))
        s2 = arcgis.GeoAccessor.from_featureclass(os.path.join(self.dir_name, "../test_data/facility2_service_areas.shp"))
        coverage = Coverage.from_spatially_enabled_dataframes(d, s, demand_id_col, supply_id_col, demand_col=demand_col)
        coverage2 = Coverage.from_spatially_enabled_dataframes(d, s2, demand_id_col, supply_id_col, demand_name=coverage.demand_name, demand_col=demand_col)
        problem = Problem.lscp([coverage, coverage2])
        problem.solve(pulp.GLPK())
        selected_locations = problem.selected_supply(coverage)
        selected_locations2 = problem.selected_supply(coverage2)
        covered_demand = d.query(f"{demand_id_col} in ({[f'{i}' for i in problem.selected_demand(coverage)]})")
        coverage = math.ceil((covered_demand[demand_col].sum() / d[demand_col].sum()) * 100)
        assert(len(selected_locations) >= 5)
        assert(len(selected_locations2) >= 17)
        assert(coverage == 100)
