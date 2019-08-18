from allagash.coverage import Coverage
from allagash.model import Model
import pytest


class TestCoverage:

    def test_init(self, demand_points, facility_service_areas):
        c = Coverage(demand_points, facility_service_areas, 'binary')
        assert(isinstance(c, Coverage))

    def test_init_invalid_demand(self, facility_service_areas):
        with pytest.raises(TypeError) as e:
            c = Coverage(None, facility_service_areas, 'binary')
        assert(e.value.args[0] == "Expected 'DemandDataset' type for demand_dataset, got '<class 'NoneType'>'")

    def test_init_invalid_supply(self, demand_points):
        with pytest.raises(TypeError) as e:
            c = Coverage(demand_points, "invalid", 'binary')
        assert (e.value.args[0] == "Expected 'SupplyDataset' or 'list' type for supply_datasets, got '<class 'str'>'")

    def test_init_none_supply(self, demand_points):
        c = Coverage(demand_points, None, 'binary')
        assert(isinstance(c, Coverage))

    def test_init_default_coverage_type(self, demand_points, facility_service_areas):
        c = Coverage(demand_points, facility_service_areas)
        assert(c.coverage_type == 'binary')

    def test_init_coverage_type_binary(self, demand_points, facility_service_areas):
        c = Coverage(demand_points, facility_service_areas, 'binary')
        assert(c.coverage_type == 'binary')

    def test_init_coverage_type_partial(self, demand_points, facility_service_areas):
        c = Coverage(demand_points, facility_service_areas, 'partial')
        assert(c.coverage_type == 'partial')

    def test_init_coverage_built(self, demand_points, facility_service_areas):
        c = Coverage(demand_points, facility_service_areas)
        assert(len(c._coverage.keys()) > 0)

    def test_init_do_not_build_coverage(self, demand_points, facility_service_areas):
        c = Coverage(demand_points, facility_service_areas, build_coverage=False)
        assert (len(c._coverage.keys()) == 0)

    def test_from_coverage_dataframe(self, demand_points, coverage_dataframe):
        c = Coverage.from_coverage_dataframe(demand_points, coverage_dataframe)
        assert(isinstance(c, Coverage))
        assert(len(c._coverage.keys()) > 0)

    def test_demand_dataset_property(self, demand_points, facility_service_areas):
        c = Coverage(demand_points, facility_service_areas)
        assert(c.demand_dataset == demand_points)

    def test_supply_datasets_property(self, demand_points, facility_service_areas):
        c = Coverage(demand_points, facility_service_areas)
        assert(isinstance(c.supply_datasets, list))
        assert(c.supply_datasets[0] == facility_service_areas)

    def test_create_lscp_model(self, demand_points, facility_service_areas):
        c = Coverage(demand_points, facility_service_areas)
        model = c.create_model('lscp')
        assert(isinstance(model, Model))
        assert(model.model_type == 'lscp')
        assert(model.problem.name == "LSCP")

    def test_create_mclp_model(self, demand_points, facility_service_areas):
        c = Coverage(demand_points, facility_service_areas)
        model = c.create_model('mclp', max_supply={facility_service_areas: 5})
        assert(isinstance(model, Model))
        assert(model.model_type == 'mclp')
        assert(model.problem.name == "MCLP")

    def test_create_mclp_model_no_max(self, demand_points, facility_service_areas):
        c = Coverage(demand_points, facility_service_areas)
        with pytest.raises(ValueError) as e:
            c.create_model('mclp')
        assert(e.value.args[0] == "'max_supply' is required")

    def test_create_mclp_model_invalid_max(self, demand_points, facility_service_areas):
        c = Coverage(demand_points, facility_service_areas)
        with pytest.raises(TypeError) as e:
            c.create_model('mclp', max_supply='test')
        assert(e.value.args[0] == "Expected 'dict' type for max_supply, got '<class 'str'>'")

    def test_create_mclp_model_empty_max(self, demand_points, facility_service_areas):
        c = Coverage(demand_points, facility_service_areas)
        with pytest.raises(ValueError) as e:
            c.create_model('mclp', max_supply={})
        assert(e.value.args[0] == "'max_supply' must contain at least one key/value pair")

    def test_create_mclp_model_str_key_max(self, demand_points, facility_service_areas):
        c = Coverage(demand_points, facility_service_areas)
        with pytest.raises(TypeError) as e:
            c.create_model('mclp', max_supply={"test": 5})
        assert(e.value.args[0] == "Expected 'SupplyDataset' type for max_supply key, got '<class 'str'>'")

    def test_create_mclp_model_str_value_max(self, demand_points, facility_service_areas):
        c = Coverage(demand_points, facility_service_areas)
        with pytest.raises(TypeError) as e:
            c.create_model('mclp', max_supply={facility_service_areas: "test"})
        assert(e.value.args[0] == "Expected 'int' type for max_supply value, got '<class 'str'>'")