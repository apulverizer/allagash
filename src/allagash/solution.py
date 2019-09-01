from pandas.api.types import is_string_dtype
import operator
from allagash.model import Model
from allagash.dataset import SupplyDataset


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

    def selected_supply(self, supply_name, operation=operator.eq, value=1):
        """
        Gets the list or dataframe represnting the supply locations that were selected when the optimization problem was solved.

        :param ~allagash.dataset.SupplyDataset supply_dataset: The supply dataset that selected locations may be found in
        :param function operation: The operation to use when determining whether a location was selected
        :param int value: The value to apply the operation to
        :param str output_format: The format of the return value. Options include `dataframe` and `list`.
        :return: The list of location ids or a geodataframe of the selected locations
        :rtype: ~geopandas.GeoDataFrame or list
        """
        if not isinstance(supply_name, str):
            raise TypeError(f"Expected 'str' type for supply_name, got '{type(supply_name)}'")
        if not callable(operation):
            raise TypeError(f"Expected callable for operation, got '{type(operation)}'")
        if not isinstance(value, (int, float)):
            raise TypeError(f"Expected 'int' or 'float' for value, got '{type(value)}'")
        ids = []
        for var in self._problem.variables():
            if var.name.split(self._model.delineator)[0] == supply_name:
                if operation(var.varValue, value):
                    ids.append(var.name.split(self._model.delineator)[1])
        return ids

    def covered_demand(self, demand_name):
        """

        :param str output_format: The format of the return value. Options include `dataframe` and `list`.
        :return: The list of location ids or a geodataframe of the covered locations
        :rtype: ~geopandas.GeoDataFrame or list
        """
        if not isinstance(demand_name, str):
            raise TypeError(f"Expected 'str' for demand_name, got '{type(demand_name)}'")
        if self._model.model_type == 'lscp':
            for c in self.model.coverages:
                if c.demand_name == demand_name:
                    return c.df.index.tolist()
            else:
                raise ValueError(f"Unable to find demand named '{demand_name}'")
        else:
            ids = []
            for var in self._problem.variables():
                if var.name.split(self._model.delineator)[0] == demand_name:
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
