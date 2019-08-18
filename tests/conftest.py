import pytest
import geopandas
from allagash.dataset import DemandDataset, SupplyDataset, Dataset
from allagash.coverage import Coverage
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