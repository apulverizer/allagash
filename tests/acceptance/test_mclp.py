import math
import os
import pulp
from allagash.coverage import Coverage
from allagash.problem import Problem


class TestMCLP:
    dir_name = os.path.dirname(__file__)

    def test_single_supply(
        self, demand_points_dataframe, facility_service_areas_dataframe
    ):
        demand_id_col = "DemandIdentifier"
        supply_id_col = "SupplyIdentifier"
        demand_col = "Value"
        coverage = Coverage.from_geodataframes(
            demand_points_dataframe,
            facility_service_areas_dataframe,
            demand_id_col,
            supply_id_col,
            demand_col=demand_col,
        )
        problem = Problem.mclp(coverage, max_supply={coverage: 1})
        problem.solve(pulp.GLPK())
        covered_demand = demand_points_dataframe.query(
            f"{demand_id_col} in ({','.join(map(str, problem.selected_demand(coverage)))})"
        )
        result = math.ceil(
            (
                covered_demand[demand_col].sum()
                / demand_points_dataframe[demand_col].sum()
            )
            * 100
        )
        assert result == 47

    def test_multiple_supply(
        self,
        demand_points_dataframe,
        facility_service_areas_dataframe,
        facility2_service_areas_dataframe,
    ):
        demand_id_col = "DemandIdentifier"
        supply_id_col = "SupplyIdentifier"
        demand_col = "Value"
        coverage = Coverage.from_geodataframes(
            demand_points_dataframe,
            facility_service_areas_dataframe,
            demand_id_col,
            supply_id_col,
            demand_col=demand_col,
        )
        coverage2 = Coverage.from_geodataframes(
            demand_points_dataframe,
            facility2_service_areas_dataframe,
            demand_id_col,
            supply_id_col,
            demand_col=demand_col,
            demand_name=coverage.demand_name,
        )
        problem = Problem.mclp(
            [coverage, coverage2], max_supply={coverage: 2, coverage2: 2}
        )
        problem.solve(pulp.GLPK())
        selected_locations = problem.selected_supply(coverage)
        selected_locations2 = problem.selected_supply(coverage2)
        covered_demand = demand_points_dataframe.query(
            f"{demand_id_col} in ({','.join(map(str, problem.selected_demand(coverage)))})"
        )
        result = math.ceil(
            (
                covered_demand[demand_col].sum()
                / demand_points_dataframe[demand_col].sum()
            )
            * 100
        )
        assert len(selected_locations) == 1
        assert len(selected_locations2) == 1
        assert result == 100
