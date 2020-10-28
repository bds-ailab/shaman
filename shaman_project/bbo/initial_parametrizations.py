"""This module contains different functions that sample some data points from a
parameter grid using different strategies for a smart selection. Many
techniques and implementations exist from the literature and for now only two
of the most common are available in the BBO package:

- Random sampling, which simply consist in randomly drawing some parameter
    from the grid.
- Latin Hypercube Sampling, which consist in finding a design that respect
    the "non collapse" properties of designs (there is no duplicate on any
    dimension).
"""


import numpy as np
from loguru import logger


def uniform_random_draw(number_of_parameters, parameter_space):
    """Draws randomly number_of_parameters among the parameter_space.

    Args:
        number_of_parameters (int): The number of parameters to draw.
        parameter_space (numpy array of numpy arrays): The parameter space,
            each array representing a dimension.

    Returns:
        numpy array of numpy arrays: an array of size number_of_parameters *
            number_of_axis containing the parameters.
    """
    if parameter_space.shape[0] != 1:
        space = parameter_space
    else:
        space = np.squeeze(parameter_space)
    random_draw = [
        np.random.choice(axis, number_of_parameters, replace=True).tolist()
        for axis in space
    ]
    return np.array(random_draw).T


def latin_hypercube_sampling(number_of_parameters, parameter_space):
    """Given a parameter space and a number of parameters to draw, draws
    number_of_parameters parameter that respect the Latin Hypercube Sampling
    rule (no parameter have the same dimension on any axis).
    The parameters are randomly drawn.

    Note that in order to respect this condition, there must be no more
    sampled points than the smallest dimension of the parameter space.

    Args:
        number_of_parameters (int): The number of parameters to draw.
        parameter_space (numpy array of numpy arrays): The parameter space,
            each array representing a dimension.

    Returns:
        numpy array of numpy arrays: an array of size number_of_parameters *
            number_of_axis containing the parameters.
    """
    # assert that the number of parameters is inferior to the maximum size of
    # the parameter space
    smallest_size = np.min([len(arr) for arr in parameter_space])
    assert number_of_parameters <= smallest_size, (
        "The number of parameters to be drawn can't be "
        "superior to the smallest dimension of the "
        "parameter space."
    )

    # empty matrix that will contain the parameter values
    random_draw = np.full((number_of_parameters, len(parameter_space)), np.nan)

    # For each row in the array
    for i in range(number_of_parameters):
        # for each dimension
        for idx, dimension in enumerate(parameter_space):
            # randomly draw the first coordinate
            random_coordinate = np.random.choice(
                dimension, 1, replace=False).tolist()
            # while the coordinate is already taken
            while random_coordinate in random_draw[:, idx]:
                random_coordinate = np.random.choice(
                    dimension, 1, replace=False
                ).tolist()
            # store value in random_draw array
            random_draw[i, idx] = random_coordinate[0]
    return random_draw


def hybrid_lhs_uniform_sampling(number_of_parameters, parameter_space):
    """Draws number_of_parameters parameter that respect the Latin Hypercube
    Sampling rule while the number of parameter does not exceed the number
    value in the smallest sample. Beyond, a uniform random sampling is applied.

    Args:
        number_of_parameters (int): The number of parameters to draw.
        parameter_space (numpy array of numpy arrays): The parameter space,
            each array representing a dimension.

    Returns:
        numpy array of numpy arrays: an array of size number_of_parameters *
            number_of_axis containing the parameters.
    """
    logger.debug(
        f"Selected number of initial parameters: {number_of_parameters}")
    n_lhs_param = number_of_parameters
    smallest_size = np.min([len(arr) for arr in parameter_space])
    if smallest_size < number_of_parameters:
        n_lhs_param = smallest_size
    lhs_draw = latin_hypercube_sampling(n_lhs_param, parameter_space)
    ur_draw = uniform_random_draw(
        max(number_of_parameters - n_lhs_param, 0), parameter_space
    )
    return np.append(lhs_draw, ur_draw, axis=0)
