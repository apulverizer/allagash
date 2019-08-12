import pytest
import geopandas
from allagash.dataset import DemandDataset, SupplyDataset
from allagash.coverage import Coverage, CoverageType


@pytest.fixture(scope="class")
def demand_points():
    return DemandDataset(geopandas.read_file("test_data/demand_point.shp"), "GEOID10", "Population")


@pytest.fixture(scope="class")
def facility_service_areas():
    return SupplyDataset(geopandas.read_file("test_data/facility_service_areas.shp"), "ORIG_ID")


@pytest.fixture(scope="class")
def facility2_service_areas():
    return SupplyDataset(geopandas.read_file("test_data/facility2_service_areas.shp"), "ORIG_ID")


@pytest.fixture(scope="class")
def binary_coverage(demand_points, facility_service_areas):
    return Coverage(demand_points, facility_service_areas, CoverageType.BINARY)


@pytest.fixture(scope="class")
def binary_coverage_multiple_supply(demand_points, facility_service_areas, facility2_service_areas):
    return Coverage(demand_points, [facility_service_areas, facility2_service_areas], CoverageType.BINARY)
