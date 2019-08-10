from pulp.solvers import LpSolver
from enum import Enum
from . exceptions import InfeasibleException, UnboundedException, UndefinedException, NotSolvedException


class ModelType(Enum):
    MCLP = 0
    MCLP_CC = 1
    THRESHOLD = 2
    THRESHOLD_CC = 3
    BCLP = 4,
    BCLP_CC = 5,
    LSCP = 6,
    TRAUMAH = 7


class Model:
    def __init__(self, problem, coverage, model_type):
        self.problem = problem
        self.coverage = coverage
        self.model_type = model_type

    def solve(self, solver: LpSolver = None):
        from .solution import Solution
        self.problem.solve(solver)
        if self.problem.status == 0:
            raise NotSolvedException('Unable to solve the model')
        elif self.problem.status == -1:
            raise InfeasibleException('Infeasible solution')
        elif self.problem.status == -2:
            raise UnboundedException('Unbounded solution')
        elif self.problem.status == -3:
            raise UndefinedException('Undefined solution')
        return Solution(self)
