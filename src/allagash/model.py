import pulp
from .coverage import Coverage


class Model:

    _model_types = ['lscp', 'mclp']

    def __init__(self, problem, coverages, model_type, delineator="$"):
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
        self._validate(problem, coverages, model_type, delineator)
        self._problem = problem
        self._coverages = coverages
        self._model_type = model_type.lower()
        self._delineator = delineator

    def _validate(self, problem, coverage, model_type, delineator):
        if not isinstance(problem, pulp.LpProblem):
            raise TypeError(f"Expected 'LpProblem' type for problem, got '{type(problem)}'")
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

        :param ~pulp.LpSover solver: The solver to use for this model
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
    def lscp(cls, coverages, delineator="$"):
        if isinstance(coverages, Coverage):
            coverages = [coverages]
        prob = cls._generate_lscp_problem(coverages, delineator=delineator)
        return Model(prob, coverages, delineator=delineator, model_type='lscp')

    @classmethod
    def mclp(cls, coverages, max_supply, delineator="$"):
        if isinstance(coverages, Coverage):
            coverages = [coverages]
        prob = cls._generate_mclp_problem(coverages, max_supply, delineator=delineator)
        return Model(prob, coverages, delineator=delineator, model_type='mclp')

    @staticmethod
    def _generate_lscp_problem(coverages, delineator="$"):
        demand_vars = {}
        for c in coverages:
            if c.demand_name not in demand_vars:
                demand_vars[c.demand_name] = {}
            for index, _ in c.df.iterrows():
                name = f"{c.demand_name}{delineator}{index}"
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
                name = f"{c.supply_name}{delineator}{s}"
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
                    sums[c.demand_name][v] = [pulp.LpVariable(f"__dummy{delineator}{v}", 0, 0, pulp.LpInteger)]

        for demand_name, v in sums.items():
            for i, to_sum in v.items():
                prob += pulp.lpSum(to_sum) >= 1, f"D{demand_name}{i}"
        return prob

    @staticmethod
    def _generate_mclp_problem(coverages, max_supply, delineator="$"):
        demand_vars = {}
        for c in coverages:
            if c.demand_name not in demand_vars:
                demand_vars[c.demand_name] = {}
            for index, _ in c.df.iterrows():
                name = f"{c.demand_name}{delineator}{index}"
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
                name = f"{c.supply_name}{delineator}{s}"
                supply_vars[c.supply_name][s] = pulp.LpVariable(name, 0, 1, pulp.LpInteger)

        # add objective
        prob = pulp.LpProblem("MCLP", pulp.LpMaximize)
        demands = {}
        for c in coverages:
            for _, demand_var in demand_vars[c.demand_name].items():
                d = demand_var.name.split(delineator)[1]
                if d not in demands:
                    demands[d] = []
                query = f"{coverages[0].df.index.name} == '{d}'"
                v = coverages[0].df.query(query)[coverages[0].demand_col].tolist()[0]
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
            prob += pulp.lpSum(to_sum) <= max_supply[c.supply_name], f"Num{delineator}{c.supply_name}"
        return prob
