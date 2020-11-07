"""This module contains functions to compute the neighbors of parameters
according to a given distance. This selection is necessary for the simulated
annealing heuristic in order to pick the next parameters to evaluate.

Of course, there are infinite methods to compute the neighbors from a
parameter and they are not necessarily static: it could be possible to have
a distance as a function of the number of iteration.

For now, there is only one available selector for a given parameter:
hop_to_next_value, which implements a random walk.
"""

# Ignore unused argument kwargs
# pylint: disable=unused-argument

import numpy as np


def hop_to_next_value(parameter, ranges):
    """
    When given a parametric grid, randomly selects a neighbor of the current
    parameter using a random walk: the returned point is a neighbor of the
    parameter, the evolution in each dimension being conditioned on a
    Bernouilli law of parameter 0.5. Note that the function cannot return
    the same value as the parameter.

    Args:
        parameter (numpy array): The parameter for which the neighbor
            must be found.
        ranges (numpy array of arrays): the parameter grid as a list of
            arrays, each array representing a dimension.

    Returns:
        numpy array: The neighboring value.
    """
    # Repeat experience if it does not generate a different outcome than the
    # previous location
    while True:
        next_parameters = list()
        # For each dimension
        for axis, range_param in enumerate(ranges):
            # Get current index of parameter
            # TODO: deal more elegantly with different types
            try:
                current_index = np.where(
                    range_param.astype(str) == str(
                        parameter[axis]))[0][0]
            except IndexError:
                raise IndexError("Current parameter out of grid.")
            current_index = random_draw(current_index, len(range_param))
            next_parameters.append(range_param[current_index])
        # test equality of parameters
        if not np.array_equal(parameter, np.array(next_parameters)):
            # If the new parameter is different from the current parameter
            break
    return np.array(next_parameters)


def random_draw(current_index, range_length):
    """Randomly draws an integer between 0 and 3. If the integer is equal to 0,
    go one step up (if not already on the edge of the grid). If the integer is
    equal to 1, go one step back (if not already on the edge of the grid). If
    the integer is equal to 2, stay in the same place.

    Args:
        current_index (int): The index of the current parameter value in the
            range.
        range_length (int): The length of the array of the parameter range.

    Returns:
        int: The new index of the next parameter value in the range.
    """
    draw = np.random.randint(0, 3, 1)
    # if null draw, go one step further if it's possible
    if draw == 0:
        # go one step up if its possible
        if current_index < range_length - 2:
            current_index += 1
        # if on the border, stay put
        else:
            current_index += 0
    # if draw is equal to 1, go one step back if its possible
    elif draw == 1:
        # go one step back if it's possible
        if current_index > 0:
            current_index += -1
        # if on the lower border, stay put
        else:
            current_index += 0
    # Else (equivalent to draw == 2) do nothing
    return current_index
