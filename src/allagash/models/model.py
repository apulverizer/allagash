from pulp.solvers import LpSolver
from pulp import LpProblem
from .types import ModelType
from .solution import LSCPSolution
from typing import Union


class Model:
    def __init__(self, problem: LpProblem, coverage: 'Coverage', model_type: ModelType):
        self.problem = problem
        self.coverage = coverage
        self.model_type = model_type

    def solve(self, solver: LpSolver = None) -> Union[LSCPSolution]:
        self.problem.solve(solver)
        return LSCPSolution(self.problem, self.coverage)
