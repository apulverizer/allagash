from pulp.solvers import LpSolver
from . exceptions import InfeasibleException, UnboundedException, UndefinedException, NotSolvedException


class Model:
    def __init__(self, problem, coverage, model_type, delineator="$"):
        self._problem = problem
        self._coverage = coverage
        self._model_type = model_type.lower()
        self._delineator = delineator

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

    def solve(self, solver: LpSolver = None):
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
