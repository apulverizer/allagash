import pulp
from .coverage import Coverage


class Model:

    _model_types = ['lscp', 'mclp']
    _delineator = "$"

    def __init__(self, problem, coverages, model_type):
        """
        A representation of the linear programming problem that can be solved.
        This is not intended to be created on it's own but rather from one of the factory methods
        :meth:`~allagash.model.Model.lscp` or :meth:`~allagash.model.Model.mclp`

        .. code-block:: python

            Model.lscp(coverage)
            Model.lscp([coverage1, coverage2])

        :param ~pulp.LpProblem problem: The pulp problem that will be solved
        :param list[~allagash.coverage.Coverage] coverages: The coverages that were used to build the problem
        :param str model_type: The type of model that was generated
        """
        self._validate(problem, coverages, model_type)
        self._problem = problem
        if isinstance(coverages, Coverage):
            self._coverages = [coverages]
        else:
            self._coverages = coverages
        self._model_type = model_type.lower()

    def _validate(self, problem, coverages, model_type):
        if not isinstance(problem, pulp.LpProblem):
            raise TypeError(f"Expected 'LpProblem' type for problem, got '{type(problem)}'")
        if not isinstance(model_type, str):
            raise TypeError(f"Expected 'str' type for model_type, got '{type(model_type)}'")
        if model_type.lower() not in self._model_types:
            raise ValueError(f"Invalid model_type: '{model_type}'")
        if not isinstance(coverages, (list, Coverage)):
            raise TypeError(f"Expected 'Coverage' or 'list' type for coverages, got '{type(coverages)}'")

    @property
    def problem(self):
        """

        :return: The pulp problem
        :rtype: ~pulp.LpProblem
        """
        return self._problem

    @property
    def coverages(self):
        """

        :return: The coverage used to create the model
        :rtype: ~allagash.coverage.Coverage
        """
        return self._coverages

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

        :param ~pulp.solvers.LpSolver solver: The solver to use for this model
        :return: The solution for this model
        :rtype: ~allagash.solution.Solution
        """
        if not isinstance(solver, pulp.LpSolver):
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

    @classmethod
    def lscp(cls, coverages):
        """
        Creates a new :class:`~allagash.model.Model` object representing the Location Covering Set Problem

        :param list[~allagash.coverage.Coverag]e coverages: The coverages to be used to create the model
        :return: The created model
        :rtype: ~allagash.model.Model
        """
        if not isinstance(coverages, (Coverage, list)):
            raise TypeError(f"Expected 'Coverage' or 'list' type for coverages, got '{type(coverages)}'")
        if isinstance(coverages, Coverage):
            coverages = [coverages]
        if not all([c.coverage_type == coverages[0].coverage_type for c in coverages]):
            raise ValueError("Invalid coverages. Coverages must have the same coverage type.")
        if coverages[0].coverage_type != "binary":
            raise ValueError("LSCP can only be generated from binary coverage.")
        prob = cls._generate_lscp_problem(coverages)
        return Model(prob, coverages, model_type='lscp')

    @classmethod
    def mclp(cls, coverages, max_supply):
        """
        Creates a new :class:`~allagash.model.Model` object representing the Maximum Covering Location Problem

        :param list[~allagash.coverage.Coverage] coverages: The coverages to be used to create the model
        :param dict[~allagash.coverage.Coverage,int] max_supply: The maximum number of supply locations to allow
        :return: The created model
        :rtype: ~allagash.model.Model
        """
        if not isinstance(coverages, (Coverage, list)):
            raise TypeError(f"Expected 'Coverage' or 'list' type for coverages, got '{type(coverages)}'")
        if isinstance(coverages, Coverage):
            coverages = [coverages]
        if not all([c.coverage_type == coverages[0].coverage_type for c in coverages]):
            raise ValueError("Invalid coverages. Coverages must have the same coverage type.")
        if coverages[0].coverage_type != "binary":
            raise ValueError("MCLP can only be generated from binary coverage.")
        if not isinstance(max_supply, dict):
            raise TypeError(f"Expected 'dict' type for max_supply, got '{type(max_supply)}'")
        for k, v in max_supply.items():
            if not isinstance(k, Coverage):
                raise TypeError(f"Expected 'Coverage' type as key in max_supply, got '{type(k)}'")
            if not isinstance(v, int):
                raise TypeError(f"Expected 'int' type as value in max_supply, got '{type(v)}'")
        prob = cls._generate_mclp_problem(coverages, max_supply)
        return Model(prob, coverages, model_type='mclp')

    @staticmethod
    def _generate_lscp_problem(coverages):
        demand_vars = {}
        for c in coverages:
            if c.demand_name not in demand_vars:
                demand_vars[c.demand_name] = {}
            for index, _ in c.df.iterrows():
                name = f"{c.demand_name}{Model._delineator}{index}"
                demand_vars[c.demand_name][index] = pulp.LpVariable(name, 0, 1, pulp.LpInteger)

        supply_vars = {}
        for c in coverages:
            if c.demand_col:
                df = c.df.drop(columns=c.demand_col)
            else:
                df = c.df
            if c.supply_name not in supply_vars:
                supply_vars[c.supply_name] = {}
            for s in df.columns.to_list():
                name = f"{c.supply_name}{Model._delineator}{s}"
                supply_vars[c.supply_name][s] = pulp.LpVariable(name, 0, 1, pulp.LpInteger)

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
                    sums[c.demand_name][v] = [pulp.LpVariable(f"__dummy{Model._delineator}{v}", 0, 0, pulp.LpInteger)]

        for demand_name, v in sums.items():
            for i, to_sum in v.items():
                prob += pulp.lpSum(to_sum) >= 1, f"D{demand_name}{i}"
        return prob

    @staticmethod
    def _generate_mclp_problem(coverages, max_supply):
        demand_vars = {}
        for c in coverages:
            if c.demand_name not in demand_vars:
                demand_vars[c.demand_name] = {}
            for index, _ in c.df.iterrows():
                name = f"{c.demand_name}{Model._delineator}{index}"
                demand_vars[c.demand_name][index] = pulp.LpVariable(name, 0, 1, pulp.LpInteger)

        supply_vars = {}
        for c in coverages:
            if c.demand_col:
                df = c.df.drop(columns=c.demand_col)
            else:
                df = c.df
            if c.supply_name not in supply_vars:
                supply_vars[c.supply_name] = {}
            for s in df.columns.to_list():
                name = f"{c.supply_name}{Model._delineator}{s}"
                supply_vars[c.supply_name][s] = pulp.LpVariable(name, 0, 1, pulp.LpInteger)

        # add objective
        prob = pulp.LpProblem("MCLP", pulp.LpMaximize)
        demands = {}
        for c in coverages:
            for _, demand_var in demand_vars[c.demand_name].items():
                d = demand_var.name.split(Model._delineator)[1]
                if d not in demands:
                    demands[d] = []
                query = f"{coverages[0].df.index.name} == '{d}'"
                v = c.df.query(query)[c.demand_col].tolist()[0]
                demands[d].append(v * demand_var)
        to_sum = []
        for k, v in demands.items():
            to_sum.extend(v)
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
            prob += pulp.lpSum(to_sum) <= max_supply[c], f"Num{Model._delineator}{c.supply_name}"
        return prob
