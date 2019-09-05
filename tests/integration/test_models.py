import pulp
import pytest
import math
from allagash.problem import Problem, InfeasibleException, UndefinedException


class TestMCLP:

    @pytest.mark.usefixtures("demand_points_dataframe", "binary_coverage")
    def test_single_supply(self, demand_points_dataframe, binary_coverage):
        problem = Problem.mclp(binary_coverage, max_supply={binary_coverage: 5})
        problem.solve(pulp.GLPK(msg=0))
        res = demand_points_dataframe.query(f"GEOID10 in ({[f'{i}' for i in  problem.selected_demand(binary_coverage)]})")
        coverage = math.ceil(res["Population"].sum() / demand_points_dataframe["Population"].sum() * 100)
        assert coverage == 53

    @pytest.mark.usefixtures("demand_points_dataframe", "binary_coverage", "binary_coverage2")
    def test_multiple_supply(self, demand_points_dataframe, binary_coverage, binary_coverage2):
        problem = Problem.mclp([binary_coverage, binary_coverage2], max_supply={binary_coverage: 5, binary_coverage2: 10})
        problem.solve(pulp.GLPK())
        res = demand_points_dataframe.query(f"GEOID10 in ({[f'{i}' for i in problem.selected_demand(binary_coverage)]})")
        coverage = math.ceil(res["Population"].sum() / demand_points_dataframe["Population"].sum() * 100)
        assert coverage == 96


class TestLSCP:

    @pytest.mark.usefixtures("binary_coverage")
    def test_single_supply(self, binary_coverage):
        problem = Problem.lscp(binary_coverage)
        with pytest.raises((InfeasibleException, UndefinedException)) as e:
            problem.solve(pulp.GLPK())

    @pytest.mark.usefixtures("demand_points_dataframe", "binary_coverage", "binary_coverage2")
    def test_multiple_supply(self, demand_points_dataframe, binary_coverage, binary_coverage2):
        problem = Problem.lscp([binary_coverage, binary_coverage2])
        problem.solve(pulp.GLPK())
        selected_locations = problem.selected_supply(binary_coverage)
        selected_locations2 = problem.selected_supply(binary_coverage2)
        covered_demand = demand_points_dataframe.query(
            f"GEOID10 in ({[f'{i}' for i in problem.selected_demand(binary_coverage)]})")
        coverage = math.ceil((covered_demand[binary_coverage.demand_col].sum() / demand_points_dataframe[binary_coverage.demand_col].sum()) * 100)
        assert (len(selected_locations) >= 5)
        assert (len(selected_locations2) >= 17)
        assert (coverage == 100)
