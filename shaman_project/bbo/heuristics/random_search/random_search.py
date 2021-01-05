# Copyright 2020 BULL SAS All rights reserved
"""The random search heuristic randomly draws a value from the possible
parametric value"""
import numpy as np

from bbo.heuristics.heuristics import Heuristic


class RandomSearch(Heuristic):
    """The ExhaustiveSearch heuristic tests sequentially every parameter
    specified by the user in the parametric space.

    The order is the one specified by the user.
    """

    def __init__(self, *args, **kwargs):
        """Initialize an object of class ExhaustiveSearch and store as
        attribute the number of tested parameters (for summary purpose)."""
        super(RandomSearch, self).__init__()

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
        # Build the parametric grid
        parametric_grid = np.array(np.meshgrid(
            *ranges)).T.reshape(-1, len(ranges))
        # Randomly draw an index value from this grid
        random_index = np.random.randint(low=0, high=len(parametric_grid))
        return parametric_grid[random_index]

    def summary(self):
        """Summarizes the grid search."""

    def reset(self):
        """Resets the algorithm."""
