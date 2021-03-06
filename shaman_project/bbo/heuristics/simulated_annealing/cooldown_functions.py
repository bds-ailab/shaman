# Copyright 2020 BULL SAS All rights reserved
"""This module contains the different functions that can be used as cooldown
schedules for the simulated annealing heuristic. Many different choice of
schedules exist in literature.

For now we have chosen to implement (alpha being the cooling factor):

- Exponential schedule
- Logarithmic schedule
- Multiplicative schedule
"""

# Ignore unused argument kwargs
# pylint: disable=unused-argument

import numpy as np


def exponential_schedule(
    initial_temperature, current_iteration, cooling_factor=0.1, **kwargs
):
    """Computes the current temperature by multiplying the temperature by
    cooling_factor at each iteration, which implies that the current
    temperature can be computed using.

    cooling_factor**current_iteration * initial_temperature
    (using the recursive formula for geometric integer series).

    .. math::
        \\T_0 \\times \\alpha \\times k

    Of course, the multiplication factor must be < 1.

    Args:
        initial_temperature (int or float): the starting
            temperature of the algorithm.
        current_iteration (int): the number of rounds already elapsed.
        cooling_factor (float): the multiplication factor alpha.
            Must be inferior to 1.

    Returns:
        float: the new value for the temperature at round k.
    """
    assert (
        cooling_factor < 1
    ), "Cooling factor must be < 1, you're warming up the system >.<"
    return cooling_factor ** current_iteration * initial_temperature


def logarithmic_schedule(
    initial_temperature, current_iteration, cooling_factor=10, **kwargs
):
    """Computes the current temperature using the logarithmic schedule formula,
    which is a function of the number of iterations and the initial
    temperature. The current temperature is equal to.

    1/(1 + cooling_factor * log(iteration + 1))

    .. math::
        \\frac{T_0}{(1 + \\alpha * log(k + 1))}

    Of course, the multiplication factor must be > 1.

    Args:
        initial_temperature (int or float): the starting temperature of
            the algorithm.
        current_iteration (int): the number of rounds already elapsed.
        cooling_factor (float): the multiplication factor alpha.
            Must be inferior to 1.

    Returns:
        float: The new value for the temperature at round k.
    """
    assert cooling_factor > 1, (
        "Cooling factor must be bigger than 1, you're warming up"
        "the system >.<"
    )
    return initial_temperature / \
        (1 + cooling_factor * np.log(current_iteration + 1))


def multiplicative_schedule(
    initial_temperature, current_iteration, cooling_factor=10, **kwargs
):
    """Computes the current temperature using the multiplicative schedule
    formula, which is a function of the number of iterations and the initial
    temperature. The current temperature is equal to.

    .. math::
        \\frac{T_0}{(1 + \\alpha * k)}

    Of course, the multiplication factor must be > 1.

    Args:
        initial_temperature (int or float): the starting temperature of
            the algorithm.
        current_iteration (int): the number of rounds already elapsed.
        cooling_factor (float): the multiplication factor alpha.
            Must be inferior to 1.

    Returns:
        float: The new value for the temperature at round k.
    """
    assert cooling_factor > 1, (
        "Cooling factor must be bigger than 1,"
        "you're warming up the system >.<"
    )
    return initial_temperature / (1 + cooling_factor * current_iteration)
