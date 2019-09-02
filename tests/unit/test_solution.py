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

    def test_selected_supply_list(self, mclp_model):
        s = Solution(mclp_model)
        assert (isinstance(s.selected_supply(mclp_model.coverages[0]), list))

    def test_selected_supply_invalid_coverage(self, mclp_model):
        s = Solution(mclp_model)
        with pytest.raises(TypeError) as e:
            s.selected_supply(None)
        assert (e.value.args[0] == "Expected 'Coverage' type for coverage, got '<class 'NoneType'>'")

    def test_selected_supply_invalid_operator(self, mclp_model):
        s = Solution(mclp_model)
        with pytest.raises(TypeError) as e:
            s.selected_supply(mclp_model.coverages[0], operation=None)
        assert (e.value.args[0] == "Expected callable for operation, got '<class 'NoneType'>'")

    def test_selected_supply_invalid_value(self, mclp_model):
        s = Solution(mclp_model)
        with pytest.raises(TypeError) as e:
            s.selected_supply(mclp_model.coverages[0], value=None)
        assert (e.value.args[0] == "Expected 'int' or 'float' for value, got '<class 'NoneType'>'")

    def test_covered_demand(self, mclp_model_solved):
        s = Solution(mclp_model_solved)
        assert (isinstance(s.selected_demand(mclp_model_solved.coverages[0]), list))

    def test_covered_demand_invalid_coverage(self, mclp_model_solved):
        s = Solution(mclp_model_solved)
        with pytest.raises(TypeError) as e:
            s.selected_demand(None)
        assert (e.value.args[0] == "Expected 'Coverage' type for coverage, got '<class 'NoneType'>'")
