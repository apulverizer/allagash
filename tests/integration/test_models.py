import pulp
import pytest
import math
from allagash.model import Model
from allagash.solution import InfeasibleException, UndefinedException


class TestMCLP:

    @pytest.mark.usefixtures("demand_points_dataframe", "binary_coverage")
    def test_single_supply(self, demand_points_dataframe, binary_coverage):
        model = Model.mclp(binary_coverage, max_supply={binary_coverage: 5})
        solution = model.solve(pulp.GLPK(msg=0))
        res = demand_points_dataframe.query(f"GEOID10 in ({[f'{i}' for i in solution.covered_demand(binary_coverage)]})")
        coverage = math.ceil(res["Population"].sum() / demand_points_dataframe["Population"].sum() * 100)
        assert coverage == 53

    @pytest.mark.usefixtures("demand_points_dataframe", "binary_coverage", "binary_coverage2")
    def test_multiple_supply(self, demand_points_dataframe, binary_coverage, binary_coverage2):
        model = Model.mclp([binary_coverage, binary_coverage2], max_supply={binary_coverage: 5, binary_coverage2: 10})
        solution = model.solve(pulp.GLPK())
        res = demand_points_dataframe.query(f"GEOID10 in ({[f'{i}' for i in solution.covered_demand(binary_coverage)]})")
        coverage = math.ceil(res["Population"].sum() / demand_points_dataframe["Population"].sum() * 100)
        assert coverage == 96


class TestLSCP:

    @pytest.mark.usefixtures("binary_coverage")
    def test_single_supply(self, binary_coverage):
        model = Model.lscp(binary_coverage)
        with pytest.raises((InfeasibleException, UndefinedException)) as e:
            model.solve(pulp.GLPK())

    @pytest.mark.usefixtures("demand_points_dataframe", "binary_coverage", "binary_coverage2")
    def test_multiple_supply(self, demand_points_dataframe, binary_coverage, binary_coverage2):
        model = Model.lscp([binary_coverage, binary_coverage2])
        solution = model.solve(pulp.GLPK())
        selected_locations = solution.selected_supply(binary_coverage)
        selected_locations2 = solution.selected_supply(binary_coverage2)
        covered_demand = demand_points_dataframe.query(
            f"GEOID10 in ({[f'{i}' for i in solution.covered_demand(binary_coverage)]})")
        coverage = math.ceil((covered_demand[binary_coverage.demand_col].sum() / demand_points_dataframe[binary_coverage.demand_col].sum()) * 100)
        assert (len(selected_locations) == 5)
        assert (len(selected_locations2) == 19)
        assert (coverage == 100)
