from pulp import LpProblem
from pulp import LpSolver


class Model:
    _model_types = ['lscp', 'mclp']

    def __init__(self, problem, coverage, model_type, delineator="$"):
        """
        A representation of the linear programming problem that can be solved.
        This is not intended to be created on it's own but rather from a :class:`~allagash.coverage.Coverage` using the `create_model` method.

        .. code-block:: python

            coverage.create_model('lscp')

        :param ~pulp.LpProblem problem: The pulp problem that will be solved
        :param ~allagash.coverage.Coverage coverage: The coverage that was used to build the problem
        :param str model_type: The type of model that was generated
        :param str delineator: The string used to split a variable in the model into two sections for parsing
        """
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
        """

        :return: The pulp problem
        :rtype: ~pulp.LpProblem
        """
        return self._problem

    @property
    def coverage(self):
        """

        :return: The coverage used to create the model
        :rtype: ~allagash.coverage.Coverage
        """
        return self._coverage

    @property
    def model_type(self):
        """

        :return: The type of model that this is
        :rtype: str
        """
        return self._model_type

    @property
    def delineator(self):
        """

        :return: The string used to split a variable in the model into two sections for parsing
        :rtype: str
        """
        return self._delineator

    def solve(self, solver):
        """

        :param ~pulp.LpSover solver: The solver to use for this model
        :return: The solution for this model
        :rtype: ~allagash.solution.Solution
        """
        if not isinstance(solver, LpSolver):
            raise TypeError(f"Expected 'LpSolver' type for solver, got '{type(solver)}'")
        from .solution import UnboundedException, UndefinedException, InfeasibleException, NotSolvedException, Solution
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
