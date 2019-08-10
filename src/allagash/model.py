from pulp.solvers import LpSolver
from enum import Enum


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
        return Solution(self)
