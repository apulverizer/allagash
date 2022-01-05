import math
import pulp
import pytest
from allagash.problem import Problem, InfeasibleException, UndefinedException


class TestMCLP:
    @pytest.mark.usefixtures("demand_points_dataframe", "binary_coverage")
    def test_single_supply(self, demand_points_dataframe, binary_coverage):
        problem = Problem.mclp(binary_coverage, max_supply={binary_coverage: 5})
        problem.solve(pulp.GLPK(msg=False))
        coverage = math.ceil(
            problem.pulp_problem.objective.value()
            / demand_points_dataframe["Population"].sum()
            * 100
        )
        assert coverage == 53

    @pytest.mark.usefixtures(
        "demand_points_dataframe", "binary_coverage", "binary_coverage2"
    )
    def test_multiple_supply(
        self, demand_points_dataframe, binary_coverage, binary_coverage2
    ):
        problem = Problem.mclp(
            [binary_coverage, binary_coverage2],
            max_supply={binary_coverage: 5, binary_coverage2: 10},
        )
        problem.solve(pulp.GLPK())
        coverage = math.ceil(
            problem.pulp_problem.objective.value()
            / demand_points_dataframe["Population"].sum()
            * 100
        )
        assert coverage == 96


class TestLSCP:
    @pytest.mark.usefixtures("binary_coverage")
    def test_single_supply_infeasible(self, binary_coverage):
        problem = Problem.lscp(binary_coverage)
        with pytest.raises((InfeasibleException, UndefinedException)):
            problem.solve(pulp.GLPK())

    @pytest.mark.usefixtures(
        "demand_points_dataframe", "binary_coverage_using_all_supply"
    )
    def test_single_supply(
        self, demand_points_dataframe, binary_coverage_using_all_supply
    ):
        problem = Problem.lscp(binary_coverage_using_all_supply)
        problem.solve(pulp.GLPK(msg=False))
        selected_locations = problem.selected_supply(binary_coverage_using_all_supply)
        covered_demand = demand_points_dataframe.query(
            f"GEOID10 in ({[f'{i}' for i in problem.selected_demand(binary_coverage_using_all_supply)]})"
        )
        coverage = math.ceil(
            (
                covered_demand[binary_coverage_using_all_supply.demand_col].sum()
                / demand_points_dataframe[
                    binary_coverage_using_all_supply.demand_col
                ].sum()
            )
            * 100
        )
        assert problem.pulp_problem.objective.value() == 24
        assert len(selected_locations) == 24
        assert coverage == 100

    @pytest.mark.usefixtures(
        "demand_points_dataframe", "binary_coverage", "binary_coverage2"
    )
    def test_multiple_supply(
        self, demand_points_dataframe, binary_coverage, binary_coverage2
    ):
        problem = Problem.lscp([binary_coverage, binary_coverage2])
        problem.solve(pulp.GLPK(msg=False))
        selected_locations = problem.selected_supply(binary_coverage)
        selected_locations2 = problem.selected_supply(binary_coverage2)
        covered_demand = demand_points_dataframe.query(
            f"GEOID10 in ({[f'{i}' for i in problem.selected_demand(binary_coverage)]})"
        )
        coverage = math.ceil(
            (
                covered_demand[binary_coverage.demand_col].sum()
                / demand_points_dataframe[binary_coverage.demand_col].sum()
            )
            * 100
        )
        assert problem.pulp_problem.objective.value() == 24
        assert len(selected_locations) >= 5
        assert len(selected_locations2) >= 17
        assert coverage == 100


class TestBCLP:
    @pytest.mark.usefixtures("binary_coverage")
    def test_single_supply_infeasible(self, binary_coverage):
        problem = Problem.bclp(binary_coverage, max_supply={binary_coverage: 5})
        with pytest.raises((InfeasibleException, UndefinedException)):
            problem.solve(pulp.GLPK())

    @pytest.mark.usefixtures(
        "demand_points_dataframe", "binary_coverage_using_all_supply"
    )
    def test_single_supply(
        self, demand_points_dataframe, binary_coverage_using_all_supply
    ):
        problem = Problem.bclp(
            binary_coverage_using_all_supply,
            max_supply={binary_coverage_using_all_supply: 24},
        )
        problem.solve(pulp.GLPK(msg=False))
        res = demand_points_dataframe.query(
            f"GEOID10 in ({[f'{i}' for i in problem.selected_demand(binary_coverage_using_all_supply)]})"
        )
        coverage = math.ceil(
            res["Population"].sum() / demand_points_dataframe["Population"].sum() * 100
        )
        assert coverage == 100
        assert (
            math.ceil(
                (
                    problem.pulp_problem.objective.value()
                    / demand_points_dataframe[
                        binary_coverage_using_all_supply.demand_col
                    ].sum()
                )
                * 100
            )
            == 56
        )

    @pytest.mark.usefixtures(
        "demand_points_dataframe", "binary_coverage", "binary_coverage2"
    )
    def test_multiple_supply(
        self, demand_points_dataframe, binary_coverage, binary_coverage2
    ):
        problem = Problem.bclp(
            [binary_coverage, binary_coverage2],
            max_supply={binary_coverage: 5, binary_coverage2: 19},
        )
        problem.solve(pulp.GLPK(msg=False))
        res = demand_points_dataframe.query(
            f"GEOID10 in ({[f'{i}' for i in problem.selected_demand(binary_coverage)]})"
        )
        coverage = math.ceil(
            res["Population"].sum() / demand_points_dataframe["Population"].sum() * 100
        )
        assert coverage == 100
        assert (
            math.ceil(
                (
                    problem.pulp_problem.objective.value()
                    / demand_points_dataframe[binary_coverage.demand_col].sum()
                )
                * 100
            )
            == 56
        )
