# Copyright 2020 BULL SAS All rights reserved
"""This module provides the different tests for the resampling policies.
"""

import unittest
import numpy as np

from bbo.noise_reduction.resampling_policies import (
    ResamplingPolicy,
    SimpleResampling,
    DynamicResampling,
    DynamicResamplingParametric,
    DynamicResamplingNonParametric,
    DynamicResamplingNonParametric2,
)



class TestResampling(unittest.TestCase):
    """Tests the proper implementation of the parent resampling
    class.
    """

    def test_parent_class(self):
        """Test the initialization of the Resampling parent
        class.
        """
        resampling_policy = ResamplingPolicy()

    def test_not_implemented(self):
        """Test that a not implemented error is raised when calling the
        resample method"""
        resampling_policy = ResamplingPolicy()
        with self.assertRaises(NotImplementedError):
            resampling_policy.resample(history={})


class TestSimpleResampling(unittest.TestCase):
    """Tests the SimpleResampling class.
    """

    def test_simple_resampling_resample(self):
        """Tests that the parameter are properly resampled when the
        last parameter should be resampled.
        """
        history = {
            "fitness": np.array([10, 5, 4, 2, 15, 20]),
            "parameters": np.array([[1, 2], [2, 3], [1, 3], [4, 3], [2, 1], [2, 1]]),
        }
        resampler = SimpleResampling(nbr_resamples=3)
        self.assertTrue(resampler.resample(history))

    def test_simple_resampling_no_resample(self):
        """Tests that the parameter are properly resampled when the
        last parameter should not be resampled.
        """
        history = {
            "fitness": np.array([10, 5, 4, 2, 15, 20]),
            "parameters": np.array([[1, 2], [2, 3], [1, 3], [2, 1], [2, 1], [2, 1]]),
        }
        resampler = SimpleResampling(nbr_resamples=3)
        self.assertFalse(resampler.resample(history))

    def test_simple_resampling_no_sequential(self):
        """Tests that when the samples are not sequentially ordered,
        the resampling still happens properly.
        """
        history = {
            "fitness": np.array([10, 5, 4, 2, 15, 20]),
            "parameters": np.array([[1, 2], [2, 3], [1, 3], [4, 3], [2, 1], [2, 1]]),
        }
        resampler = SimpleResampling(nbr_resamples=2)
        self.assertFalse(resampler.resample(history))


class TestDynamicResampling(unittest.TestCase):
    """Tests the abstract class of dynamic resampling.
    """

    def test_initialization(self):
        """Tests the proper initialization of the class.
        """
        dynamic_resampling = DynamicResampling(percentage=0.5)

    def test_resampling_schedule_None(self):
        """Tests the good definition of the resampling schedule when set to None.
        """
        dynamic_resampling = DynamicResampling(percentage=0.5)
        self.assertEqual(0.5, dynamic_resampling.resampling_schedule(1))

    def test_resampling_schedule(self):
        """Tests the good definition of the resampling schedule.
        """
        dynamic_resampling = DynamicResampling(
            percentage=0.5, resampling_schedule="logarithmic"
        )
        self.assertEqual(0.5 / np.log(2), dynamic_resampling.resampling_schedule(1))

    def test_allow_resampling_schedule_None(self):
        """Tests that the allow resampling schedule behaves as expected when set to None.
        """
        dynamic_resampling = DynamicResampling(percentage=0.5)
        self.assertEqual(1, dynamic_resampling.allow_resampling_schedule(1))

    def test_allow_resampling_schedule(self):
        """Tests that the allow resampling schedule behaves as expected when set to a value.
        """
        dynamic_resampling = DynamicResampling(
            percentage=0.5,
            allow_resampling_start=5,
            allow_resampling_schedule="logarithmic",
        )
        self.assertEqual(5 / np.log(2), dynamic_resampling.allow_resampling_schedule(1))


class TestDynamicResamplingParametric(unittest.TestCase):
    """Tests that the DynamicResamplingParametric class behaves as expected.
    """

    def test_error_percentage(self):
        """Tests that dynamic resampling raises an error when the percentage is below 0.
        """
        with self.assertRaises(ValueError):
            DynamicResamplingParametric(percentage=-0.1)

    def test_dynamic_resampling_formula(self):
        """
        Tests that the computation performs what is expected.
        """
        test_dynamic_resampling = DynamicResamplingParametric(0.2)
        history = {
            "fitness": np.array([10, 5, 4, 14, 15, 16]),
            "parameters": np.array([[1, 2], [2, 3], [1, 3], [2, 1], [2, 1], [2, 1]]),
        }
        fitness = np.array(history["fitness"])
        parameters = np.array(history["parameters"])
        last_elem_fitness = fitness[np.all(parameters == parameters[-1], axis=1)]
        ic_len = 2 * 1.96 * np.std(last_elem_fitness) / len(last_elem_fitness)
        expected_resampling = ic_len > 0.2 * np.mean(last_elem_fitness)
        resampling = test_dynamic_resampling.resample(history)
        self.assertEqual(resampling, expected_resampling)

    def test_dynamic_resampling_resample(self):
        """
        Tests that there is resampling when the IC is larger than the threshold.
        """
        test_dynamic_resampling = DynamicResamplingParametric(0.9)
        history = {
            "fitness": np.array([10, 5, 4, 12, 15, 20]),
            "parameters": np.array([[1, 2], [2, 3], [1, 3], [2, 1], [2, 1], [2, 1]]),
        }
        self.assertFalse(test_dynamic_resampling.resample(history))

    def test_dynamic_no_resample(self):
        """
        Tests that there is no resampling when the size of the IC is lower than the threshold.
        """
        test_dynamic_resampling = DynamicResamplingParametric(0.2)
        history = {
            "fitness": np.array([10, 5, 4, 12, 15, 20]),
            "parameters": np.array([[1, 2], [2, 3], [1, 3], [2, 1], [2, 1], [2, 1]]),
        }
        self.assertTrue(test_dynamic_resampling.resample(history))

    def test_dynamic_resampling_schedule(self):
        """
        Tests that using a dynamic resampling schedule affects the resampling process.
        """
        history = {
            "fitness": np.array([10, 5, 4, 10, 11, 11.5]),
            "parameters": np.array([[1, 2], [2, 3], [1, 3], [2, 1], [2, 1], [2, 1]]),
        }
        # Without a resampling schedule, there is no resampling
        test_dynamic_resampling = DynamicResamplingParametric(0.2)
        self.assertFalse(test_dynamic_resampling.resample(history))
        # With a resampling schedule, there is a resampling
        test_dynamic_resampling = DynamicResamplingParametric(
            0.2, resampling_schedule="logarithmic"
        )
        self.assertTrue(test_dynamic_resampling.resample(history))


class TestDynamicNonParametricResampling(unittest.TestCase):
    """Tests the behavior of the non parametric resampling method.
    """

    def test_dynamic_resampling_non_parametric_init(self):
        """Tests that the initialization of the class DynamicResamplingNonParametric behaves as expected.
        """
        with self.assertRaises(ValueError):
            DynamicResamplingNonParametric(percentage=-0.1, threshold=0.9)
        with self.assertRaises(ValueError):
            DynamicResamplingNonParametric(percentage=0.1, threshold=1.1)

    def test_dynamic_resampling_non_parametric_one_resample(self):
        """Tests that when there is only one resampling for a parametrization the parametrization
        is automatically repeated.
        """
        test_dynamic_resampling = DynamicResamplingNonParametric(0.2, threshold=0.9)
        history = {
            "fitness": np.array([10, 5, 4, 12]),
            "parameters": np.array([[1, 2], [2, 3], [1, 3], [2, 1]]),
        }
        self.assertTrue(test_dynamic_resampling.resample(history))

    def test_dynamic_resampling_non_parametric_no_resample(self):
        """Tests that there is no resampling when the size of the IC is lower than the threshold.
        """
        test_dynamic_resampling = DynamicResamplingNonParametric(0.2, threshold=0.9)
        history = {
            "fitness": np.array([10, 5, 4, 12, 12, 12, 12]),
            "parameters": np.array(
                [[1, 2], [2, 3], [1, 3], [2, 1], [2, 1], [2, 1], [2, 1]]
            ),
        }
        self.assertFalse(test_dynamic_resampling.resample(history))

    def test_dynamic_resampling_non_parametric_resample(self):
        """Tests that there is resampling when the size of the IC is higher than the threshold.
        """
        test_dynamic_resampling = DynamicResamplingNonParametric(0.2, threshold=0.9)
        history = {
            "fitness": np.array([10, 5, 4, 8, 10, 12, 16]),
            "parameters": np.array(
                [[1, 2], [2, 3], [1, 3], [2, 1], [2, 1], [2, 1], [2, 1]]
            ),
        }
        self.assertTrue(test_dynamic_resampling.resample(history))

    def test_dynamic_resampling_effect_threshold(self):
        """Tests that the resampling behavior depends on the error of the IC.
        """
        test_dynamic_resampling = DynamicResamplingNonParametric(0.2, threshold=0.95)
        history = {
            "fitness": np.array([10, 5, 4, 8, 10, 12, 16, 15, 10, 12, 16, 14]),
            "parameters": np.array(
                [
                    [1, 2],
                    [2, 3],
                    [1, 3],
                    [2, 1],
                    [2, 1],
                    [2, 1],
                    [2, 1],
                    [2, 1],
                    [2, 1],
                    [2, 1],
                    [2, 1],
                    [2, 1],
                ]
            ),
        }
        self.assertTrue(test_dynamic_resampling.resample(history))
        test_dynamic_resampling = DynamicResamplingNonParametric(0.2, threshold=0.1)
        self.assertFalse(test_dynamic_resampling.resample(history))

    def test_dynamc_resamplingschedule(self):
        """Tests that the resampling behaves as expected when using a resampling schedule.
        """
        test_dynamic_resampling = DynamicResamplingNonParametric(
            0.2, threshold=0.95, resampling_schedule=""
        )
        history = {
            "fitness": np.array([10, 5, 4, 8, 10, 12, 16, 15, 10, 12, 16, 14]),
            "parameters": np.array(
                [
                    [1, 2],
                    [2, 3],
                    [1, 3],
                    [2, 1],
                    [2, 1],
                    [2, 1],
                    [2, 1],
                    [2, 1],
                    [2, 1],
                    [2, 1],
                    [2, 1],
                    [2, 1],
                ]
            ),
        }


class TestDynamicNonParametricResampling2(unittest.TestCase):
    """Tests the behavior of the non parametric resampling method.
    """

    def test_dynamic_resampling_non_parametric_init(self):
        """Tests that the initialization of the class DynamicResamplingNonParametric behaves as expected.
        """
        with self.assertRaises(ValueError):
            DynamicResamplingNonParametric2(percentage=-0.1, threshold=0.9)
        with self.assertRaises(ValueError):
            DynamicResamplingNonParametric2(percentage=0.1, threshold=1.1)

    def test_dynamic_resampling_non_parametric_one_resample(self):
        """Tests that when there is only one resampling for a parametrization the parametrization
        is automatically repeated.
        """
        test_dynamic_resampling = DynamicResamplingNonParametric2(0.2, threshold=0.9)
        history = {
            "fitness": np.array([10, 5, 4, 12]),
            "parameters": np.array([[1, 2], [2, 3], [1, 3], [2, 1]]),
        }
        self.assertTrue(test_dynamic_resampling.resample(history))

    def test_dynamic_resampling_non_parametric_no_resample(self):
        """Tests that there is no resampling when the median of the resampled data point is higher
        than the current median.
        """
        test_dynamic_resampling = DynamicResamplingNonParametric2(0.2, threshold=0.9)
        history = {
            "fitness": np.array([10, 5, 4, 12, 12]),
            "parameters": np.array([[1, 2], [2, 3], [1, 3], [2, 1], [2, 1]]),
        }
        self.assertFalse(test_dynamic_resampling.resample(history))

    def test_dynamic_resampling_non_parametric_resample2(self):
        """Tests that there is resampling when the size of the IC is higher than the threshold and
        the median of the resampled data point lower than the current median.
        """
        test_dynamic_resampling = DynamicResamplingNonParametric2(0.2, threshold=0.9)
        history = {
            "fitness": np.array([10, 5, 4, 2, 5, 3, 7]),
            "parameters": np.array(
                [[1, 2], [2, 3], [1, 3], [2, 1], [2, 1], [2, 1], [2, 1]]
            ),
        }
        self.assertTrue(test_dynamic_resampling.resample(history))

    def test_dynamic_resampling_effect_threshold(self):
        """Tests that the resampling behavior depends on the error of the IC.
        """
        test_dynamic_resampling = DynamicResamplingNonParametric2(0.2, threshold=0.95)
        history = {
            "fitness": np.array([20, 5, 4, 8, 10, 12, 16, 15, 10, 12, 16, 13]),
            "parameters": np.array(
                [
                    [1, 2],
                    [2, 3],
                    [1, 3],
                    [2, 1],
                    [2, 1],
                    [2, 1],
                    [2, 1],
                    [2, 1],
                    [2, 1],
                    [2, 1],
                    [2, 1],
                    [2, 1],
                ]
            ),
        }
        self.assertTrue(test_dynamic_resampling.resample(history))
        test_dynamic_resampling = DynamicResamplingNonParametric2(0.2, threshold=0.1)
        self.assertFalse(test_dynamic_resampling.resample(history))


if __name__ == "__main__":
    unittest.main()
