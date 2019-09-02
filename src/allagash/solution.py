import operator
from allagash.model import Model


class Solution:
    def __init__(self, model):
        """
        A representation of the solved linear programming model

        :param ~allagash.model.Model model: The model that was solved
        """
        if not isinstance(model, Model):
            raise TypeError(f"Expected 'Model' type for model, got '{type(model)}'")
        self._model = model
        self._problem = model.problem

    @property
    def model(self):
        """

        :return: The model that was solved
        :rtype: ~allagash.model.Model
        """
        return self._model

    def selected_supply(self, coverage, operation=operator.eq, value=1):
        from allagash.coverage import Coverage
        if not isinstance(coverage, Coverage):
            raise TypeError(f"Expected 'Coverage' type for coverage, got '{type(coverage)}'")
        if not callable(operation):
            raise TypeError(f"Expected callable for operation, got '{type(operation)}'")
        if not isinstance(value, (int, float)):
            raise TypeError(f"Expected 'int' or 'float' for value, got '{type(value)}'")
        ids = []
        for var in self._problem.variables():
            if var.name.split(self._model.delineator)[0] == coverage.supply_name:
                if operation(var.varValue, value):
                    ids.append(var.name.split(self._model.delineator)[1])
        return ids

    def covered_demand(self, coverage):
        from allagash.coverage import Coverage
        if not isinstance(coverage, Coverage):
            raise TypeError(f"Expected 'Coverage' type for coverage, got '{type(coverage)}'")
        if self._model.model_type == 'lscp':
            for c in self.model.coverages:
                if c.demand_name == c.demand_name:
                    return c.df.index.tolist()
            else:
                raise ValueError(f"Unable to find demand named '{coverage.demand_name}'")
        else:
            ids = []
            for var in self._problem.variables():
                if var.name.split(self._model.delineator)[0] == coverage.demand_name:
                    if var.varValue >= 1:
                        ids.append(var.name.split(self._model.delineator)[1])
            return ids


class NotSolvedException(Exception):
    def __init__(self, message):
        """
        An exception indicating the model was not solved

        :param str message: A descriptive message about the exception
        """
        super().__init__(message)


class InfeasibleException(Exception):
    def __init__(self, message):
        """
        An exception indicating the model as an infeasible solution

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
        An exception indicating the model was not solved for an undefined reason

        :param str message: A descriptive message about the exception
        """
        super().__init__(message)
