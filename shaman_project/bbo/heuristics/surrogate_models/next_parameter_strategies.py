# Copyright 2020 BULL SAS All rights reserved
"""This module contains different strategies used to compute the next point to
evaluate when modeling the function with surrogate models. There exists in the
literature three main methods to compute this parameter:

- Using the surrogate model as the merit function and look for its minimum by
using various heuristics (CMA, LBFGS, etc ...)
- Using some probabilistic properties of the surrogate model (for example after
having regressed it using Gaussian Processes) and using those properties to
compute "probability of improvements" or expected gains.
"""

# Ignore unused argument kwargs
# pylint: disable=unused-argument

import numpy as np
from scipy.optimize import minimize
from scipy.special import erf
import cma

from bbo.initial_parametrizations import uniform_random_draw


def _norm_pdf(x, mean, sigma):
    """Compute probability density for Gaussian distribution."""
    return (
        1 / (np.sqrt(np.pi * 2) * sigma) *
        np.exp(-((x - mean) ** 2) / (2 * sigma ** 2))
    )


def _norm_cdf(x, mean, sigma):
    """Compute distribution function for Gaussian distribution."""
    return 1 / 2 * (1 + erf((x - mean) / (sigma * np.sqrt(2))))


def l_bfgs_b_minimizer(func, ranges, **kwargs):
    """Apply L-BFGS-B algorithm on a function, constrained by the bounds in the
    range argument. The function used in the one implemented in the
    numpy.optimize package. The initialization of the algorithm is performed by
    a random choice on the grid.

    Args:
        func (function): The function to optimize.
        ranges (numpy array of numpy arrays): The parameter space.

    Returns:
        float: The minimum found of the function.
    """
    bounds = [(min(range_), max(range_)) for range_ in ranges]
    x_0 = uniform_random_draw(1, ranges)
    min_ = minimize(func, x0=x_0, method="L-BFGS-B", bounds=bounds)
    return min_.x


def cma_optimizer(func, ranges, sigma=0.5, **kwargs):
    """Applies the CMA optimizer upon a given function on the grid described in
    the ranges argument. The function used for performing optimization in the
    function available in the cma package.

    Args:
        func (function): The function to optimize using CMA.
        ranges (numpy array of numpy arrays): The parameter grid on which
            to optimize the function.
        sigma (float): The value for the sigma (the step size)

    Returns:
        float: The minimum of the function.
    """
    # compute the minimum and the maximum of each dimension of the grid
    mins = list()
    maxs = list()
    for _range in ranges:
        mins.append(min(_range))
        maxs.append(max(_range))
    bound = (mins, maxs)
    x_0 = uniform_random_draw(1, ranges)
    evolution_strategy = cma.CMAEvolutionStrategy(x_0, sigma,
                                                  {"bounds": bound})
    evolution_strategy.optimize(func)
    return evolution_strategy.result.xbest


def compute_maximum_probability_improvement(current_optimum, means, stds):
    """Given a current optimum, the estimated means and the estimated standard
    error, return the value of the maximum probability improvement. If the
    standard error is estimated to be 0 for a given data point, the expected
    improvement is set to 0.

    Args:
        current_optimum (float): The current best parametrization.
        means (np.array): A numpy array containing the means of each
            data point.
        stds (np.array): A numpy array containing the standard error of
            each data point.
    """
    flattened_means = means.flatten()
    with np.errstate(divide="ignore"):
        maximum_improvement = _norm_cdf(current_optimum, flattened_means, stds)
        maximum_improvement[np.isnan(maximum_improvement)] = 0.0
    return maximum_improvement


def maximum_probability_improvement(func, ranges, previous_evaluations):
    """Given a surrogate function that was regressed by a method that estimates
    both the mean and the variance of each data point, computes the probability
    of improvement at each data point on the grid. This probability is computed
    using a closed form formula that makes use of the gaussian density
    function. It amounts to the distribution a binary variable whose value is 1
    if the current value under evaluation is better than the estimated optimum
    and 0 if not.

    It returns the data point with the highest probability of improvement among
    all the ranges.

    Args:
        func (function): the prediction function.
            Careful: Must possess an argument return_std that can be set to
            True. For example, estimating the function using Gaussian Process
            via sklearn is a way to proceed.
        ranges (numpy array of numpy arrays): the parameter grid to evaluate
            the function upon.
        previous_evaluations (numpy array): the previous evaluations
            of the function.

    Returns:
        numpy array: The data point with the highest probability of
            improvement.
    """
    combination_ranges = np.array(
        np.meshgrid(*ranges)).T.reshape(-1, len(ranges))
    try:
        mean, sigma = func(combination_ranges, return_std=True)
    except TypeError:
        raise TypeError(
            "In order to use Expected Improvement, you have to use a"
            "regression method which estimates the mean and the standard"
            "deviation of the black-box function."
        )

    current_optimum = min(previous_evaluations)
    maximum_improvement = compute_maximum_probability_improvement(
        current_optimum, mean, sigma
    )
    return combination_ranges[np.argmax(maximum_improvement)]


def compute_expected_improvement(current_optimum, means, stds):
    """Given a current optimum, the estimated means and the estimated standard
    error, return the value of the expected improvement. If the standard error
    is estimated to be 0 for a given data point, the expected improvement is
    set to 0.

    Args:
        current_optimum (float): The current best parametrization.
        means (np.array): A numpy array containing the means of each
            data point.
        stds (np.array): A numpy array containing the standard error of
            each data point.
    """
    # flattened means, else, memory error
    flattened_means = means.flatten()
    with np.errstate(divide="ignore"):
        expected_imp = (current_optimum - flattened_means) * _norm_cdf(
            current_optimum, flattened_means, stds
        ) + stds * _norm_pdf(current_optimum, flattened_means, stds)
        expected_imp[stds == 0] = 0.0
    return expected_imp


def expected_improvement(func, ranges, previous_evaluations):
    """Given a surrogate function that was regressed by a method that estimates
    both the mean and the variance of each data point, computes the expected
    improvement at each data point for the grid of possible parametrization.
    This probability is computed using a closed form formula that makes use of
    the gaussian density function. It amounts to computing the expected gain of
    the a random variable which is the current data point minus the current
    optimum.

    This method returns the data point with the highest expected improvement.

    Args:
        func (function): The prediction function on which to compute the
            expected improvement.
            CAREFUL: Must possess an argument return_std that can be set
            to True.
            For example, estimating the function using Gaussian Process
            via sklearn is a way to proceed.
        ranges (numpy array of numpy arrays): the parameter grid to evaluate
            the function upon.
        previous_evaluations (numpy array): the previous evaluations of the
            function.

    Returns:
        numpy array: The data point from ranges which has the highest
            expected improvement.
    """
    # compute all possible combinations of parameters
    combination_ranges = np.array(
        np.meshgrid(*ranges)).T.reshape(-1, len(ranges))
    try:
        mean, sigma = func(combination_ranges, return_std=True)
    except TypeError:
        raise TypeError(
            "In order to use Expected Improvement, you have to use a"
            "regression method which estimates the mean and the standard"
            "deviation of the black-box function."
        )
    current_optimum = min(previous_evaluations)
    expected_imp = compute_expected_improvement(current_optimum, mean, sigma)
    if np.sum(expected_imp) == 0:
        return combination_ranges[np.random.choice(
            np.arange(len(combination_ranges)))]
    else:
        return combination_ranges[np.argmax(expected_imp)]
