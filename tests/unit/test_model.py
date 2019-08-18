from allagash.model import Model
from allagash.solution import Solution
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
        assert (e.value.args[0] == "Expected 'Coverage' type for coverage, got '<class 'NoneType'>'")

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
        assert(m.problem == binary_lscp_problem)

    def test_coverage_property(self, binary_lscp_problem, binary_coverage):
        m = Model(binary_lscp_problem, binary_coverage, 'lscp')
        assert(m.coverage == binary_coverage)

    def test_model_type_property(self, binary_mclp_problem, binary_coverage):
        m = Model(binary_mclp_problem, binary_coverage, 'mclp')
        assert(m.model_type == 'mclp')

    def test_delineator_default_property(self, binary_lscp_problem, binary_coverage):
        m = Model(binary_lscp_problem, binary_coverage, 'lscp')
        assert(m.delineator == '$')

    def test_delineator_property(self, binary_lscp_problem, binary_coverage):
        m = Model(binary_lscp_problem, binary_coverage, 'lscp', delineator="*")
        assert(m.delineator == '*')

    def test_solver(self, binary_mclp_problem, binary_coverage):
        m = Model(binary_mclp_problem, binary_coverage, 'mclp')
        s = m.solve(GLPK())
        assert(isinstance(s, Solution))

    def test_invalid_solver(self, binary_mclp_problem, binary_coverage):
        m = Model(binary_mclp_problem, binary_coverage, 'mclp')
        with pytest.raises(TypeError) as e:
            s = m.solve(None)
        assert (e.value.args[0] == "Expected 'LpSolver' type for solver, got '<class 'NoneType'>'")