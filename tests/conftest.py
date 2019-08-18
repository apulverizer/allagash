import pytest
import geopandas
from allagash.dataset import DemandDataset, SupplyDataset
from allagash.coverage import Coverage
from allagash.model import Model
from allagash.solution import Solution
from pulp.solvers import GLPK
import os

dir_name = os.path.dirname(__file__)


@pytest.fixture(scope='class')
def demand_points_dataframe():
    return geopandas.read_file(os.path.join(dir_name, "test_data/demand_point.shp"))


@pytest.fixture(scope='class')
def facility_service_areas_dataframe():
    return geopandas.read_file(os.path.join(dir_name, "test_data/facility_service_areas.shp"))


@pytest.fixture(scope='class')
def facility2_service_areas_dataframe():
    return geopandas.read_file(os.path.join(dir_name, "test_data/facility2_service_areas.shp"))


@pytest.fixture(scope="class")
def demand_points(demand_points_dataframe):
    return DemandDataset(demand_points_dataframe, "GEOID10", "Population")


@pytest.fixture(scope="class")
def facility_service_areas(facility_service_areas_dataframe):
    return SupplyDataset(facility_service_areas_dataframe, "ORIG_ID")


@pytest.fixture(scope="class")
def facility2_service_areas(facility2_service_areas_dataframe):
    return SupplyDataset(facility2_service_areas_dataframe, "ORIG_ID")


@pytest.fixture(scope="class")
def binary_coverage(demand_points, facility_service_areas):
    return Coverage(demand_points, facility_service_areas, 'binary')


@pytest.fixture(scope="class")
def binary_coverage_multiple_supply(demand_points, facility_service_areas, facility2_service_areas):
    return Coverage(demand_points, [facility_service_areas, facility2_service_areas], 'binary')


@pytest.fixture(scope="class")
def coverage_dataframe(demand_points, facility_service_areas):
    return Coverage(demand_points, facility_service_areas)._coverage[facility_service_areas]


@pytest.fixture(scope="class")
def binary_lscp_problem(binary_coverage):
    return binary_coverage._generate_lscp_problem()


@pytest.fixture(scope="class")
def binary_mclp_problem(binary_coverage):
    return binary_coverage._generate_mclp_problem(max_supply={binary_coverage.supply_datasets[0]: 5})


@pytest.fixture(scope="class")
def mclp_model(binary_mclp_problem, binary_coverage):
    return Model(binary_mclp_problem, binary_coverage, 'mclp')


@pytest.fixture(scope="class")
def mclp_solution(mclp_model):
    mclp_model.solve(GLPK())
    return Solution(mclp_model)
