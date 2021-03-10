# Copyright 2020 BULL SAS All rights reserved
"""This module contains different classes to implement a stop criterion.
These criteria take as input the history of the optimization process,
and outputs a boolean indicating if the optimization process should stop
depending on the tested values.

The implemented criteria are:
- Improvement based:
    - Best improvement: improvement of the best objective value is
        below a threshold t for a number of iterations g
    - Average improvement: improvement of the average object function
        is below a threshold t for a number of iterations g
- Movement based:
    - Count based: the optimization algorithm is stopped once
        there is less than t different parametrization evaluated
        over a number of iterations g
    - Distance based: the optimization algorithm is stopped once
        the distance between each parametrization goes below a
        certain threshold t for a number of iterations g
"""
import itertools
import numpy as np


class StopCriterion:
    """
    Abstract parent class for stop rules, that all implementations of stop
    criterion should inherit from.
    """

    def stop_rule(self, history):
        """Given the previous optimization history, returns False if the
        optimization should stop, and else should evaluate to True.

        Args:
            history (dict): A dictionary describing the BBO optimization
                history.
            stop_window (int): The number of iterations
                the improvement should be computed on.

        Returns:
            bool: whether or not the optimization process should be
                stopped given the history.
        """
        raise NotImplementedError


class ImprovementCriterion(StopCriterion):
    """
    Implements a stop criterion based on the notion of improvements.
    This class outputs true (ie: do not stop the optimization
    process) if the improvement in the
    fitness function is below the value threshold for over
    stop_window iterations. The improvement is defined as
    a ratio between the value of an estimator (eg: minimum, maximum ...)
    found in the whole history and in the last stop_window iterations.
    The threshold must thus be defined as a float
    located between 0 and 1.
    """

    def __init__(self, improvement_threshold,
                 improvement_estimator, stop_window, *args,
                 **kwargs):
        """
        Initializes an object of class BestImprovement, by giving
        as input the value of the improvement_threshold, the
        improvement_estimator and the stop_window.

        Args:
            improvement_threshold (float): The expected ratio of improvement to
                stop the optimization or not.
            improvement_estimator (function): The function to compute on the
                fitness to compute the improvement.
            stop_window (int): The number of iterations
                the improvement should be computed on.
        """
        self.improvement_threshold = improvement_threshold
        self.improvement_estimator = improvement_estimator
        self.stop_window = stop_window

    def stop_rule(self, history):
        """This method outputs true (ie: do not stop the optimization
        process) if the improvement in the
        fitness function is below the value threshold for over
        stop_window iterations. The improvement is defined as
        a ratio between the value computed by the estimator found in the
        whole history and in the last nbr_iterations. The threshold must thus
        be defined as a float located between 0 and 1.

        Args:
            history (dict): A dictionary describing the BBO optimization
                history.

        Returns:
            bool: whether or not the optimization process should be
                stopped given the history.
        """
        fitness = history["fitness"]
        # If the number of iterations for the interval is below the
        # already computed parametrization, return False
        # (aka: do not stop the optimization process)
        if len(fitness) <= self.stop_window:
            return True
        current_improvement = self.improvement_estimator(
            fitness[:-self.stop_window])
        improvement_in_iterations = self.improvement_estimator(
            fitness[-self.stop_window:])
        improvement_ratio = (
            current_improvement - improvement_in_iterations)\
            / current_improvement
        return improvement_ratio >= self.improvement_threshold


class CountMovementCriterion(StopCriterion):
    """The CountMovementCriterion relies on the number of different
    parametrization tested over the number of distinct parametrizations
    is below the threshold stop_window over a stop_window
    iterations
    """

    def __init__(self, nbr_parametrizations, stop_window, *args,
                 **kwargs):
        """Initializes an object of class CountMovementCriterion, by giving
        as input the value of the distinct number of parametrizations
        nbr_parametrizations and the stop window stop_window.

        Args:
        stop_window (int): The number of iterations
            the number of distinct parametrizations should be computed on.
        nbr_parametrization (int): The number of required distinct
            parametrization to not stop the optimization process.
        """
        self.nbr_parametrizations = nbr_parametrizations
        self.stop_window = stop_window

    def stop_rule(self, history):
        """This method outputs true (ie: do not stop the optimization
        process) if the number of distinct parametrizations is below the
        threshold nbr_parametrizations over a stop_window number of
        iterations.

        Args:
            history (dict): A dictionary describing the BBO optimization
                history.

        Returns:
            bool: whether or not the optimization process should be
                stopped given the history.
        """
        parametrization = history["parameters"]
        # If the number of iterations for the interval is below the
        # already computed parametrization, return False
        # (aka: do not stop the optimization process)
        if len(parametrization) <= self.stop_window:
            return True
        unique_parametrization = np.unique(
            parametrization[-self.stop_window:], axis=0)
        return len(unique_parametrization) > self.nbr_parametrizations


class DistanceMovementCriterion(StopCriterion):
    """The CountMovementCriterion relies on the number of different
    parametrization tested over the number of distinct parametrizations
    is below the threshold stop_window over a stop_window
    iterations
    """

    def __init__(self, distance, stop_window, *args,
                 **kwargs):
        """Initializes an object of class CountMovementCriterion, by giving
        as input the value of the distinct number of parametrizations
        nbr_parametrizations and the stop window stop_window.

        Args:
            distance (float): The threshold for the average distance between
                each parametrization.
            stop_window (int): The number of iterations
            the number of distinct parametrizations should be computed on.
        """
        self.distance = distance
        self.stop_window = stop_window

    def stop_rule(self, history):
        """This method outputs true (ie: do not stop the optimization
        process) if the average distance between the parametrizations tested
        is below the threshold distance over a stop_window number of
        iterations.

        Args:
            history (dict): A dictionary describing the BBO optimization
                history.

        Returns:
            bool: whether or not the optimization process should be
                stopped given the history.
        """
        parametrization = history["parameters"]
        # If the number of iterations for the interval is below the
        # already computed parametrization, return False
        # (aka: do not stop the optimization process)
        if len(parametrization) <= self.stop_window:
            return True
        # Compute the unique parametrization to reduce computation time
        unique_parametrization = np.unique(
            parametrization[-self.stop_window:], axis=0)
        # Compute two by two distance between each parametrization
        avg_distance = 0
        for parametrizations in itertools.combinations(
                unique_parametrization, 2):
            avg_distance += np.linalg.norm(
                parametrizations[0] - parametrizations[1])
        return avg_distance / len(unique_parametrization) > self.distance
