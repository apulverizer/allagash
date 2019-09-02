import pytest
import geopandas
from allagash import Coverage
from allagash import Model
from pulp.solvers import GLPK
import os

dir_name = os.path.dirname(__file__)


@pytest.fixture(scope='class')
def demand_points_dataframe():
    return geopandas.read_file(os.path.join(dir_name, "test_data/demand_point.shp"))


@pytest.fixture(scope='class')
def demand_polygon_dataframe():
    return geopandas.read_file(os.path.join(dir_name, "test_data/demand_polygon.shp"))


@pytest.fixture(scope='class')
def facility_service_areas_dataframe():
    return geopandas.read_file(os.path.join(dir_name, "test_data/facility_service_areas.shp"))


@pytest.fixture(scope='class')
def facility2_service_areas_dataframe():
    return geopandas.read_file(os.path.join(dir_name, "test_data/facility2_service_areas.shp"))


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
def binary_lscp_problem(binary_coverage, binary_coverage2):
    return Model.lscp([binary_coverage, binary_coverage2]).pulp_problem


@pytest.fixture(scope="class")
def binary_mclp_problem(binary_coverage):
    return Model.mclp(binary_coverage, max_supply={binary_coverage.supply_name: 5}).pulp_problem


@pytest.fixture(scope="class")
def mclp_model(binary_coverage, binary_coverage2):
    return Model.mclp([binary_coverage, binary_coverage2], max_supply={binary_coverage: 5, binary_coverage2: 10})


@pytest.fixture(scope="class")
def lscp_model(binary_coverage, binary_coverage2):
    return Model.lscp([binary_coverage, binary_coverage2])


@pytest.fixture(scope="class")
def mclp_model_solved(mclp_model):
    mclp_model.solve(GLPK())
    return mclp_model
