from . exceptions import InfeasibleException, UnboundedException, UndefinedException, NotSolvedException
from pulp import LpProblem
from pulp import LpSolver


class Model:
    _model_types = ['lscp', 'mclp']

    def __init__(self, problem, coverage, model_type, delineator="$"):
        self._validate(problem, coverage, model_type, delineator)
        self._problem = problem
        self._coverage = coverage
        self._model_type = model_type.lower()
        self._delineator = delineator

    def _validate(self, problem, coverage, model_type, delineator):
        from allagash.coverage import Coverage
        if not isinstance(problem, LpProblem):
            raise TypeError(f"Expected 'LpProblem' type for problem, got '{type(problem)}'")
        if not isinstance(coverage, Coverage):
            raise TypeError(f"Expected 'Coverage' type for coverage, got '{type(coverage)}'")
        if not isinstance(model_type, str):
            raise TypeError(f"Expected 'str' type for model_type, got '{type(model_type)}'")
        if not isinstance(delineator, str):
            raise TypeError(f"Expected 'str' type for delineator, got '{type(delineator)}'")
        if model_type.lower() not in self._model_types:
            raise ValueError(f"Invalid model_type: '{model_type}'")

    @property
    def problem(self):
        return self._problem

    @property
    def coverage(self):
        return self._coverage

    @property
    def model_type(self):
        return self._model_type

    @property
    def delineator(self):
        return self._delineator

    def solve(self, solver):
        if not isinstance(solver, LpSolver):
            raise TypeError(f"Expected 'LpSolver' type for solver, got '{type(solver)}'")
        from .solution import Solution
        self._problem.solve(solver)
        if self._problem.status == 0:
            raise NotSolvedException('Unable to solve the model')
        elif self._problem.status == -1:
            raise InfeasibleException('Infeasible solution')
        elif self._problem.status == -2:
            raise UnboundedException('Unbounded solution')
        elif self._problem.status == -3:
            raise UndefinedException('Undefined solution')
        return Solution(self)
