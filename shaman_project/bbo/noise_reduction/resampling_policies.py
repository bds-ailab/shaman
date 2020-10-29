"""This module provides resampling policies: they consist in reevaluating some
parametrization several times, in order to get a better estimation of the
impact of these parameters on the performance function.

This allows to be less dependent on the cluster's noise.
"""
import numpy as np
from scipy.stats import binom


class ResamplingPolicy:
    """Abstract parent class for Resampling policies, that all resampling
    implementations must inherit from."""

    def resample(self, history):
        """Given the previous evaluation history, returns a boolean which
        indicates if the last parameters should be re-evaluated.

        Args:
            history (dict): A dictionary with two keys: parameters, which
                contains the parameters already tested by the heuristic, and
                fitness, which contains the corresponding performance measure.

        Returns:
            bool: Whether or not the last parameters should be evaluated again.

        Raises:
            NotImplementedError: All children class should have a resample
                method, else a NotImplementedError is raised.
        """
        raise NotImplementedError


class SimpleResampling(ResamplingPolicy):
    """Simple resampling consists in reevaluating each parametrization the same
    number of times.

    The number of reevaluations is set by an integer nbr_resamples which
    indicates how many resampling should be done.
    """

    def __init__(self, nbr_resamples, *args, **kwargs):
        """Initializes an object of class SimpleResampling.

        Args:
            nbr_resamples (int): The number of times each parametrization
                is to be reevaluated.
        """
        self.nbr_resamples = nbr_resamples

    def resample(self, history):
        """Given the previous evaluation history, returns a boolean which
        indicates if the last parameters has been re-evaluated nbr_resamples
        times.

        Args:
            history (dict): A dictionary with two keys: parameters, which
                contains the parameters already tested by the heuristic, and
                fitness, which contains the corresponding performance measure.

        Returns:
            bool: Whether or not the last parameters has been re-evaluated
                nbr_resamples times.
        """
        parameters_array = np.array(history["parameters"])
        last_elem = parameters_array[-1]
        # Check if there are enough resampling for the last_elem
        return (
            np.sum(
                np.all(
                    parameters_array == last_elem,
                    axis=1)) < self.nbr_resamples
        )


class DynamicResampling(ResamplingPolicy):
    """Generic class for dynamic resampling."""

    def __init__(
        self,
        percentage,
        resampling_schedule=None,
        allow_resampling_schedule=None,
        allow_resampling_start=1,
        *args,
        **kwargs,
    ):
        """Initialize an object of class DynamicResampling."""
        # Check value for percentage
        if percentage <= 0:
            raise ValueError(
                "Dynamic resampling percentage argument should be positive."
            )
        # The element that will be under investigation for resampling
        # In our case, it will be the last element of the history
        self.last_elem_fitness = None
        self.last_elem_nbr = None
        self.total_nbr = None
        # Store the percentage.
        self.percentage = percentage
        # If there is a resampling schedule,
        # the percentage is used as the start
        # of the schedule
        if resampling_schedule:
            self.resampling_schedule = lambda x: percentage * \
                resampling_schedule(x)
        else:
            self.resampling_schedule = lambda x: percentage
        # If there is a allow resampling schedule,
        # the schedule starts at allow_resampling_start
        # Note that the schedule is limited to 2
        if allow_resampling_schedule:
            self.allow_resampling_schedule = (
                lambda x: allow_resampling_start * allow_resampling_schedule(x)
            )
        else:
            self.allow_resampling_schedule = lambda x: allow_resampling_start

    @staticmethod
    def process_last_elem(history):
        """Given a history dictionary, returns information on the last sampled
        element:

        - The number of resamples.
        - The fitness corresponding fitness array.
        """
        # Save as array the parametrization and their corresponding fitness
        parameters_array = np.array(history["parameters"])
        fitness_array = np.array(history["fitness"])
        # Get the last element and its corresponding fitness values
        last_elem = parameters_array[-1]
        print(f"Parameter under consideration: {last_elem}")
        last_elem_fitness = fitness_array[np.all(
            parameters_array == last_elem, axis=1)]
        # Get its number of repetitions
        last_elem_nbr = np.sum(np.all(parameters_array == last_elem, axis=1))
        # Get the total number of iterations
        total_nbr = parameters_array.shape[0]
        return last_elem_fitness, last_elem_nbr, total_nbr

    def resample(self, history):
        """Resample or not."""
        (
            self.last_elem_fitness,
            self.last_elem_nbr,
            self.total_nbr,
        ) = self.process_last_elem(history)
        # Resample if there has been less than two resamples
        if self.last_elem_nbr < 2:
            return True
        # Check if the resampling process should be enabled
        if self.allow_resampling(history):
            # Check if should be resampled
            return self.resampling_rule()
        return False

    def resampling_rule(self):
        """Boolean to evaluate to know if resampling must happen."""
        print(f"IC length: {np.abs(self.ic_length())}")
        print(f"CI threshold: {self.ic_threshold()}")
        return np.abs(self.ic_length()) > self.ic_threshold()

    def allow_resampling(self, history):
        """Defines if resampling should be allowed or not."""
        return True

    def ic_length(self):
        """Computes the IC at threshold % for the fitness contained in
        last_elem_fitness."""
        raise NotImplementedError

    def ic_threshold(self):
        """Computes the threshold value for the IC length."""
        raise NotImplementedError


class DynamicResamplingParametric(DynamicResampling):
    """Dynamic resampling consists in re-evaluating a parametrization until the
    confidence interval around the mean estimator drops down to a certain size.
    We use the definition of the 95% IC, using the unbiased variance estimator,

    which gives it a length of: 2 * 1.96 * (sigma/sqrt(n))
    The parametrization is resampled until the length of the IC goes down a
    certain percentage of the mean.

    It inherits from the ResamplingPolicy class.
    """

    def ic_length(self):
        """Computes the IC at threshold % for the fitness contained in
        last_elem_fitness."""
        return 2 * 1.96 * np.std(self.last_elem_fitness) / \
            np.sqrt(self.last_elem_nbr)

    def ic_threshold(self):
        """Computes the threshold value for the IC length."""
        percentage = self.resampling_schedule(self.total_nbr)
        return np.abs(percentage * np.mean(self.last_elem_fitness))


class DynamicResamplingParametric2(DynamicResamplingParametric):
    """Dynamic resampling using parametric tests."""

    def __init__(self, percentage, *args, **kwargs):
        """Initialize an object of class DynamicResamplingParametric2, which
        inherits from the class DynamicResamplingParametric and adds a check on
        the value of the fitness before performing the resampling."""
        super().__init__(percentage, *args, **kwargs)

    def allow_resampling(self, history):
        """Compares the current value to other statistics to the history."""
        current_median = np.median(history["fitness"])
        return (
            np.median(self.last_elem_fitness)
            <= self.allow_resampling_schedule(self.total_nbr) * current_median
        )


class DynamicResamplingNonParametric(DynamicResampling):
    """Class for performing dynamic resampling using non-parametric confidence
    interval around the median.

    Taken from: http://www.stat.umn.edu/geyer/old03/5102/notes/rank.pdf
    """

    def __init__(self, percentage, threshold, *args, **kwargs):
        """Initialize an object of class DynamicResamplingNonParametric.

        Args:
            percentage (float): A float located between 0 and 1, which gives
                the percentage of the median the IC length should go under.
            threshold (float): The value of the threshold the closest to
                the available one.
        """
        if percentage <= 0:
            raise ValueError(
                "Dynamic resampling percentage argument should be positive."
            )
        if not 0 <= threshold <= 1:
            raise ValueError("Threshold should be positive and inferior to 1.")
        super().__init__(percentage, *args, **kwargs)
        self.threshold = threshold

    def get_interval_rank(self):
        """Get the rank of the individuals matching the closest to the
        requested interval.

        Taken from: http://www.stat.umn.edu/geyer/old03/5102/notes/rank.pdf
        """
        probs = 1 - 2 * binom.cdf(
            np.arange(self.last_elem_nbr / 2), self.last_elem_nbr, 1 / 2
        )
        return np.argmin(np.sqrt((self.threshold - probs) ** 2))

    def get_ci_bounds(self):
        """Return CI bounds at threshold %."""
        # Compute the location of the first and last value of the distribution
        threshold_location = self.get_interval_rank()
        # Return bounds based on threshold
        return (
            self.last_elem_fitness[threshold_location],
            self.last_elem_fitness[-(threshold_location + 1)],
        )

    def ic_length(self):
        """Computes the length CI at threshold % for the fitness contained in
        last_elem_fitness."""
        # Get bounds of CI
        inf_bound, sup_bound = self.get_ci_bounds()
        # Compute the length of the IC
        return sup_bound - inf_bound

    def ic_threshold(self):
        """Computes the threshold value for the IC length."""
        percentage = self.resampling_schedule(self.total_nbr)
        return np.abs(percentage * np.median(self.last_elem_fitness))


class DynamicResamplingNonParametric2(DynamicResamplingNonParametric):
    """Dynamic resampling relying on non-parametric confidence interval + stop
    rule for non-promising parametrizations."""

    def __init__(self, percentage, threshold, *args, **kwargs):
        """Initialize an object of class DynamicResamplingParametric2, which
        inherits from the class DynamicResamplingParametric and adds a check on
        the value of the fitness before performing the resampling."""
        super().__init__(percentage, threshold, *args, **kwargs)

    def allow_resampling(self, history):
        """Compares the current value to other statistics to the history."""
        if self.last_elem_nbr < 2:
            return True
        current_median = np.median(history["fitness"])
        return (
            np.median(self.last_elem_fitness)
            <= self.allow_resampling_schedule(self.total_nbr) * current_median
        )
