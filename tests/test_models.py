from allagash.model import ModelType
import pulp
import pytest
import math
from allagash.exceptions import InfeasibleException


class TestMCLP:

    @pytest.mark.usefixtures("demand_points", "facility_service_areas", "binary_coverage")
    def test_single_supply(self, demand_points, facility_service_areas, binary_coverage):
        model = binary_coverage.create_model(ModelType.MCLP, max_supply={facility_service_areas: 5})
        solution = model.solve(pulp.GLPK(msg=0))
        coverage = math.ceil((solution.covered_demand["Population"].sum() / demand_points.df["Population"].sum()) * 100)
        assert coverage == 53

    @pytest.mark.usefixtures("demand_points", "facility_service_areas", "facility2_service_areas", "binary_coverage_multiple_supply")
    def test_multiple_supply(self, demand_points, facility_service_areas, facility2_service_areas, binary_coverage_multiple_supply):
        model = binary_coverage_multiple_supply.create_model(ModelType.MCLP, max_supply={facility_service_areas: 5, facility2_service_areas: 10})
        solution = model.solve(pulp.GLPK(msg=0))
        coverage = math.ceil((solution.covered_demand["Population"].sum() / demand_points.df["Population"].sum()) * 100)
        assert coverage == 96


class TestLSCP:

    @pytest.mark.usefixtures("binary_coverage")
    def test_single_supply(self, binary_coverage):
        model = binary_coverage.create_model(ModelType.LSCP)
        with pytest.raises(InfeasibleException) as e:
            model.solve(pulp.GLPK(msg=0))

    @pytest.mark.usefixtures("demand_points", "binary_coverage_multiple_supply")
    def test_multiple_supply(self, demand_points, binary_coverage_multiple_supply):
        model = binary_coverage_multiple_supply.create_model(ModelType.LSCP)
        solution = model.solve(pulp.GLPK(msg=0))
        coverage = math.ceil((solution.covered_demand["Population"].sum() / demand_points.df["Population"].sum()) * 100)
        assert coverage == 100
