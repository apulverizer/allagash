import os
import arcgis
import geopandas
import pandas as pd
from pulp import GLPK
import pytest
from allagash import Coverage
from allagash import Problem

dir_name = os.path.dirname(__file__)


@pytest.fixture(scope="class")
def demand_points_dataframe():
    demand_df = pd.DataFrame(
        {
            "Name": ["Demand_1", "Demand_2", "Demand_3", "Demand_4", "Demand_5"],
            "DemandIdentifier": [1, 2, 3, 4, 5],
            "Value": [100, 200, 300, 400, 500],
            "Latitude": [1, 2, 3, 4, 5],
            "Longitude": [1, 2, 3, 4, 5],
        }
    )
    demand_gdf = geopandas.GeoDataFrame(
        demand_df,
        geometry=geopandas.points_from_xy(demand_df.Longitude, demand_df.Latitude),
    )
    return demand_gdf


@pytest.fixture(scope="class")
def demand_points_sedf(demand_points_dataframe):
    return arcgis.GeoAccessor.from_geodataframe(
        demand_points_dataframe, column_name="geometry"
    )


@pytest.fixture(scope="class")
def demand_polygon_dataframe():
    demand_df = pd.DataFrame(
        {
            "Name": ["Demand_1", "Demand_2", "Demand_3", "Demand_4", "Demand_5"],
            "DemandIdentifier": [1, 2, 3, 4, 5],
            "Value": [100, 200, 300, 400, 500],
            "Coordinates": [
                "POLYGON((0.5 0.5, 0.5 1.5, 1.5 1.5, 1.5 0.5, 0.5 0.5))",
                "POLYGON((1.5 1.5, 1.5 2.5, 2.5 2.5, 2.5 1.5, 1.5 1.5))",
                "POLYGON((2.5 2.5, 2.5 3.5, 3.5 3.5, 3.5 2.5, 2.5 2.5))",
                "POLYGON((3.5 3.5, 3.5 4.5, 4.5 4.5, 4.5 3.5, 3.5 3.5))",
                "POLYGON((4.5 4.5, 4.5 5.5, 5.5 5.5, 5.5 4.5, 4.5 4.5))",
            ],
        }
    )

    demand_df["Coordinates"] = geopandas.GeoSeries.from_wkt(demand_df["Coordinates"])
    return geopandas.GeoDataFrame(demand_df, geometry="Coordinates")


@pytest.fixture(scope="class")
def demand_polygon_sedf(demand_polygon_dataframe):
    return arcgis.GeoAccessor.from_geodataframe(
        demand_polygon_dataframe, column_name="geometry"
    )


@pytest.fixture(scope="class")
def facility_service_areas_dataframe():
    supply_df = pd.DataFrame(
        {
            "Name": ["Supply_1", "Supply_2", "Supply_3"],
            "SupplyIdentifier": [1, 2, 3],
            "Coordinates": [
                "POLYGON((0 0, 0 3.5, 3.5 3.5, 3.5 0, 0 0))",  # Covers Demand 1, 2, 3
                "POLYGON((2.5 0, 2.5 3.5, 3.5 3.5, 3.5 0, 2.5 0))",  # Covers Demand 3
                "POLYGON((2.5 2.5, 2.5 4.5, 4.5 4.5, 4.5 2.5, 2.5 2.5))",  # Covers Demand 3, 4
            ],
        }
    )

    supply_df["Coordinates"] = geopandas.GeoSeries.from_wkt(supply_df["Coordinates"])
    return geopandas.GeoDataFrame(supply_df, geometry="Coordinates")


@pytest.fixture(scope="class")
def facility_service_areas_sedf(facility_service_areas_dataframe):
    return arcgis.GeoAccessor.from_geodataframe(
        facility_service_areas_dataframe, column_name="geometry"
    )


@pytest.fixture(scope="class")
def facility2_service_areas_dataframe():
    supply_df = pd.DataFrame(
        {
            "Name": ["Supply_4", "Supply_5"],
            "SupplyIdentifier": [4, 5],
            "Coordinates": [
                "POLYGON((0 0, 0 1.5, 1.5 1.5, 1.5 0, 0 0))",  # Covers Demand 1
                "POLYGON((3.5 3.5, 3.5 5.5, 5.5 5.5, 5.5 3.5, 3.5 3.5))",  # Covers Demand 4, 5
            ],
        }
    )

    supply_df["Coordinates"] = geopandas.GeoSeries.from_wkt(supply_df["Coordinates"])
    return geopandas.GeoDataFrame(supply_df, geometry="Coordinates")


@pytest.fixture(scope="class")
def facility2_service_areas_sedf(facility2_service_areas_dataframe):
    return arcgis.GeoAccessor.from_geodataframe(
        facility2_service_areas_dataframe, column_name="geometry"
    )


@pytest.fixture(scope="class")
def binary_coverage(demand_points_dataframe, facility_service_areas_dataframe):
    return Coverage.from_geodataframes(
        demand_points_dataframe,
        facility_service_areas_dataframe,
        "DemandIdentifier",
        "SupplyIdentifier",
        demand_col="Value",
    )


@pytest.fixture(scope="class")
def binary_coverage_no_demand(
    demand_points_dataframe, facility_service_areas_dataframe
):
    return Coverage.from_geodataframes(
        demand_points_dataframe,
        facility_service_areas_dataframe,
        "DemandIdentifier",
        "SupplyIdentifier",
    )


@pytest.fixture(scope="class")
def binary_coverage2_other_demand_name(
    demand_points_dataframe, facility2_service_areas_dataframe
):
    return Coverage.from_geodataframes(
        demand_points_dataframe,
        facility2_service_areas_dataframe,
        "DemandIdentifier",
        "SupplyIdentifier",
        demand_col="Value",
        demand_name="other",
    )


@pytest.fixture(scope="class")
def binary_coverage_using_all_supply(
    demand_points_dataframe,
    facility_service_areas_dataframe,
    facility2_service_areas_dataframe,
):
    all_facility_service_areas_df = facility_service_areas_dataframe.append(
        facility2_service_areas_dataframe
    )
    return Coverage.from_geodataframes(
        demand_points_dataframe,
        all_facility_service_areas_df,
        "DemandIdentifier",
        "SupplyIdentifier",
        demand_col="Value",
        coverage_type="binary",
    )


@pytest.fixture(scope="class")
def partial_coverage(demand_polygon_dataframe, facility_service_areas_dataframe):
    return Coverage.from_geodataframes(
        demand_polygon_dataframe,
        facility_service_areas_dataframe,
        "DemandIdentifier",
        "SupplyIdentifier",
        demand_col="Value",
        coverage_type="partial",
    )


@pytest.fixture(scope="class")
def binary_coverage2(demand_points_dataframe, facility2_service_areas_dataframe):
    return Coverage.from_geodataframes(
        demand_points_dataframe,
        facility2_service_areas_dataframe,
        "DemandIdentifier",
        "SupplyIdentifier",
        demand_col="Value",
    )


@pytest.fixture(scope="class")
def binary_coverage_dataframe(binary_coverage):
    return binary_coverage.df


@pytest.fixture(scope="class")
def binary_lscp_pulp_problem(binary_coverage, binary_coverage2):
    return Problem.lscp([binary_coverage, binary_coverage2]).pulp_problem


@pytest.fixture(scope="class")
def binary_mclp_pulp_problem(binary_coverage):
    return Problem.mclp(
        binary_coverage, max_supply={binary_coverage.supply_name: 2}
    ).pulp_problem


@pytest.fixture(scope="class")
def mclp_problem(binary_coverage, binary_coverage2):
    return Problem.mclp(
        [binary_coverage, binary_coverage2],
        max_supply={binary_coverage: 2, binary_coverage2: 2},
    )


@pytest.fixture(scope="class")
def lscp_problem(binary_coverage, binary_coverage2):
    return Problem.lscp([binary_coverage, binary_coverage2])


@pytest.fixture(scope="class")
def mclp_problem_solved(binary_coverage, binary_coverage2):
    problem = Problem.mclp(
        [binary_coverage, binary_coverage2],
        max_supply={binary_coverage: 2, binary_coverage2: 2},
    )
    problem.solve(GLPK())
    return problem
