from allagash.model import Model
import pytest
from pulp.solvers import GLPK


class TestModel:

    def test_init(self, binary_lscp_problem, binary_coverage):
        m = Model(binary_lscp_problem, binary_coverage, 'lscp')
        assert(isinstance(m, Model))

    def test_init_invalid_problem(self, binary_coverage):
        with pytest.raises(TypeError) as e:
            Model(None, binary_coverage, 'lscp')
        assert(e.value.args[0] == "Expected 'LpProblem' type for problem, got '<class 'NoneType'>'")

    def test_init_invalid_coverage(self, binary_lscp_problem):
        with pytest.raises(TypeError) as e:
            Model(binary_lscp_problem, None, 'lscp')
        assert (e.value.args[0] == "Expected 'Coverage' or 'list' type for coverages, got '<class 'NoneType'>'")

    def test_init_invalid_model_type(self, binary_lscp_problem, binary_coverage):
        with pytest.raises(TypeError) as e:
            Model(binary_lscp_problem, binary_coverage, None)
        assert (e.value.args[0] == "Expected 'str' type for model_type, got '<class 'NoneType'>'")

    def test_init_invalid_model_type_option(self, binary_lscp_problem, binary_coverage):
        with pytest.raises(ValueError) as e:
            Model(binary_lscp_problem, binary_coverage, 'test')
        assert (e.value.args[0] == f"Invalid model_type: 'test'")

    def test_problem_property(self, binary_lscp_problem, binary_coverage):
        m = Model(binary_lscp_problem, binary_coverage, 'lscp')
        assert(m.pulp_problem == binary_lscp_problem)

    def test_coverage_property(self, binary_lscp_problem, binary_coverage):
        m = Model(binary_lscp_problem, binary_coverage, 'lscp')
        assert(m.coverages[0] == binary_coverage)

    def test_model_type_property(self, binary_lscp_problem, binary_coverage):
        m = Model(binary_lscp_problem, binary_coverage, 'lscp')
        assert(m.model_type == 'lscp')

    def test_solver(self, binary_lscp_problem, binary_coverage):
        m = Model(binary_lscp_problem, binary_coverage, 'lscp')
        m = m.solve(GLPK())
        assert(isinstance(m, Model))

    def test_invalid_solver(self, binary_lscp_problem, binary_coverage):
        m = Model(binary_lscp_problem, binary_coverage, 'lscp')
        with pytest.raises(TypeError) as e:
            s = m.solve(None)
        assert (e.value.args[0] == "Expected 'LpSolver' type for solver, got '<class 'NoneType'>'")

    def test_lscp(self, binary_coverage, binary_coverage2):
        m = Model.lscp([binary_coverage, binary_coverage2])
        assert (m.model_type == "lscp")

    def test_lscp_invalid_coverages(self):
        with pytest.raises(TypeError) as e:
            m = Model.lscp(None)
        assert (e.value.args[0] == "Expected 'Coverage' or 'list' type for coverages, got '<class 'NoneType'>'")

    def test_lscp_invalid_coverages2(self, binary_coverage, partial_coverage):
        with pytest.raises(ValueError) as e:
            m = Model.lscp([binary_coverage, partial_coverage])
        assert (e.value.args[0] == "Invalid coverages. Coverages must have the same coverage type.")

    def test_lscp_invalid_coverages3(self, partial_coverage):
        with pytest.raises(ValueError) as e:
            m = Model.lscp(partial_coverage)
        assert (e.value.args[0] == "LSCP can only be generated from binary coverage.")

    def test_mclp(self, binary_coverage, binary_coverage2):
        m = Model.mclp([binary_coverage, binary_coverage2], max_supply={binary_coverage: 5, binary_coverage2: 10})
        assert (m.model_type == "mclp")

    def test_mclp_invalid_coverages(self):
        with pytest.raises(TypeError) as e:
            m = Model.mclp(None, max_supply={})
        assert (e.value.args[0] == "Expected 'Coverage' or 'list' type for coverages, got '<class 'NoneType'>'")

    def test_mclp_invalid_coverages2(self, binary_coverage, partial_coverage):
        with pytest.raises(ValueError) as e:
            m = Model.mclp([binary_coverage, partial_coverage], max_supply={binary_coverage: 5, partial_coverage: 5})
        assert (e.value.args[0] == "Invalid coverages. Coverages must have the same coverage type.")

    def test_mclp_invalid_coverages3(self, partial_coverage):
        with pytest.raises(ValueError) as e:
            m = Model.mclp(partial_coverage, max_supply={partial_coverage: 5})
        assert (e.value.args[0] == "MCLP can only be generated from binary coverage.")

    def test_mclp_invalid_coverages4(self, binary_coverage):
        with pytest.raises(TypeError) as e:
            m = Model.mclp(binary_coverage, max_supply={binary_coverage: 5.5})
        assert (e.value.args[0] == "Expected 'int' type as value in max_supply, got '<class 'float'>'")

    def test_mclp_invalid_coverages5(self, binary_coverage):
        with pytest.raises(TypeError) as e:
            m = Model.mclp(binary_coverage, max_supply={"test": 5})
        assert (e.value.args[0] == "Expected 'Coverage' type as key in max_supply, got '<class 'str'>'")

    def test_mclp_invalid_coverages6(self, binary_coverage):
        with pytest.raises(TypeError) as e:
            m = Model.mclp(binary_coverage, max_supply=None)
        assert (e.value.args[0] == "Expected 'dict' type for max_supply, got '<class 'NoneType'>'")

    def test_selected_supply_list(self, mclp_model_solved):
        assert (isinstance(mclp_model_solved.selected_supply(mclp_model_solved.coverages[0]), list))

    def test_selected_supply_invalid_coverage(self, mclp_model_solved):
        with pytest.raises(TypeError) as e:
            mclp_model_solved.selected_supply(None)
        assert (e.value.args[0] == "Expected 'Coverage' type for coverage, got '<class 'NoneType'>'")

    def test_selected_supply_invalid_operator(self, mclp_model_solved):
        with pytest.raises(TypeError) as e:
            mclp_model_solved.selected_supply(mclp_model_solved.coverages[0], operation=None)
        assert (e.value.args[0] == "Expected callable for operation, got '<class 'NoneType'>'")

    def test_selected_supply_invalid_value(self, mclp_model_solved):
        with pytest.raises(TypeError) as e:
            mclp_model_solved.selected_supply(mclp_model_solved.coverages[0], value=None)
        assert (e.value.args[0] == "Expected 'int' or 'float' for value, got '<class 'NoneType'>'")

    def test_covered_demand(self, mclp_model_solved):
        assert (isinstance(mclp_model_solved.selected_demand(mclp_model_solved.coverages[0]), list))

    def test_covered_demand_invalid_coverage(self, mclp_model_solved):
        with pytest.raises(TypeError) as e:
            mclp_model_solved.selected_demand(None)
        assert (e.value.args[0] == "Expected 'Coverage' type for coverage, got '<class 'NoneType'>'")