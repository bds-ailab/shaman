# Copyright 2020 BULL SAS All rights reserved
"""The exhaustive search heuristic tests sequentially every parameter in the
optimization grid, in the order of the parameter space specified by the
user."""
import numpy as np

from bbo.heuristics.heuristics import Heuristic


class ExhaustiveSearch(Heuristic):
    """The ExhaustiveSearch heuristic tests sequentially every parameter
    specified by the user in the parametric space.

    The order is the one specified by the user.
    """

    def __init__(self, *args, **kwargs):
        """Initialize an object of class ExhaustiveSearch and store as
        attribute the number of tested parameters (for summary purpose)."""
        super(ExhaustiveSearch, self).__init__()
        self.nbr_tested = 0

    def choose_next_parameter(self, history, ranges, *args, **kwargs):
        """Selects the next parameter to try out by the heuristic, by building
        the grid of all the possible combinations of parameters and then
        selecting the one corresponding to the next value, given the length of
        the history.

        Args:
            history (dict): the history of the optimization, i.e. the tested
                parameters and the associated value.
            ranges (numpy array of numpy arrays): the possible values of each
                parameter dimension.

        Returns:
            numpy array: The next parameter, i.e. the next parametrization in
                the grid.
        """
        # Get index of non-init value
        index = len(history["fitness"]) - sum(history["initialization"])
        # Add 1 to the number of tested parametrization
        self.nbr_tested += 1
        # Build the parametric grid
        parametric_grid = np.array(np.meshgrid(
            *ranges)).T.reshape(-1, len(ranges))
        # Return the corresponding parameter
        try:
            return parametric_grid[index]
        except IndexError:
            return parametric_grid[-1]

    def summary(self, *args, **kwargs):
        """Summarizes the grid search."""
        print(f"Number of tested parametrization: {self.nbr_tested}")

    def reset(self):
        """Resets the algorithm."""
