import math
import os
import pulp
import pytest
from allagash.coverage import Coverage
from allagash.problem import Problem, InfeasibleException, UndefinedException


class TestLSCP:
    dir_name = os.path.dirname(__file__)

    def test_single_supply(
        self, demand_points_dataframe, facility_service_areas_dataframe
    ):
        coverage = Coverage.from_geodataframes(
            demand_points_dataframe,
            facility_service_areas_dataframe,
            "DemandIdentifier",
            "SupplyIdentifier",
        )
        problem = Problem.lscp(coverage)
        with pytest.raises((InfeasibleException, UndefinedException)):
            problem.solve(pulp.GLPK())

    def test_single_supply_arcgis(
        self, demand_points_sedf, facility_service_areas_sedf
    ):
        coverage = Coverage.from_spatially_enabled_dataframes(
            demand_points_sedf,
            facility_service_areas_sedf,
            "DemandIdentifier",
            "SupplyIdentifier",
            supply_geometry_col="geometry",
            demand_geometry_col="geometry",
        )
        problem = Problem.lscp(coverage)
        with pytest.raises((InfeasibleException, UndefinedException)):
            problem.solve(pulp.GLPK())

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
            demand_name=coverage.demand_name,
            demand_col=demand_col,
        )
        problem = Problem.lscp([coverage, coverage2])
        problem.solve(pulp.GLPK())
        selected_locations = problem.selected_supply(coverage)
        selected_locations2 = problem.selected_supply(coverage2)
        covered_demand = demand_points_dataframe.query(
            f"{demand_id_col} in ({','.join(map(str,problem.selected_demand(coverage)))})"
        )
        coverage = math.ceil(
            (
                covered_demand[demand_col].sum()
                / demand_points_dataframe[demand_col].sum()
            )
            * 100
        )
        assert len(selected_locations) == 1
        assert len(selected_locations2) == 1
        assert coverage == 100

    def test_multiple_supply_arcgis(
        self,
        demand_points_sedf,
        facility_service_areas_sedf,
        facility2_service_areas_sedf,
    ):
        demand_id_col = "DemandIdentifier"
        supply_id_col = "SupplyIdentifier"
        demand_col = "Value"
        coverage = Coverage.from_spatially_enabled_dataframes(
            demand_points_sedf,
            facility_service_areas_sedf,
            demand_id_col,
            supply_id_col,
            demand_col=demand_col,
            demand_geometry_col="geometry",
            supply_geometry_col="geometry",
        )
        coverage2 = Coverage.from_spatially_enabled_dataframes(
            demand_points_sedf,
            facility2_service_areas_sedf,
            demand_id_col,
            supply_id_col,
            demand_name=coverage.demand_name,
            demand_col=demand_col,
            demand_geometry_col="geometry",
            supply_geometry_col="geometry",
        )
        problem = Problem.lscp([coverage, coverage2])
        problem.solve(pulp.GLPK())
        selected_locations = problem.selected_supply(coverage)
        selected_locations2 = problem.selected_supply(coverage2)
        covered_demand = demand_points_sedf.query(
            f"{demand_id_col} in ({','.join(map(str, problem.selected_demand(coverage)))})"
        )
        coverage = math.ceil(
            (covered_demand[demand_col].sum() / demand_points_sedf[demand_col].sum())
            * 100
        )
        assert len(selected_locations) == 1
        assert len(selected_locations2) == 1
        assert coverage == 100
