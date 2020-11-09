# Copyright 2020 BULL SAS All rights reserved
"""
Tests that the initial parametrizations methods work properly.
"""
# Disable the could be a function for unit testing
# pylint: disable=no-self-use
# Disable name too longs (necessary for clarity in testing)
# pylint: disable=invalid-name

import unittest
import numpy as np
from numpy.testing import assert_array_equal

from bbo.initial_parametrizations import (
    uniform_random_draw,
    latin_hypercube_sampling,
    hybrid_lhs_uniform_sampling,
)


class TestUniformRandomDraws(unittest.TestCase):
    """
    Tests that the initial drawing of parameters work properly.
    """

    def setUp(self):
        """
        Sets up the testing procedure by setting the random seed of the project.
        """
        np.random.seed(2)

    def test_uniform_random_draw_array(self):
        """
        Tests that the uniform random draw functions behaves as expected when the parameter space
        is described by arrays.
        """
        number_of_parameters = 2
        parameter_space = np.array([[1, 2, 3], [4, 5, 6, 7], [8, 9, 10]])
        expected_result = np.array([[1, 4, 10], [2, 6, 8]])
        actual_result = uniform_random_draw(number_of_parameters, parameter_space)
        assert_array_equal(actual_result, expected_result)

    def test_uniform_random_draw_array_large(self):
        """
        Tests that the uniform random draw functions behaves as expected when the parameter space
        is described by arrays.
        """
        number_of_parameters = 5
        parameter_space = np.array([[1, 2, 3], [4, 5, 6, 7], [8, 9, 10]])
        expected_result = np.array(
            [[1, 7, 9], [2, 4, 10], [1, 7, 8], [3, 6, 8], [3, 5, 8]]
        )
        actual_result = uniform_random_draw(number_of_parameters, parameter_space)
        assert_array_equal(actual_result, expected_result)

    def test_uniform_random_draw_range(self):
        """
        Tests that the uniform random draw works as expected when given a range as a parametric
        space.
        """
        number_of_parameters = 2
        parameter_space = np.array(
            [np.arange(1, 10), np.arange(10, 20), np.arange(20, 30)]
        )
        expected_result = np.array([[9, 16, 28], [9, 12, 27]])
        actual_result = uniform_random_draw(number_of_parameters, parameter_space)
        assert_array_equal(actual_result, expected_result)

    def test_uniform_random_draw_except(self):
        """
        Tests that the uniform random draw works as expected when given a range 1D parametric
        space.
        """
        number_of_parameters = 2
        parameter_space = np.array([[[1, 2, 3], [4, 5, 6, 7], [8, 9, 10]]])
        expected_result = np.array([[1, 4, 10], [2, 6, 8]])
        actual_result = uniform_random_draw(number_of_parameters, parameter_space)
        assert_array_equal(actual_result, expected_result)

    def test_latin_hypercube_sampling(self):
        """
        Tests that the latin hypercube sampling works properly.
        """
        number_of_parameters = 4
        parameter_space = np.array([np.arange(1, 10), np.arange(1, 5)])
        actual_result = latin_hypercube_sampling(number_of_parameters, parameter_space)
        expected_result = np.array([[5.0, 1.0], [4.0, 2.0], [9.0, 3.0], [1.0, 4.0]])
        assert_array_equal(actual_result, expected_result)

    def test_latin_hypercube_sampling_too_many_parameters(self):
        """
        Tests that the latin hypercube sampling returns an Assertion Error when the user asks for
        more parameter draws than the size of the smallest dimension.
        """
        number_of_parameters = 6
        parameter_space = np.array([np.arange(1, 10), np.arange(1, 5)])
        with self.assertRaises(AssertionError):
            latin_hypercube_sampling(number_of_parameters, parameter_space)

    def test_non_collapse_property(self):
        """
        Tests that the non collapse property of the latin hypercube is respected, meaning that
        there is no duplicate column values.
        """
        np.random.seed(10)
        number_of_parameters = 4
        parameter_space = np.array([np.arange(1, 10), np.arange(1, 5)])
        actual_result = latin_hypercube_sampling(number_of_parameters, parameter_space)
        len_unique_values = [len(np.unique(axis)) for axis in actual_result.T]
        dim_size = [value == number_of_parameters for value in len_unique_values]
        self.assertTrue(all(dim_size), "Collapsible property was not respected.")

    def test_hybrid_lhs_uniform_sampling_small(self):
        """
        Tests that the hybride sampling works like the latin hypercube sampling if the number of
        parameter is less than the size of the smallest sample.
        """
        number_of_parameters = 4
        parameter_space = np.array([np.arange(1, 10), np.arange(1, 5)])
        actual_result = hybrid_lhs_uniform_sampling(
            number_of_parameters, parameter_space
        )
        np.random.seed(2)
        expected_result = latin_hypercube_sampling(
            number_of_parameters, parameter_space
        )
        assert_array_equal(actual_result, expected_result)

    def test_hybrid_lhs_uniform_sampling_large(self):
        """
        Tests that the latin hypercube sampling with random uniform works properly.
        """
        number_of_parameters = 8
        parameter_space = np.array([np.arange(1, 10), np.arange(1, 5)])
        actual_result = hybrid_lhs_uniform_sampling(
            number_of_parameters, parameter_space
        )
        np.random.seed(2)
        lhs = latin_hypercube_sampling(4, parameter_space)
        ur = uniform_random_draw(4, parameter_space)
        assert_array_equal(actual_result, np.append(lhs, ur, axis=0))


if __name__ == "__main__":
    unittest.main()
