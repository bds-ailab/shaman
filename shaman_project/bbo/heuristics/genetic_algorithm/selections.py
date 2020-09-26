"""
This module contains several functions to perform selection of the two fittest parents.
"""

__copyright__ = """
Copyright (C) 2020 Bull S. A. S. - All rights reserved
Bull, Rue Jean Jaures, B.P.68, 78340, Les Clayes-sous-Bois, France
This is not Free or Open Source software.
Please contact Bull S. A. S. for details about its license.
"""
# Ignore unused argument kwargs
# pylint: disable=unused-argument

import numpy as np


def _sort_by_fitness(parameters, fitness):
    """
    Given a parameters and fitness array, returns the same arrays but sorted in ascending order
    of the fitness.

    Args:
        fitness (numpy array): As a numpy array, the values for the fitness.
        parameters (numpy array): As a numpy array, the values for the parameters.

    Returns:
        sorted_parameters, sorted_fitness: the sorted numpy arrays.
    """
    best_fitness_inds = fitness.argsort()
    sorted_fitness = fitness[best_fitness_inds[::]]
    sorted_parameters = parameters[best_fitness_inds[::]]
    return sorted_parameters, sorted_fitness


def _select_by_fitness(history, matingpool_size):
    """
    Given the history of an optimization process, returns "matingpool_size" parameters as ranked
    from the minimum fitness.

    Args:
        history (dict): A Python dictionary that contains the history of the optimization
            process, i.e. the parameters and the fitness value.
        matingpool_size (int): The number of the individuals to return.

    Returns:
        selected_individuals (numpy array): the selected parameters.
    """
    # extract the values from the dictionary
    fitness = history["fitness"]
    parameters = history["parameters"]

    # sort the vectors according to the fitness value
    sorted_parameters, sorted_fitness = _sort_by_fitness(parameters, fitness)

    # return the matingpool_size best parameters
    return sorted_parameters[:matingpool_size], sorted_fitness[:matingpool_size]


def _remove_from_history(parameters, fitness, parameter):
    """
    Given a parameter value, removes from the history (list of the selected fitness and
    parameter) the given parameter in order to ensure no selected parents are duplicated.

    Args:
        parameters (numpy array): An array containing the list of parameters to filter.
        fitness (numpy array): An array containing the list of fitness to filter.
        parameter: The parameter to remove from the history.

    Returns:
        filtered_history (dict): The history with the parameter and the corresponding fitness
            removed.
    """
    mask = np.any(parameters != parameter, axis=1)
    return parameters[mask], fitness[mask]


def _compute_weighted_probability(fitness):
    """
    Computes the weighted fitness given an array containing the fitness, in order to compute the
    probability for each individual to be picked.

    Args:
        fitness (numpy array): an array containing the fitness values.

    Returns:
        weighted_fitness: the weighted fitness.
    """
    # compute inverse of fitness
    inverse_fitness = 1 / (fitness - np.min(fitness) + 1)
    # compute probabilities
    probability_vector = inverse_fitness / sum(inverse_fitness)
    return probability_vector


def probabilistic_pick(history, *args, matingpool_size=100, elitism=False, **kwargs):
    """
    Given the previous history of the algorithm (i.e. the parameter values and the associated
    fitness), selects the two fittest parents using their weighted fitness as the random law to
    perform the choice. The number of candidates are limited to the first mating_size
    chromosomes, ranked according to their fitness. If the flag elitism is set to True,
    the chromosome with the highest fitness is automatically selected and only one parent is left
    to select. Once the first parent is drawn, it is removed from the list of possible candidates
    in order to ensure that it is not picked again.

    Args:
        history (dict): The history of the optimization process.
        matingpool_size (int): The size of the mating pool.
        elitism (bool): Whether or not the best parent should automatically be selected.

    Returns:
        tuple of two numpy arrays: The two parents, *i.e.* two posssible parametrizations.

    Examples:
        >>> history = {"fitness": np.array([10, 5, 4, 2, 15, 20]),
        >>>            "parameters": np.array([[1, 2], [2, 3], [1, 3], [4, 3], [2, 1], [1, 5]])}
        >>> probabilistic_pick(history, elitism=True)
        np.array([[4, 3], [2, 3]])
        >>> probabilistic_pick(history)
        np.array([[2, 1], [2, 3]])
    """
    # draw the initial mating pool
    mating_pool_parameters, mating_pool_fitness = _select_by_fitness(
        history, matingpool_size
    )
    # draw parent 1
    # if elitism is enabled, automatically draw the individual with the best fitness
    if elitism:
        parent_1 = mating_pool_parameters[0]
    # else, draw according to the weighted probability rule
    else:
        weighted_probability = _compute_weighted_probability(mating_pool_fitness)
        parent_1 = mating_pool_parameters[
            np.random.choice(mating_pool_parameters.shape[0], p=weighted_probability)
        ]
    # draw parent 2
    # make sure that it is not possible to draw parent 1 again by computing the mating pool again
    mating_pool_parameters, mating_pool_fitness = _remove_from_history(
        mating_pool_parameters, mating_pool_fitness, parent_1
    )
    # compute the new weighted probability vector
    weighted_probability = _compute_weighted_probability(mating_pool_fitness)
    parent_2 = mating_pool_parameters[
        np.random.choice(mating_pool_parameters.shape[0], p=weighted_probability)
    ]
    return parent_1, parent_2


def _draw_fitness_parameters(parameters, fitness, number_of_individuals):
    """
    Given arrays that contain parameter and fitness values, randomly draws individuals from these
    distributions.

    Args:
        parameters (numpy array): The array of parameters to draw from.
        fitness (numpy array): The array of fitness to draw from.

    Returns:
        tuple of numpy arrays: the randomly drawn parameters and the correspnding fitness
    """
    try:
        choices = np.random.choice(
            parameters.shape[0], number_of_individuals, replace=False
        )
        return parameters[choices], fitness[choices]
    # if the number_of_individuals to draw is superior to the number of individuals in the pool,
    # simply return the entire population
    except ValueError:
        return parameters[:], fitness[:]


def tournament_pick(
    history, *args, pool_size=10, matingpool_size=100, elitism=False, **kwargs
):
    """
    Given the previous history of the algorithm (i.e. the tested parameters and the associated
    fitness values), performs the pick of the two fittest parents: for each of them, pool_size
    individuals are selected and the fittest individuals is chosen. If the flag elitism is set to
    True,
    the chromosome with the highest fitness is automatically selected and only one parent is left
    to select. Once the first parent is drawn, it is removed from the list of possible candidates
    in order to ensure that it is not picked again.

    Args:
        history (dict): the history of the optimization process.
        pool_size (int): the size of each pool in the tournament.
        matingpool_size (int): The size of the mating pool
        elitism (bool): Whether or not the best parent should automatically be selected.

    Returns:
        tuple of two numpy arrays: The two parents, *i.e.* two posssible parametrizations.

    Examples:
        >>> history = {"fitness": np.array([10, 5, 4, 2, 15, 20]),
        >>>            "parameters": np.array([[1, 2], [2, 3], [1, 3], [4, 3], [2, 1], [1, 5]])}
        >>> tournament_pick(history, elitism=True)
        np.array([[4, 3], [2, 3]])
        >>> tournament_pick(history)
        np.array([[1, 3], [2, 1]])
    """
    # draw the initial mating pool
    mating_pool_parameters, mating_pool_fitness = _select_by_fitness(
        history, matingpool_size
    )
    # draw parent 1
    # if elitism is enabled, automatically draw the individual with the best fitness
    if elitism:
        parent_1 = mating_pool_parameters[0]
    # else, draw pool_size individuals and select the fittest
    else:
        tournament_pool_parameters, tournament_pool_fitness = _draw_fitness_parameters(
            mating_pool_parameters, mating_pool_fitness, number_of_individuals=pool_size
        )
        parameters, _ = _sort_by_fitness(
            tournament_pool_parameters, tournament_pool_fitness
        )
        parent_1 = parameters[0]
    # remove parent 1 from the possible values
    mating_pool_parameters, mating_pool_fitness = _remove_from_history(
        mating_pool_parameters, mating_pool_fitness, parent_1
    )
    # start again for parent 2
    tournament_pool_parameters, tournament_pool_fitness = _draw_fitness_parameters(
        mating_pool_parameters, mating_pool_fitness, number_of_individuals=pool_size
    )
    parameters, _ = _sort_by_fitness(
        tournament_pool_parameters, tournament_pool_fitness
    )
    parent_2 = parameters[0]
    return parent_1, parent_2
