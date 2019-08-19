from allagash.dataset import DemandDataset, SupplyDataset
from allagash.coverage import Coverage
from allagash.model import InfeasibleException, UndefinedException
import pulp
import geopandas
import math
import os
import pytest


class TestLSCP:
    dir_name = os.path.dirname(__file__)

    def test_single_supply(self):
        d = DemandDataset(geopandas.read_file(os.path.join(self.dir_name, "../test_data/demand_point.shp")), "GEOID10", "Population")
        s = SupplyDataset(geopandas.read_file(os.path.join(self.dir_name, "../test_data/facility_service_areas.shp")), "ORIG_ID")
        coverage = Coverage(d, s, 'binary')
        model = coverage.create_model('lscp')
        with pytest.raises((InfeasibleException, UndefinedException)) as e:
            model.solve(pulp.GLPK())

    def test_multiple_supply(self):
        d = DemandDataset(geopandas.read_file(os.path.join(self.dir_name, "../test_data/demand_point.shp")), "GEOID10", "Population")
        s = SupplyDataset(geopandas.read_file(os.path.join(self.dir_name, "../test_data/facility_service_areas.shp")), "ORIG_ID")
        s2 = SupplyDataset(geopandas.read_file(os.path.join(self.dir_name, "../test_data/facility2_service_areas.shp")), "ORIG_ID")
        coverage = Coverage(d, [s, s2], 'binary')
        model = coverage.create_model('lscp')
        solution = model.solve(pulp.GLPK())
        selected_locations = solution.selected_supply(s)
        selected_locations2 = solution.selected_supply(s2)
        coverage = math.ceil((solution.covered_demand()["Population"].sum() / d.df["Population"].sum()) * 100)
        assert(len(selected_locations) == 5)
        assert(len(selected_locations2) == 19)
        assert(coverage == 100)
