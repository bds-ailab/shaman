# Copyright 2020 BULL SAS All rights reserved
"""This module contains different functions to perform mutations on a
chromosome or a gene."""

# Ignore unused argument kwargs
# pylint: disable=unused-argument

from bbo.heuristics.simulated_annealing.neighbor_functions \
    import hop_to_next_value


def mutate_chromosome_to_neighbor(chromosome, ranges):
    """Given a chromosome (i.e. a parametrization), mutates the chromosome into
    its neighbor by using a random walk on the parameter grid. Note that this
    method makes use of the method hop_to_next_value available in the simulated
    annealing module.

    Args:
        chromosome (numpy array): A chromosome (== a parametrization)
        ranges (list of numpy array): The grid of possible values for a
            parameter.

    Returns:
        numpy array: A new chromosome obtained by a random walk on the
            parameter grid.

    Examples:
        >>> chromosome = np.array([5, 8, 3, 4])
        >>> ranges = np.array([np.arange(10), np.arange(10),
                               np.arange(10), np.arange(10)])
        >>> mutate_chromosome_to_neighbor(chromosome, ranges)
        np.array([4, 7, 4, 5])
    """
    return hop_to_next_value(chromosome, ranges)
