"""This module provides the different tests for the fitness aggregation policy.
"""

import unittest
import numpy as np
from bbo.noise_reduction.fitness_transformation import (
    FitnessTransformation,
    SimpleFitnessTransformation,
)


class TestFitnessAggregation(unittest.TestCase):
    """Tests the proper implementation of the fitness aggregation class.
    """

    def test_fitness_aggregation(self):
        """
        Tests the proper initialization of the class.
        """
        ft = FitnessTransformation()


class TestSimpleFitnessTransformation(unittest.TestCase):
    """
    Tests that proper implementation of the SimpleFitnessTransformation class.
    """

    def test_simple_fitness_transformation(self):
        """
        Tests the proper initialization of the SimpleFitnessTransformation class.
        """
        _ = SimpleFitnessTransformation(estimator=np.mean)

    def test_simple_fitness_transformation_mean(self):
        """Tests the proper computation of the simple fitness transformation
        when using the mean as an estimator.
        """
        sft = SimpleFitnessTransformation(estimator=np.mean)
        history = {
            "fitness": [2, 3, 4, 1],
            "parameters": np.array([[1, 2], [1, 2], [3, 4], [3, 4]]),
            "truncated": [False, False, False, False],
        }
        transformed_history = sft.transform(history)
        np.testing.assert_array_equal(transformed_history["fitness"], [2.5, 2.5])
        np.testing.assert_array_equal(
            transformed_history["parameters"], np.array([[1, 2], [3, 4]])
        )

    def test_simple_fitness_transformation_median(self):
        """Tests the proper computation of the simple fitness transformation
        when using the median as an estimator.
        """
        sft = SimpleFitnessTransformation(estimator=np.std)
        history = {
            "fitness": [2, 3, 4, 1],
            "parameters": np.array([[1, 2], [1, 2], [3, 4], [3, 4]]),
            "truncated": [False, False, False, False],
        }
        transformed_history = sft.transform(history)
        np.testing.assert_array_equal(transformed_history["fitness"], [0.5, 1.5])
        np.testing.assert_array_equal(
            transformed_history["parameters"], np.array([[1, 2], [3, 4]])
        )


if __name__ == "__main__":
    unittest.main()
