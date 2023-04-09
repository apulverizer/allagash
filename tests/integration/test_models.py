import math
import pulp
import pytest
from allagash.problem import Coverage, Problem, InfeasibleException, UndefinedException


class TestMCLP:
    @pytest.mark.usefixtures("demand_points_dataframe", "binary_coverage")
    def test_single_supply(self, demand_points_dataframe, binary_coverage):
        # Demand 1,2,3,4 should be covered, Demand 5 shouldn't be covered
        problem = Problem.mclp(binary_coverage, max_supply={binary_coverage: 2})
        problem.solve(pulp.GLPK(msg=False))
        coverage = math.ceil(
            problem.pulp_problem.objective.value()
            / demand_points_dataframe["Value"].sum()
            * 100
        )
        assert coverage == 67

    @pytest.mark.usefixtures(
        "demand_points_dataframe", "binary_coverage", "binary_coverage2"
    )
    def test_multiple_supply(
        self, demand_points_dataframe, binary_coverage, binary_coverage2
    ):
        # All demand points should be covered
        problem = Problem.mclp(
            [binary_coverage, binary_coverage2],
            max_supply={binary_coverage: 2, binary_coverage2: 2},
        )
        problem.solve(pulp.GLPK())
        coverage = math.ceil(
            problem.pulp_problem.objective.value()
            / demand_points_dataframe["Value"].sum()
            * 100
        )
        assert coverage == 100

    def test_with_string_id_column(
        self,
        demand_points_dataframe,
        facility_service_areas_dataframe,
        facility2_service_areas_dataframe,
    ):
        all_facility_service_areas = facility_service_areas_dataframe.append(
            facility2_service_areas_dataframe
        )

        coverage = Coverage.from_geodataframes(
            demand_points_dataframe,
            all_facility_service_areas,
            "Name",
            "Name",
            demand_col="Value",
        )

        # MCLP
        problem = Problem.mclp([coverage], max_supply={coverage: 3})
        problem.solve(pulp.GLPK(msg=False))

        selected_locations = all_facility_service_areas.query(
            f"""Name in [{','.join([f"'{f}'" for f in problem.selected_supply(coverage)])}]"""
        )
        assert len(selected_locations) == 2
        assert selected_locations["Name"].iloc[0] == "Supply_1"
        assert selected_locations["Name"].iloc[1] == "Supply_5"


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
            f"DemandIdentifier in ({','.join(map(str, problem.selected_demand(binary_coverage_using_all_supply)))})"
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
        assert problem.pulp_problem.objective.value() == 2
        assert len(selected_locations) == 2
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
            f"DemandIdentifier in ({','.join(map(str, problem.selected_demand(binary_coverage)))})"
        )
        coverage = math.ceil(
            (
                covered_demand[binary_coverage.demand_col].sum()
                / demand_points_dataframe[binary_coverage.demand_col].sum()
            )
            * 100
        )
        assert problem.pulp_problem.objective.value() == 2
        assert len(selected_locations) == 1
        assert len(selected_locations2) == 1
        assert coverage == 100


class TestBCLP:
    @pytest.mark.usefixtures("binary_coverage")
    def test_single_supply_infeasible(self, binary_coverage):
        problem = Problem.bclp(binary_coverage, max_supply={binary_coverage: 2})
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
            max_supply={binary_coverage_using_all_supply: 2},
        )
        problem.solve(pulp.GLPK(msg=False))
        res = demand_points_dataframe.query(
            f"DemandIdentifier in ({','.join(map(str, problem.selected_demand(binary_coverage_using_all_supply)))})"
        )
        coverage = math.ceil(
            res["Value"].sum() / demand_points_dataframe["Value"].sum() * 100
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
            == 0
        )

    @pytest.mark.usefixtures(
        "demand_points_dataframe", "binary_coverage", "binary_coverage2"
    )
    def test_multiple_supply(
        self, demand_points_dataframe, binary_coverage, binary_coverage2
    ):
        problem = Problem.bclp(
            [binary_coverage, binary_coverage2],
            max_supply={binary_coverage: 2, binary_coverage2: 2},
        )
        problem.solve(pulp.GLPK(msg=False))
        res = demand_points_dataframe.query(
            f"DemandIdentifier in ({','.join(map(str, problem.selected_demand(binary_coverage)))})"
        )
        coverage = math.ceil(
            res["Value"].sum() / demand_points_dataframe["Value"].sum() * 100
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
            == 54
        )

    def test_with_string_id_column(
        self,
        demand_points_dataframe,
        facility_service_areas_dataframe,
        facility2_service_areas_dataframe,
    ):
        all_facility_service_areas = facility_service_areas_dataframe.append(
            facility2_service_areas_dataframe
        )

        coverage = Coverage.from_geodataframes(
            demand_points_dataframe,
            all_facility_service_areas,
            "Name",
            "Name",
            demand_col="Value",
        )

        problem = Problem.bclp([coverage], max_supply={coverage: 3})
        problem.solve(pulp.GLPK(msg=False))

        selected_locations = all_facility_service_areas.query(
            f"""Name in [{','.join([f"'{f}'" for f in problem.selected_supply(coverage)])}]"""
        )
        assert len(selected_locations) == 3
        assert selected_locations["Name"].iloc[0] == "Supply_1"
        assert selected_locations["Name"].iloc[1] == "Supply_3"
        assert selected_locations["Name"].iloc[2] == "Supply_5"
