import pytest
from pulp.solvers import GLPK
from allagash.problem import Problem


class TestProblem:

    def test_init(self, binary_lscp_pulp_problem, binary_coverage):
        p = Problem(binary_lscp_pulp_problem, binary_coverage, 'lscp')
        assert(isinstance(p, Problem))

    def test_init_invalid_problem(self, binary_coverage):
        with pytest.raises(TypeError) as e:
            Problem(None, binary_coverage, 'lscp')
        assert(e.value.args[0] == "Expected 'LpProblem' type for problem, got '<class 'NoneType'>'")

    def test_init_invalid_coverage(self, binary_lscp_pulp_problem):
        with pytest.raises(TypeError) as e:
            Problem(binary_lscp_pulp_problem, None, 'lscp')
        assert (e.value.args[0] == "Expected 'Coverage' or 'list' type for coverages, got '<class 'NoneType'>'")

    def test_init_invalid_problem_type(self, binary_lscp_pulp_problem, binary_coverage):
        with pytest.raises(TypeError) as e:
            Problem(binary_lscp_pulp_problem, binary_coverage, None)
        assert (e.value.args[0] == "Expected 'str' type for problem_type, got '<class 'NoneType'>'")

    def test_init_invalid_problem_type_option(self, binary_lscp_pulp_problem, binary_coverage):
        with pytest.raises(ValueError) as e:
            Problem(binary_lscp_pulp_problem, binary_coverage, 'test')
        assert (e.value.args[0] == f"Invalid problem_type: 'test'")

    def test_problem_property(self, binary_lscp_pulp_problem, binary_coverage):
        p = Problem(binary_lscp_pulp_problem, binary_coverage, 'lscp')
        assert(p.pulp_problem == binary_lscp_pulp_problem)

    def test_coverage_property(self, binary_lscp_pulp_problem, binary_coverage):
        p = Problem(binary_lscp_pulp_problem, binary_coverage, 'lscp')
        assert(p.coverages[0] == binary_coverage)

    def test_problem_type_property(self, binary_lscp_pulp_problem, binary_coverage):
        p = Problem(binary_lscp_pulp_problem, binary_coverage, 'lscp')
        assert(p.problem_type == 'lscp')

    def test_solver(self, binary_lscp_pulp_problem, binary_coverage):
        p = Problem(binary_lscp_pulp_problem, binary_coverage, 'lscp')
        p = p.solve(GLPK())
        assert(isinstance(p, Problem))

    def test_invalid_solver(self, binary_lscp_pulp_problem, binary_coverage):
        p = Problem(binary_lscp_pulp_problem, binary_coverage, 'lscp')
        with pytest.raises(TypeError) as e:
            s = p.solve(None)
        assert (e.value.args[0] == "Expected 'LpSolver' type for solver, got '<class 'NoneType'>'")

    def test_lscp(self, binary_coverage, binary_coverage2):
        p = Problem.lscp([binary_coverage, binary_coverage2])
        assert (p.problem_type == "lscp")

    def test_lscp_invalid_coverages(self):
        with pytest.raises(TypeError) as e:
            p = Problem.lscp(None)
        assert (e.value.args[0] == "Expected 'Coverage' or 'list' type for coverages, got '<class 'NoneType'>'")

    def test_lscp_invalid_coverages2(self, binary_coverage, partial_coverage):
        with pytest.raises(ValueError) as e:
            p = Problem.lscp([binary_coverage, partial_coverage])
        assert (e.value.args[0] == "Invalid coverages. Coverages must have the same coverage type.")

    def test_lscp_invalid_coverages3(self, partial_coverage):
        with pytest.raises(ValueError) as e:
            p = Problem.lscp(partial_coverage)
        assert (e.value.args[0] == "LSCP can only be generated from binary coverage.")

    def test_mclp(self, binary_coverage, binary_coverage2):
        p = Problem.mclp([binary_coverage, binary_coverage2], max_supply={binary_coverage: 5, binary_coverage2: 10})
        assert (p.problem_type == "mclp")

    def test_mclp_invalid_coverages(self):
        with pytest.raises(TypeError) as e:
            p = Problem.mclp(None, max_supply={})
        assert (e.value.args[0] == "Expected 'Coverage' or 'list' type for coverages, got '<class 'NoneType'>'")

    def test_mclp_invalid_coverages2(self, binary_coverage, partial_coverage):
        with pytest.raises(ValueError) as e:
            p = Problem.mclp([binary_coverage, partial_coverage], max_supply={binary_coverage: 5, partial_coverage: 5})
        assert (e.value.args[0] == "Invalid coverages. Coverages must have the same coverage type.")

    def test_mclp_invalid_coverages3(self, partial_coverage):
        with pytest.raises(ValueError) as e:
            p = Problem.mclp(partial_coverage, max_supply={partial_coverage: 5})
        assert (e.value.args[0] == "MCLP can only be generated from binary coverage.")

    def test_mclp_invalid_coverages4(self, binary_coverage):
        with pytest.raises(TypeError) as e:
            p = Problem.mclp(binary_coverage, max_supply={binary_coverage: 5.5})
        assert (e.value.args[0] == "Expected 'int' type as value in max_supply, got '<class 'float'>'")

    def test_mclp_invalid_coverages5(self, binary_coverage):
        with pytest.raises(TypeError) as e:
            p = Problem.mclp(binary_coverage, max_supply={"test": 5})
        assert (e.value.args[0] == "Expected 'Coverage' type as key in max_supply, got '<class 'str'>'")

    def test_mclp_invalid_coverages6(self, binary_coverage):
        with pytest.raises(TypeError) as e:
            p = Problem.mclp(binary_coverage, max_supply=None)
        assert (e.value.args[0] == "Expected 'dict' type for max_supply, got '<class 'NoneType'>'")

    def test_selected_supply_list(self, mclp_problem_solved):
        assert (isinstance(mclp_problem_solved.selected_supply(mclp_problem_solved.coverages[0]), list))

    def test_selected_supply_invalid_coverage(self, mclp_problem_solved):
        with pytest.raises(TypeError) as e:
            mclp_problem_solved.selected_supply(None)
        assert (e.value.args[0] == "Expected 'Coverage' type for coverage, got '<class 'NoneType'>'")

    def test_selected_supply_invalid_operator(self, mclp_problem_solved):
        with pytest.raises(TypeError) as e:
            mclp_problem_solved.selected_supply(mclp_problem_solved.coverages[0], operation=None)
        assert (e.value.args[0] == "Expected callable for operation, got '<class 'NoneType'>'")

    def test_selected_supply_invalid_value(self, mclp_problem_solved):
        with pytest.raises(TypeError) as e:
            mclp_problem_solved.selected_supply(mclp_problem_solved.coverages[0], value=None)
        assert (e.value.args[0] == "Expected 'int' or 'float' for value, got '<class 'NoneType'>'")

    def test_selected_demand(self, mclp_problem_solved):
        assert (isinstance(mclp_problem_solved.selected_demand(mclp_problem_solved.coverages[0]), list))

    def test_selected_demand_invalid_coverage(self, mclp_problem_solved):
        with pytest.raises(TypeError) as e:
            mclp_problem_solved.selected_demand(None)
        assert (e.value.args[0] == "Expected 'Coverage' type for coverage, got '<class 'NoneType'>'")

    def test_selected_demand_problem_not_solved(self, mclp_problem):
        with pytest.raises(RuntimeError) as e:
            mclp_problem.selected_demand(mclp_problem.coverages[0])
        assert (e.value.args[0] == "Problem not optimally solved yet")
        
    def test_selected_supply_problem_not_solved(self, mclp_problem):
        with pytest.raises(RuntimeError) as e:
            mclp_problem.selected_supply(mclp_problem.coverages[0])
        assert (e.value.args[0] == "Problem not optimally solved yet")