"""This module contains several fitness transformation methods. Fitness transformation
transforms the values of the fitness that will be given to the optimizer, in order to
influence differently its choice.
"""
import numpy as np


class FitnessTransformation:
    """
    Abstract parent class for fitness transformation policies, that all fitness aggregation
    methods must inherit from.
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize an object of class FitnessAggregation.
        """

    def transform(self, history):
        """
        Given the previous evaluation history, transforms the values of the
        fitness function to return a new history.

        Args:
            history (dict): A dictionary with two keys: parameters, which
                contains the parameters already tested by the heuristic, and
                fitness, which contains the corresponding performance measure.

        Returns:
            dict: The transformed history, with three keys: parameters, which
                contains the parameters already tested by the heuristic,
                fitness, which contains the corresponding performance measure, and truncated
                which indicates if the observation has been censored.
        """
        return history


class SimpleFitnessTransformation(FitnessTransformation):
    """
    Simple fitness transformation consists in applying an estimator (given as argument) on the
    fitness grouped by parameters. For example, if the estimator is the mean, the fitness is
    transformed by computing the mean for each parmametrization.

    Args:
        history (dict): A dictionary with two keys: parameters, which
            contains the parameters already tested by the heuristic, and
            fitness, which contains the corresponding performance measure.

    Returns:
        dict: The transformed history, with three keys: parameters, which
            contains the parameters already tested by the heuristic,
            fitness, which contains the corresponding performance measure, and truncated
            which indicates if the observation has been censored.
    """

    def __init__(self, estimator, *args, **kwargs):
        """
        Initializes an object of class SimpleFitnessTransformation.

        Args:
            estimator (function): The function to use for aggregating the fitness.
        """
        super(SimpleFitnessTransformation, self).__init__(estimator, *args, **kwargs)
        self.estimator = estimator

    def transform(self, history):
        """
        Performs the transformation of the fitness, by aggregating the fitness within each
        parametrization using the estimator.
        """
        new_parameters = list()
        new_fitness = list()
        fitness_array = np.array(history["fitness"])
        parameters_array = np.array(history["parameters"])
        # Get the index of the unique parametrization
        # You have to use the index else the array gets sorted and this is problematic
        # for space location dependent heuristics
        unique_parameterization_indexes = np.unique(
            parameters_array, axis=0, return_index=True
        )[1]
        unique_unsorted_parameterization = [
            parameters_array[index, :]
            for index in sorted(unique_parameterization_indexes)
        ]
        for parametrization in unique_unsorted_parameterization:
            new_parameters.append(parametrization)
            new_fitness.append(
                self.estimator(
                    fitness_array[np.all(parameters_array == parametrization, axis=1)]
                )
            )
        return {
            "parameters": np.array(new_parameters),
            "fitness": np.array(new_fitness),
            "truncated": history["truncated"],
            "initialization": history["initialization"],
            "resampled": history["resampled"],
        }
