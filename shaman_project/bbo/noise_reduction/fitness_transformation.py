# Copyright 2020 BULL SAS All rights reserved
"""This module contains several fitness transformation methods.

Fitness transformation transforms the values of the fitness that will be
given to the optimizer, in order to influence differently its choice.
"""
import numpy as np


class FitnessTransformation:
    """Abstract parent class for fitness transformation policies, that all
    fitness aggregation methods must inherit from."""

    def __init__(self, *args, **kwargs):
        """Initialize an object of class FitnessAggregation."""

    def transform(self, history):
        """Given the previous evaluation history, transforms the values of the
        fitness function to return a new history.

        Args:
            history (dict): A dictionary with two keys: parameters, which
                contains the parameters already tested by the heuristic, and
                fitness, which contains the corresponding performance measure.

        Returns:
            dict: The transformed history, with three keys: parameters, which
                contains the parameters already tested by the heuristic,
                fitness, which contains the corresponding performance measure,
                and truncated which indicates if the observation has
                been censored.
        """
        return history


class SimpleFitnessTransformation(FitnessTransformation):
    """Simple fitness transformation consists in applying an estimator (given
    as argument) on the fitness grouped by parameters. For example, if the
    estimator is the mean, the fitness is transformed by computing the mean for
    each parmametrization.

    Args:
        history (dict): A dictionary with two keys: parameters, which
            contains the parameters already tested by the heuristic, and
            fitness, which contains the corresponding performance measure.

    Returns:
        dict: The transformed history, with three keys: parameters, which
            contains the parameters already tested by the heuristic,
            fitness, which contains the corresponding performance measure,
            and truncated which indicates if the observation has been censored.
    """

    def __init__(self, estimator, *args, **kwargs):
        """Initializes an object of class SimpleFitnessTransformation.

        Args:
            estimator (function): The function to use for aggregating
            the fitness.
        """
        super(SimpleFitnessTransformation, self).\
            __init__(estimator, *args, **kwargs)
        self.estimator = estimator

    def transform(self, history):
        """Performs the transformation of the fitness, by aggregating the
        fitness within each parametrization using the estimator."""
        new_parameters = list()
        new_fitness = list()
        new_truncated = list()
        fitness_array = np.array(history["fitness"])
        # HACK: convert array to string in order to compute its
        # unique values, and then convert it using infer_types
        parameters_array = np.array(history["parameters"]).astype(str)
        truncated_array = np.array(history["truncated"])
        # Check that there is at least two elements
        if len(fitness_array) < 2:
            return history
        else:
            # Get the index of the unique parametrization
            # You have to use the index else the array gets sorted and
            # this is problematic
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
                        fitness_array[
                            np.all(parameters_array == parametrization, axis=1)
                        ]
                    )
                )
                new_truncated.append(
                    self.estimator(
                        truncated_array[
                            np.all(parameters_array == parametrization, axis=1)
                        ]
                    )
                )

            return {
                "parameters": self.infer_type_parameters(new_parameters),
                "fitness": np.array(new_fitness),
                "truncated": np.array(new_truncated),
                "initialization": history["initialization"],
                "resampled": history["resampled"],
            }

    @staticmethod
    def infer_type(array):
        """Given an array, returns a copy with the type inferred to the
        best of its ability: unless the value cannot be converted to int
        or float, the value is assumed to be a string.

        Args:
            array (np.array): The array to infer the data for.

        Returns:
            np.array: A copy of the new typed array.
        """
        copied_array = np.zeros(shape=len(array), dtype=object)
        for ix, value in enumerate(array):
            try:
                converted_value = float(value)
                if converted_value.is_integer():
                    converted_value = int(converted_value)
                copied_array[ix] = converted_value
            except ValueError:
                copied_array[ix] = str(value)
        return copied_array

    def infer_type_parameters(self, parameter_array):
        """Returns a copy of the history parameters with the type inferred
        to the best of its ability: unless the value cannot be converted
        to int or float, the value is assumed to be a string.

        Args:
            array (np.array of np.array): The array of array to infer the
                data for.

        Returns:
            np.array: A copy of the new typed array.
        """
        copied_array = []
        for ix, sub_array in enumerate(parameter_array):
            copied_array.append(np.array(self.infer_type(sub_array)))
        return np.array(copied_array)
