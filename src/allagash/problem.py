import operator
import pulp
from .coverage import Coverage
from pandas.api.types import is_string_dtype


class Problem:
    _problem_types = ["lscp", "mclp", "bclp"]
    _delineator = "$"

    def __init__(self, pulp_problem, coverages, problem_type):
        """
        A representation of the linear programming problem that can be solved.
        This is not intended to be created on it's own but rather from one of the factory methods
        :meth:`~allagash.problem.Problem.lscp` or :meth:`~allagash.problem.Problem.mclp`

        .. code-block:: python

            Problem.lscp(coverage)
            Problem.lscp([coverage1, coverage2])

        :param ~pulp.LpProblem pulp_problem: The pulp problem that will be solved
        :param list[~allagash.coverage.Coverage] coverages: The coverages that were used to build the problem
        :param str problem_type: The type of problem that was generated
        """
        self._validate(pulp_problem, coverages, problem_type)
        self._pulp_problem = pulp_problem
        if isinstance(coverages, Coverage):
            self._coverages = [coverages]
        else:
            self._coverages = coverages
        self._problem_type = problem_type.lower()

    def _validate(self, problem, coverages, problem_type):
        if not isinstance(problem, pulp.LpProblem):
            raise TypeError(
                f"Expected 'LpProblem' type for problem, got '{type(problem)}'"
            )
        if not isinstance(problem_type, str):
            raise TypeError(
                f"Expected 'str' type for problem_type, got '{type(problem_type)}'"
            )
        if problem_type.lower() not in self._problem_types:
            raise ValueError(f"Invalid problem_type: '{problem_type}'")
        if not isinstance(coverages, (list, Coverage)):
            raise TypeError(
                f"Expected 'Coverage' or 'list' type for coverages, got '{type(coverages)}'"
            )

    @property
    def pulp_problem(self):
        """

        :return: The pulp problem
        :rtype: ~pulp.LpProblem
        """
        return self._pulp_problem

    @property
    def coverages(self):
        """

        :return: The coverage used to create the problem
        :rtype: list[~allagash.coverage.Coverage]
        """
        return self._coverages

    @property
    def problem_type(self):
        """

        :return: The type of problem that this is
        :rtype: str
        """
        return self._problem_type

    def solve(self, solver):
        """

        :param ~pulp.solvers.LpSolver solver: The solver to use for this problem
        :return: The solution for this problem
        :rtype: ~allagash.problem.Problem
        """
        if not isinstance(solver, pulp.LpSolver):
            raise TypeError(
                f"Expected 'LpSolver' type for solver, got '{type(solver)}'"
            )
        self._pulp_problem.solve(solver)
        if self._pulp_problem.status == 0:
            raise NotSolvedException("Unable to solve the problem")
        elif self._pulp_problem.status == -1:
            raise InfeasibleException("Infeasible problem")
        elif self._pulp_problem.status == -2:
            raise UnboundedException("Unbounded problem")
        elif self._pulp_problem.status == -3:
            raise UndefinedException("Undefined problem")
        return self

    @classmethod
    def lscp(cls, coverages):
        """
        Creates a new :class:`~allagash.problem.Problem` object representing the Location Covering Set Problem

        :param list[~allagash.coverage.Coverage] coverages: The coverages to be used to create the problem
        :return: The created problem
        :rtype: ~allagash.problem.Problem
        """
        if not isinstance(coverages, (Coverage, list)):
            raise TypeError(
                f"Expected 'Coverage' or 'list' type for coverages, got '{type(coverages)}'"
            )
        if isinstance(coverages, Coverage):
            coverages = [coverages]
        if not all([c.coverage_type == coverages[0].coverage_type for c in coverages]):
            raise ValueError(
                "Invalid coverages. Coverages must have the same coverage type."
            )
        if coverages[0].coverage_type != "binary":
            raise ValueError("LSCP can only be generated from binary coverage.")
        if not all(x.demand_name == coverages[0].demand_name for x in coverages):
            raise ValueError("All Coverages must have the same 'demand_name'")
        prob = cls._generate_lscp_problem(coverages)
        return Problem(prob, coverages, problem_type="lscp")

    @classmethod
    def bclp(cls, coverages, max_supply):
        """
        Creates a new :class:`~allagash.problem.Problem` object representing the Backup Covering Location Problem

        :param list[~allagash.coverage.Coverage] coverages: The coverages to be used to create the problem
        :param dict[~allagash.coverage.Coverage,int] max_supply: The maximum number of supply locations to allow
        :return: The created problem
        :rtype: ~allagash.problem.Problem
        """
        if not isinstance(coverages, (Coverage, list)):
            raise TypeError(
                f"Expected 'Coverage' or 'list' type for coverages, got '{type(coverages)}'"
            )
        if isinstance(coverages, Coverage):
            coverages = [coverages]
        if not all([c.coverage_type == coverages[0].coverage_type for c in coverages]):
            raise ValueError(
                "Invalid coverages. Coverages must have the same coverage type."
            )
        if coverages[0].coverage_type != "binary":
            raise ValueError("BCLP can only be generated from binary coverage.")
        if not isinstance(max_supply, dict):
            raise TypeError(
                f"Expected 'dict' type for max_supply, got '{type(max_supply)}'"
            )
        for k, v in max_supply.items():
            if not isinstance(k, Coverage):
                raise TypeError(
                    f"Expected 'Coverage' type as key in max_supply, got '{type(k)}'"
                )
            if k.demand_col is None:
                raise TypeError("Coverages used in BCLP must have 'demand_col'")
            if not isinstance(v, int):
                raise TypeError(
                    f"Expected 'int' type as value in max_supply, got '{type(v)}'"
                )
        if not all(x.demand_name == coverages[0].demand_name for x in coverages):
            raise ValueError("All Coverages must have the same 'demand_name'")
        prob = cls._generate_bclp_problem(coverages, max_supply)
        return Problem(prob, coverages, problem_type="bclp")

    @classmethod
    def mclp(cls, coverages, max_supply):
        """
        Creates a new :class:`~allagash.problem.Problem` object representing the Maximum Covering Location Problem

        :param list[~allagash.coverage.Coverage] coverages: The coverages to be used to create the problem
        :param dict[~allagash.coverage.Coverage,int] max_supply: The maximum number of supply locations to allow
        :return: The created problem
        :rtype: ~allagash.problem.Problem
        """
        if not isinstance(coverages, (Coverage, list)):
            raise TypeError(
                f"Expected 'Coverage' or 'list' type for coverages, got '{type(coverages)}'"
            )
        if isinstance(coverages, Coverage):
            coverages = [coverages]
        if not all([c.coverage_type == coverages[0].coverage_type for c in coverages]):
            raise ValueError(
                "Invalid coverages. Coverages must have the same coverage type."
            )
        if coverages[0].coverage_type != "binary":
            raise ValueError("MCLP can only be generated from binary coverage.")
        if not isinstance(max_supply, dict):
            raise TypeError(
                f"Expected 'dict' type for max_supply, got '{type(max_supply)}'"
            )
        for k, v in max_supply.items():
            if not isinstance(k, Coverage):
                raise TypeError(
                    f"Expected 'Coverage' type as key in max_supply, got '{type(k)}'"
                )
            if k.demand_col is None:
                raise TypeError("Coverages used in MCLP must have 'demand_col'")
            if not isinstance(v, int):
                raise TypeError(
                    f"Expected 'int' type as value in max_supply, got '{type(v)}'"
                )
        if not all(x.demand_name == coverages[0].demand_name for x in coverages):
            raise ValueError("All Coverages must have the same 'demand_name'")

        prob = cls._generate_mclp_problem(coverages, max_supply)
        return Problem(prob, coverages, problem_type="mclp")

    @staticmethod
    def _generate_lscp_problem(coverages):  # noqa: C901
        demand_vars = {}
        for c in coverages:
            if c.demand_name not in demand_vars:
                demand_vars[c.demand_name] = {}
            for index, _ in c.df.iterrows():
                name = f"{c.demand_name}{Problem._delineator}{index}"
                demand_vars[c.demand_name][index] = pulp.LpVariable(
                    name, 0, 1, pulp.LpInteger
                )

        supply_vars = {}
        for c in coverages:
            if c.demand_col:
                df = c.df.drop(columns=c.demand_col)
            else:
                df = c.df
            if c.supply_name not in supply_vars:
                supply_vars[c.supply_name] = {}
            for s in df.columns.to_list():
                name = f"{c.supply_name}{Problem._delineator}{s}"
                supply_vars[c.supply_name][s] = pulp.LpVariable(
                    name, 0, 1, pulp.LpInteger
                )

        prob = pulp.LpProblem("LSCP", pulp.LpMinimize)
        to_sum = []
        for _, v in supply_vars.items():
            to_sum.append(v)
        prob += pulp.lpSum(to_sum)

        sums = {}
        for c in coverages:
            if c.demand_name not in sums:
                sums[c.demand_name] = {}
            if c.demand_col:
                df = c.df.drop(columns=c.demand_col)
            else:
                df = c.df
            for index, demand in df.iterrows():
                if index not in sums[c.demand_name]:
                    sums[c.demand_name][index] = []
                cov = demand.T
                for i, value in cov.iteritems():
                    if value is True:
                        sums[c.demand_name][index].append(supply_vars[c.supply_name][i])

        for c in coverages:
            for k, v in demand_vars[c.demand_name].items():
                if not to_sum:
                    sums[c.demand_name][v] = [
                        pulp.LpVariable(
                            f"__dummy{Problem._delineator}{v}", 0, 0, pulp.LpInteger
                        )
                    ]

        for demand_name, v in sums.items():
            for i, to_sum in v.items():
                prob += pulp.lpSum(to_sum) >= 1, f"D{demand_name}{i}"
        return prob

    @staticmethod
    def _generate_bclp_problem(coverages, max_supply):  # noqa: C901
        demand_vars = {}
        for c in coverages:
            if c.demand_name not in demand_vars:
                demand_vars[c.demand_name] = {}
            for index, _ in c.df.iterrows():
                name = f"{c.demand_name}{Problem._delineator}{index}"
                demand_vars[c.demand_name][index] = pulp.LpVariable(
                    name, 0, 1, pulp.LpInteger
                )

        supply_vars = {}
        for c in coverages:
            if c.demand_col:
                df = c.df.drop(columns=c.demand_col)
            else:
                df = c.df
            if c.supply_name not in supply_vars:
                supply_vars[c.supply_name] = {}
            for s in df.columns.to_list():
                name = f"{c.supply_name}{Problem._delineator}{s}"
                supply_vars[c.supply_name][s] = pulp.LpVariable(
                    name, 0, 1, pulp.LpInteger
                )

        # add objective
        prob = pulp.LpProblem("BCLP", pulp.LpMaximize)
        demands = {}
        for c in coverages:
            for _, demand_var in demand_vars[c.demand_name].items():
                d = demand_var.name.split(Problem._delineator)[1]
                if d not in demands:
                    if is_string_dtype(coverages[0].df.index.dtype):
                        query = f"{coverages[0].df.index.name} == '{d}'"
                    else:
                        query = f"{coverages[0].df.index.name} == {d}"
                    v = c.df.query(query)[c.demand_col].tolist()[0]
                    demands[d] = v * demand_var
        to_sum = []
        for k, v in demands.items():
            to_sum.append(v)
        prob += pulp.lpSum(to_sum)

        # coverage constraints
        sums = {}
        for c in coverages:
            if c.demand_name not in sums:
                sums[c.demand_name] = {}
            if c.demand_col:
                df = c.df.drop(columns=c.demand_col)
            else:
                df = c.df
            for index, demand in df.iterrows():
                if index not in sums[c.demand_name]:
                    sums[c.demand_name][index] = [
                        -demand_vars[c.demand_name][index],
                        -1,
                    ]
                cov = demand.T
                for i, value in cov.iteritems():
                    if value is True:
                        sums[c.demand_name][index].append(supply_vars[c.supply_name][i])
        for k, v in sums.items():
            for index, to_sum in v.items():
                prob += pulp.lpSum(to_sum) >= 0, f"D{index}"

        # Number of supply locations
        for c in coverages:
            to_sum = []
            for k, v in supply_vars[c.supply_name].items():
                to_sum.append(v)
            prob += (
                pulp.lpSum(to_sum) <= max_supply[c],
                f"Num{Problem._delineator}{c.supply_name}",
            )
        return prob

    @staticmethod
    def _generate_mclp_problem(coverages, max_supply):  # noqa: C901
        demand_vars = {}
        for c in coverages:
            if c.demand_name not in demand_vars:
                demand_vars[c.demand_name] = {}
            for index, _ in c.df.iterrows():
                name = f"{c.demand_name}{Problem._delineator}{index}"
                demand_vars[c.demand_name][index] = pulp.LpVariable(
                    name, 0, 1, pulp.LpInteger
                )

        supply_vars = {}
        for c in coverages:
            if c.demand_col:
                df = c.df.drop(columns=c.demand_col)
            else:
                df = c.df
            if c.supply_name not in supply_vars:
                supply_vars[c.supply_name] = {}
            for s in df.columns.to_list():
                name = f"{c.supply_name}{Problem._delineator}{s}"
                supply_vars[c.supply_name][s] = pulp.LpVariable(
                    name, 0, 1, pulp.LpInteger
                )

        # add objective
        prob = pulp.LpProblem("MCLP", pulp.LpMaximize)
        demands = {}
        for c in coverages:
            for _, demand_var in demand_vars[c.demand_name].items():
                d = demand_var.name.split(Problem._delineator)[1]
                if d not in demands:
                    if is_string_dtype(coverages[0].df.index.dtype):
                        query = f"{coverages[0].df.index.name} == '{d}'"
                    else:
                        query = f"{coverages[0].df.index.name} == {d}"
                    v = c.df.query(query)[c.demand_col].tolist()[0]
                    demands[d] = v * demand_var
        to_sum = []
        for k, v in demands.items():
            to_sum.append(v)
        prob += pulp.lpSum(to_sum)

        # coverage constraints
        sums = {}
        for c in coverages:
            if c.demand_name not in sums:
                sums[c.demand_name] = {}
            if c.demand_col:
                df = c.df.drop(columns=c.demand_col)
            else:
                df = c.df
            for index, demand in df.iterrows():
                if index not in sums[c.demand_name]:
                    sums[c.demand_name][index] = [-demand_vars[c.demand_name][index]]
                cov = demand.T
                for i, value in cov.iteritems():
                    if value is True:
                        sums[c.demand_name][index].append(supply_vars[c.supply_name][i])
        for k, v in sums.items():
            for index, to_sum in v.items():
                prob += pulp.lpSum(to_sum) >= 0, f"D{index}"

        # Number of supply locations
        for c in coverages:
            to_sum = []
            for k, v in supply_vars[c.supply_name].items():
                to_sum.append(v)
            prob += (
                pulp.lpSum(to_sum) <= max_supply[c],
                f"Num{Problem._delineator}{c.supply_name}",
            )
        return prob

    def selected_supply(self, coverage, operation=operator.eq, value=1):
        """
        Gets the list of the supply locations that were selected when the optimization problem was solved.

        :param ~allagash.coverage.Coverage coverage: The coverage that selected locations may be found in.
        :param function operation: The operation to use when determining whether a location was selected
        :param int value: The value to apply the operation to
        :return: The list of location ids of the selected locations
        :rtype: list
        """
        if self._pulp_problem.status != 1:
            raise RuntimeError("Problem not optimally solved yet")
        from allagash.coverage import Coverage

        if not isinstance(coverage, Coverage):
            raise TypeError(
                f"Expected 'Coverage' type for coverage, got '{type(coverage)}'"
            )
        if not callable(operation):
            raise TypeError(f"Expected callable for operation, got '{type(operation)}'")
        if not isinstance(value, (int, float)):
            raise TypeError(f"Expected 'int' or 'float' for value, got '{type(value)}'")
        ids = []
        for var in self._pulp_problem.variables():
            if var.name.split(self._delineator)[0] == coverage.supply_name:
                if operation(var.varValue, value):
                    ids.append(var.name.split(self._delineator)[1])
        return ids

    def selected_demand(self, coverage):
        """
        Gets the list of the demand locations that were selected when the optimization problem was solved.

        :param ~allagash.coverage.Coverage coverage: The coverage that the demand locations may be found in. If multiple
                coverages were used that have the same demand, locations covered by any other coverages will also
                be returned.
        :return: The list of location ids of the covered locations
        :rtype: list
        """
        if self._pulp_problem.status != 1:
            raise RuntimeError("Problem not optimally solved yet")
        from allagash.coverage import Coverage

        if not isinstance(coverage, Coverage):
            raise TypeError(
                f"Expected 'Coverage' type for coverage, got '{type(coverage)}'"
            )
        if self.problem_type in ["lscp", "bclp"]:
            for c in self.coverages:
                if c.demand_name == c.demand_name:
                    return c.df.index.tolist()
            else:
                raise ValueError(
                    f"Unable to find demand named '{coverage.demand_name}'"
                )
        else:
            ids = []
            for var in self._pulp_problem.variables():
                if var.name.split(self._delineator)[0] == coverage.demand_name:
                    if var.varValue >= 1:
                        ids.append(var.name.split(self._delineator)[1])
            return ids


class NotSolvedException(Exception):
    def __init__(self, message):
        """
        An exception indicating the problem was not solved

        :param str message: A descriptive message about the exception
        """
        super().__init__(message)


class InfeasibleException(Exception):
    def __init__(self, message):
        """
        An exception indicating the problem as an infeasible solution

        :param str message: A descriptive message about the exception
        """
        super().__init__(message)


class UnboundedException(Exception):
    def __init__(self, message):
        """
        An exception indicating the solution is unbounded

        :param str message: A descriptive message about the exception
        """
        super().__init__(message)


class UndefinedException(Exception):
    def __init__(self, message):
        """
        An exception indicating the problem was not solved for an undefined reason

        :param str message: A descriptive message about the exception
        """
        super().__init__(message)
