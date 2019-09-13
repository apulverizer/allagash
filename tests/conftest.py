import os
import arcgis
import geopandas
from pulp.solvers import GLPK
import pytest
from allagash import Coverage
from allagash import Problem

dir_name = os.path.dirname(__file__)


@pytest.fixture(scope='class')
def demand_points_dataframe():
    return geopandas.read_file(os.path.join(dir_name, "test_data/demand_point.shp"))


@pytest.fixture(scope='class')
def demand_points_sedf():
    return arcgis.GeoAccessor.from_featureclass(os.path.join(dir_name, "test_data/demand_point.shp"))


@pytest.fixture(scope='class')
def demand_polygon_dataframe():
    return geopandas.read_file(os.path.join(dir_name, "test_data/demand_polygon.shp"))


@pytest.fixture(scope='class')
def demand_polygon_sedf():
    return arcgis.GeoAccessor.from_featureclass(os.path.join(dir_name, "test_data/demand_polygon.shp"))


@pytest.fixture(scope='class')
def facility_service_areas_dataframe():
    return geopandas.read_file(os.path.join(dir_name, "test_data/facility_service_areas.shp"))


@pytest.fixture(scope='class')
def facility_service_areas_sedf():
    return arcgis.GeoAccessor.from_featureclass(os.path.join(dir_name, "test_data/facility_service_areas.shp"))


@pytest.fixture(scope='class')
def facility2_service_areas_dataframe():
    return geopandas.read_file(os.path.join(dir_name, "test_data/facility2_service_areas.shp"))


@pytest.fixture(scope='class')
def facility2_service_areas_sedf():
    return arcgis.GeoAccessor.from_featureclass(os.path.join(dir_name, "test_data/facility2_service_areas.shp"))


@pytest.fixture(scope="class")
def binary_coverage(demand_points_dataframe, facility_service_areas_dataframe):
    return Coverage.from_geodataframes(demand_points_dataframe, facility_service_areas_dataframe, "GEOID10", "ORIG_ID",
                                       demand_col="Population",
                                       demand_name="demand")


@pytest.fixture(scope="class")
def partial_coverage(demand_polygon_dataframe, facility_service_areas_dataframe):
    return Coverage.from_geodataframes(demand_polygon_dataframe, facility_service_areas_dataframe, "GEOID10", "ORIG_ID",
                                       demand_col="Population",
                                       demand_name="demand",
                                       coverage_type="partial")


@pytest.fixture(scope="class")
def binary_coverage2(demand_points_dataframe, facility2_service_areas_dataframe):
    return Coverage.from_geodataframes(demand_points_dataframe, facility2_service_areas_dataframe, "GEOID10", "ORIG_ID",
                                       demand_col="Population",
                                       demand_name="demand")


@pytest.fixture(scope="class")
def binary_coverage_dataframe(binary_coverage):
    return binary_coverage.df


@pytest.fixture(scope="class")
def binary_lscp_pulp_problem(binary_coverage, binary_coverage2):
    return Problem.lscp([binary_coverage, binary_coverage2]).pulp_problem


@pytest.fixture(scope="class")
def binary_mclp_pulp_problem(binary_coverage):
    return Problem.mclp(binary_coverage, max_supply={binary_coverage.supply_name: 5}).pulp_problem


@pytest.fixture(scope="class")
def mclp_problem(binary_coverage, binary_coverage2):
    return Problem.mclp([binary_coverage, binary_coverage2], max_supply={binary_coverage: 5, binary_coverage2: 10})


@pytest.fixture(scope="class")
def lscp_problem(binary_coverage, binary_coverage2):
    return Problem.lscp([binary_coverage, binary_coverage2])


@pytest.fixture(scope="class")
def mclp_problem_solved(binary_coverage, binary_coverage2):
    problem = Problem.mclp([binary_coverage, binary_coverage2], max_supply={binary_coverage: 5, binary_coverage2: 10})
    problem.solve(GLPK())
    return problem
