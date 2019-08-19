from allagash.solution import Solution
import pandas as pd
import pytest


class TestSolution:

    def test_init(self, mclp_model):
        s = Solution(mclp_model)
        assert(isinstance(s, Solution))

    def test_init_invalid_model(self):
        with pytest.raises(TypeError) as e:
            Solution(None)
        assert(e.value.args[0] == "Expected 'Model' type for model, got '<class 'NoneType'>'")

    def test_model_property(self, mclp_model):
        s = Solution(mclp_model)
        assert(s.model == mclp_model)

    def test_selected_supply_list(self, mclp_model, facility_service_areas):
        s = Solution(mclp_model)
        assert (isinstance(s.selected_supply(facility_service_areas, output_format='list'), list))

    def test_selected_supply_dataframe(self, mclp_model, facility_service_areas):
        s = Solution(mclp_model)
        assert (isinstance(s.selected_supply(facility_service_areas, output_format='dataframe'), pd.DataFrame))

    def test_selected_supply_default(self, mclp_model, facility_service_areas):
        s = Solution(mclp_model)
        assert (isinstance(s.selected_supply(facility_service_areas), pd.DataFrame))

    def test_selected_supply_invalid_supply_dataset(self, mclp_model):
        s = Solution(mclp_model)
        with pytest.raises(TypeError) as e:
            s.selected_supply(None)
        assert (e.value.args[0] == "Expected 'SupplyDataset' type for supply_dataset, got '<class 'NoneType'>'")

    def test_selected_supply_invalid_operator(self, mclp_model, facility_service_areas):
        s = Solution(mclp_model)
        with pytest.raises(TypeError) as e:
            s.selected_supply(facility_service_areas, operation=None)
        assert (e.value.args[0] == "Expected callable for operation, got '<class 'NoneType'>'")

    def test_selected_supply_invalid_value(self, mclp_model, facility_service_areas):
        s = Solution(mclp_model)
        with pytest.raises(TypeError) as e:
            s.selected_supply(facility_service_areas, value=None)
        assert (e.value.args[0] == "Expected 'int' or 'float' for value, got '<class 'NoneType'>'")

    def test_selected_supply_invalid_output_format(self, mclp_model, facility_service_areas):
        s = Solution(mclp_model)
        with pytest.raises(TypeError) as e:
            s.selected_supply(facility_service_areas, output_format=None)
        assert (e.value.args[0] == "Expected 'str' for output_format, got '<class 'NoneType'>'")

    def test_selected_supply_invalid_output_format2(self, mclp_model, facility_service_areas):
        s = Solution(mclp_model)
        with pytest.raises(ValueError) as e:
            s.selected_supply(facility_service_areas, output_format='test')
        assert (e.value.args[0] == "Invalid output_format: 'test'")

    def test_covered_demand_default(self, mclp_solution):
        assert (isinstance(mclp_solution.covered_demand(), pd.DataFrame))

    def test_covered_demand_list(self, mclp_solution):
        assert (isinstance(mclp_solution.covered_demand(output_format='list'), list))

    def test_covered_demand_dataframe(self, mclp_solution):
        assert (isinstance(mclp_solution.covered_demand(output_format='dataframe'), pd.DataFrame))