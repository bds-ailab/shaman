# Copyright 2020 BULL SAS All rights reserved
"""This module contains different functions to perform crossover using two
chromosomes, i.e. building a child chromosome given two parents."""

# Ignore unused argument kwargs
# pylint: disable=unused-argument

import numpy as np


def single_point_crossover(parent_1, parent_2):
    """Given two parents, creates a new child by using the single point
    crossover method. The parents are split in two at a given point and the
    child is a mix of the beginning and the end of each parent.

    Args:
        parent_1 (numpy array): The first parent.
        parent_2 (numpy array): The second parent.

    Returns:
        numpy array: The child as a single point crossover of both parents.

    Examples:
        >>> parent_1 = np.array([1, 2, 1, 4])
        >>> parent_2 = np.array([3, 10, 20, 5])
        >>> single_point_crossover(parent_1, parent_2)
        np.array([1, 2, 20, 5])
    """
    parents_length = parent_1.shape[0]
    # if the length of the parent is equal or inferior to 2,
    # the crossover point is necessarily one
    if parents_length < 3:
        crossover_point = 1
    # else randomly draw the crossover point
    else:
        crossover_point = np.random.choice(np.arange(1, parents_length - 1))
    part_1 = parent_1[:crossover_point]
    part_2 = parent_2[crossover_point:]

    return np.hstack([part_1, part_2])


def double_point_crossover(parent_1, parent_2):
    """Given two parents, creates a new child by using the double point
    crossover method. The two parents are randomly split in three. The first
    and the last part of the child are from the sections of the first parent
    while its middle is taken from its second parent.

    Args:
        parent_1 (numpy array): The first parent.
        parent_2 (numpy array): The second parent.

    Returns:
        numpy array: The child as a double point crossover of both parents.

    Examples:
        >>> parent_1 = np.array([1, 2, 1, 4])
        >>> parent_2 = np.array([3, 10, 20, 5])
        >>> double_point_crossover(parent_1, parent_2)
        np.array([1, 10, 1, 4])
    """
    parents_length = parent_1.shape[0]
    if parents_length < 4:
        # switch to single point crossover
        return single_point_crossover(parent_1, parent_2)
    crossover_point = np.random.choice(
        np.arange(1, parents_length - 1), size=2, replace=False
    )
    part_1 = parent_1[: min(crossover_point)]
    part_2 = parent_2[min(crossover_point): max(crossover_point)]
    part_3 = parent_1[max(crossover_point):]
    return np.hstack([part_1, part_2, part_3])
