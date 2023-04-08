import geopandas
import math
import pulp
import pytest
import pandas as pd
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

    def test_with_string_id_column(self):
        demand_df = pd.DataFrame(
            {
                "Name": ["Demand_1", "Demand_2", "Demand_3", "Demand_4", "Demand_5"],
                "Identifier": [1, 2, 3, 4, 5],
                "Value": [100, 200, 300, 400, 500],
                "Latitude": [1, 2, 3, 4, 5],
                "Longitude": [1, 2, 3, 4, 5],
            }
        )

        demand_gdf = geopandas.GeoDataFrame(
            demand_df,
            geometry=geopandas.points_from_xy(demand_df.Longitude, demand_df.Latitude),
        )

        supply_df = pd.DataFrame(
            {
                "Name": ["Supply_1", "Supply_2", "Supply_3", "Supply_4", "Supply_5"],
                "Identifier": [1, 2, 3, 4, 5],
                "Coordinates": [
                    "POLYGON((0 0, 0 3.5, 3.5 3.5, 3.5 0, 0 0))",  # Covers Demand 1, 2, 3
                    "POLYGON((2.5 0, 2.5 3.5, 3.5 3.5, 3.5 0, 2.5 0))",  # Covers Demand 3
                    "POLYGON((2.5 2.5, 2.5 4.5, 4.5 4.5, 4.5 2.5, 2.5 2.5))",  # Covers Demand 3, 4
                    "POLYGON((0 0, 0 1.5, 1.5 1.5, 1.5 0, 0 0))",  # Covers Demand 1
                    "POLYGON((3.5 3.5, 3.5 5.5, 5.5 5.5, 5.5 3.5, 3.5 3.5))",  # Covers Demand 4, 5
                ],
            }
        )

        supply_df["Coordinates"] = geopandas.GeoSeries.from_wkt(
            supply_df["Coordinates"]
        )
        supply_gdf = geopandas.GeoDataFrame(supply_df, geometry="Coordinates")
        coverage = Coverage.from_geodataframes(
            demand_gdf, supply_gdf, "Name", "Name", demand_col="Value"
        )

        # MCLP
        problem = Problem.mclp([coverage], max_supply={coverage: 3})
        problem.solve(pulp.GLPK(msg=False))

        selected_locations = supply_gdf.query(
            f"""Name in [{','.join([f"'{f}'" for f in problem.selected_supply(coverage)])}]"""
        )
        assert len(selected_locations) == 2
        assert selected_locations["Identifier"].iloc[0] == 1
        assert selected_locations["Identifier"].iloc[1] == 5


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

    def test_with_string_id_column(self):
        demand_df = pd.DataFrame(
            {
                "Name": ["Demand_1", "Demand_2", "Demand_3", "Demand_4", "Demand_5"],
                "Identifier": [1, 2, 3, 4, 5],
                "Value": [100, 200, 300, 400, 500],
                "Latitude": [1, 2, 3, 4, 5],
                "Longitude": [1, 2, 3, 4, 5],
            }
        )

        demand_gdf = geopandas.GeoDataFrame(
            demand_df,
            geometry=geopandas.points_from_xy(demand_df.Longitude, demand_df.Latitude),
        )

        supply_df = pd.DataFrame(
            {
                "Name": ["Supply_1", "Supply_2", "Supply_3", "Supply_4", "Supply_5"],
                "Identifier": [1, 2, 3, 4, 5],
                "Coordinates": [
                    "POLYGON((0 0, 0 3.5, 3.5 3.5, 3.5 0, 0 0))",  # Covers Demand 1, 2, 3
                    "POLYGON((2.5 0, 2.5 3.5, 3.5 3.5, 3.5 0, 2.5 0))",  # Covers Demand 3
                    "POLYGON((2.5 2.5, 2.5 4.5, 4.5 4.5, 4.5 2.5, 2.5 2.5))",  # Covers Demand 3, 4
                    "POLYGON((0 0, 0 1.5, 1.5 1.5, 1.5 0, 0 0))",  # Covers Demand 1
                    "POLYGON((3.5 3.5, 3.5 5.5, 5.5 5.5, 5.5 3.5, 3.5 3.5))",  # Covers Demand 4, 5
                ],
            }
        )

        supply_df["Coordinates"] = geopandas.GeoSeries.from_wkt(
            supply_df["Coordinates"]
        )
        supply_gdf = geopandas.GeoDataFrame(supply_df, geometry="Coordinates")
        coverage = Coverage.from_geodataframes(
            demand_gdf, supply_gdf, "Name", "Name", demand_col="Value"
        )

        problem = Problem.bclp([coverage], max_supply={coverage: 3})
        problem.solve(pulp.GLPK(msg=False))

        selected_locations = supply_gdf.query(
            f"""Name in [{','.join([f"'{f}'" for f in problem.selected_supply(coverage)])}]"""
        )
        assert len(selected_locations) == 3
        assert selected_locations["Identifier"].iloc[0] == 1
        assert selected_locations["Identifier"].iloc[1] == 3
        assert selected_locations["Identifier"].iloc[2] == 5
