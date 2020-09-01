#!/usr/bin/env python
"""
This module proposes unit tests for the configuration_parser module.
"""
__copyright__ = """
Copyright (C) 2020 Bull S. A. S. - All rights reserved
Bull, Rue Jean Jaures, B.P.68, 78340, Les Clayes-sous-Bois, France
This is not Free or Open Source software.
Please contact Bull S. A. S. for details about its license.
"""

import os
import unittest
import numpy as np
from bbo.heuristics.genetic_algorithm.selections import tournament_pick
from bbo.heuristics.genetic_algorithm.crossover import single_point_crossover
from bbo.heuristics.genetic_algorithm.mutations import mutate_chromosome_to_neighbor
from little_shaman.configuration_parser import ShamanConfig

FILE_DIR = os.path.dirname(os.path.realpath(__file__))
TEST_DATA = os.path.join(FILE_DIR, "test_data")
CONFIG = os.path.join(TEST_DATA, "test_config.cfg")
CONFIG_ASYNC_DEFAULT = os.path.join(
    TEST_DATA, "config_shaman_async_default.cfg")
CONFIG_ASYNC_INT = os.path.join(TEST_DATA, "config_shaman_async_int.cfg")
CONFIG_ASYNC_WRONG_MAX_STEP = os.path.join(
    TEST_DATA, "config_shaman_async_wrong_max_step.cfg")
CONFIG_ASYNC_NO_DEFAULT = os.path.join(
    TEST_DATA, "config_shaman_async_no_default.cfg")
CONFIG_ASYNC_MEDIAN = os.path.join(TEST_DATA, "config_shaman_async_median.cfg")
CONFIG_NOISE_REDUCTION = os.path.join(
    TEST_DATA, "test_config_noise_reduction.cfg")


class TestShamanConfig(unittest.TestCase):
    """ TestCase used to test the 'ShamanConfig' class. """

    def setUp(self):
        """ Initialize the variable required for the tests. """
        self.sc = ShamanConfig(configuration_file=CONFIG,
                               accelerator_name='fiol')

    def test_init(self):
        """ Test the attribute of the class 'ShamanConfig' are properly set. """
        self.assertEqual(self.sc.accelerator_name, 'FIOL')

    def test_change_parameters(self):
        """ Tests that calling an accelerator MY_acc properly configures the accelerator and turn it into uppercase."""
        sc = ShamanConfig(CONFIG, 'MY_acc')
        self.assertEqual(sc.accelerator_name, 'MY_ACC')

    def test_experiment_parameters_config(self):
        """ Test the properties of the EXPERIMENT section are properly set. """
        self.assertFalse(self.sc.with_ioi)
        self.assertTrue(self.sc.default_first)
        self.assertFalse(self.sc.pruning)
        self.assertEqual(self.sc.max_step_duration, None)

    def test_experiment_parameters_async_max_step_default(self):
        """Tests that the configuration is properly read when the
        max default is set to an integer value."""
        sc = ShamanConfig(CONFIG_ASYNC_DEFAULT, 'fiol')
        self.assertTrue(sc.pruning)
        self.assertEqual(sc.max_step_duration, "default")

    def test_experiment_parameters_async_max_step_int(self):
        """Tests that the configuration is properly read when the
        max default is set to 'default'."""
        sc = ShamanConfig(CONFIG_ASYNC_INT, 'fiol')
        self.assertTrue(sc.pruning)
        self.assertEqual(sc.max_step_duration, 10)

    def test_experiment_parameters_async_wrong_max_step(self):
        """Tests that an error is raised when the max_step_duration is wrongly specified."""
        sc = ShamanConfig(CONFIG_ASYNC_WRONG_MAX_STEP, 'fiol')
        with self.assertRaises(ValueError):
            sc.max_step_duration

    def test_experiment_parameters_async_wrong_default(self):
        """Tests that an error is raised when the default_first property is set to False and
        the max_step_duration is set to 'default'"""
        sc = ShamanConfig(CONFIG_ASYNC_NO_DEFAULT, 'fiol')
        with self.assertRaises(ValueError):
            sc.max_step_duration

    def test_experiment_parameters_async_median(self):
        """Tests that the max step duration is properly read when given a function.
        """
        sc = ShamanConfig(CONFIG_ASYNC_MEDIAN, 'fiol')
        self.assertTrue(callable(sc.max_step_duration))

    def test_bbo_kwargs_config(self):
        """ Test the property 'bbo_kwargs' is properly set. """
        expected_dict = {
            'heuristic': 'genetic_algorithm',
            'initial_sample_size': 2,
            'selection_method': tournament_pick,
            'crossover_method': single_point_crossover,
            'mutation_method': mutate_chromosome_to_neighbor,
            'mutation_rate': 0.4,
            'elitism': False
        }
        self.assertDictEqual(self.sc.bbo_kwargs, expected_dict)

    def test_acc_parameter_names_config(self):
        """ Test the property 'acc_parameter_names' is properly set. """
        expected_list = ["fiol_param_1", "fiol_param_2"]
        self.assertListEqual(self.sc.acc_parameter_names, expected_list)

    def test_acc_parameter_space_config(self):
        """ Test the property 'acc_parameter_space' is properly set. """
        expected_array = np.array([np.array([5, 6, 7, 8, 9, 10]),
                                   np.array([10, 30, 50, 70, 90])])
        for arr, exp_arr in zip(self.sc.acc_parameter_space, expected_array):
            np.testing.assert_array_equal(arr, exp_arr)

    def test_api_host_config(self):
        """ Test the property dtabase host is properly set. """
        self.assertEqual(self.sc.api_parameters['host'], "localhost")

    def test_api_port_config(self):
        """ Test the property database port is properly set. """
        self.assertEqual(self.sc.api_parameters['port'], "5000")


class TestStaticShamanConfig(unittest.TestCase):
    """ TestCase used to test the static method of the 'ShamanConfig' class. """

    def test_check_range_format(self):
        """ Test the 'check_range_format' method returns the proper bool according to the range
        set. """
        self.assertTrue(ShamanConfig.check_range_format("{1, 10, 1}"))
        self.assertTrue(ShamanConfig.check_range_format("{123, 1, 456}"))
        self.assertFalse(ShamanConfig.check_range_format("1, 10, 1"))
        self.assertFalse(ShamanConfig.check_range_format("[1, 10, 1]"))
        self.assertFalse(ShamanConfig.check_range_format("[1.1, 2.2, 1]"))

    def test_create_range(self):
        """ Test the 'create_range' method returns the proper list according to the range
        set. """
        self.assertListEqual(ShamanConfig.create_range(
            "{1, 5, 1}"), [1, 2, 3, 4, 5])

    def test_create_range_except(self):
        """ Test the 'create_range' raises the ValueError if the list is not set properly. """
        self.assertRaises(ValueError, ShamanConfig.create_range, "1, 5, 1")


class TestConfigNoiseReduction(unittest.TestCase):
    """Tests that the configuration is correctly parsed when there is a noise reduction section.
    """

    def test_parse_noise_reduction(self):
        """Tests that the information concerning the noise reduction is properly parsed.
        """
        shaman_config = ShamanConfig(CONFIG_NOISE_REDUCTION, 'FIOL')
        noise_reduction_dict = {
            "resampling_policy": "simple_resampling",
            "nbr_resamples": 3
        }
        self.assertEqual(
            shaman_config.bbo_kwargs["resampling_policy"], noise_reduction_dict["resampling_policy"])
        self.assertEqual(
            shaman_config.bbo_kwargs["nbr_resamples"], noise_reduction_dict["nbr_resamples"])


if __name__ == '__main__':
    unittest.main(verbosity=2)
