"""
This module contains different methods to restart the simulated annealing system. It provides
functions that return a boolean to indicate if the system should restart and the new temperature.
There exists many ways to restart the system.

The provided methods in this module are:
    - A random restart, which restarts the system randomly
    - A threshold restart, which restarts the system once it has gone under a certain threshold.
"""

# Ignore unused argument kwargs
# pylint: disable=unused-argument

import numpy as np


def random_restart(bernouilli_parameter, initial_temperature, **kwargs):
    """
    Randomly restarts the system by drawing a Bernouilli parameter in order to return a Boolean.
    Returns the system maximal temperature as this type of restart restarts the system completely.

    Args:
        bernouilli_parameter (float): A float located between 0 and 1.
        initial_temperature (float): The system's maximal temperature.

    Returns:
        tuple of bool and float: Whether or not the system should restart and the system's maximal
            temperature.
    """
    assert 0 <= bernouilli_parameter <= 1, (
        "Bernouilli's law parameter must be located between 0 " "and 1."
    )
    flag = np.random.binomial(1, bernouilli_parameter)
    return flag == 1, initial_temperature


def threshold_restart(
    probability_threshold, current_probability, initial_temperature, **kwargs
):
    """
    Restarts the system by resetting the temperature to its highest value once the acceptance
    probability function has gone underneath a given threshold.

    Args:
        probability_threshold (float): A float located between 0 and 1, that gives the threshold
            underneath which the system should restart.
        current_probability (float): The system's current acceptance probability.
        initial_temperature (float): The system's maximal temperature.

    Returns:
        tuple of bool and float: Whether or not the system should restart and the system's maximal
            temperature.
    """
    assert 0 <= probability_threshold <= 1, (
        "Probability threshold should be located between 0 " "and 1."
    )
    return current_probability < probability_threshold, initial_temperature
