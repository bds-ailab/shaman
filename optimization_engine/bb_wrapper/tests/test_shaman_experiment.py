#!/usr/bin/env python
"""
This module proposes unit tests for the shaman_experiment module.
"""
from __future__ import division, absolute_import, generators, print_function, unicode_literals,\
                       with_statement, nested_scopes # ensure python2.x compatibility

__copyright__ = """
Copyright (C) 2020 Bull S. A. S. - All rights reserved
Bull, Rue Jean Jaures, B.P.68, 78340, Les Clayes-sous-Bois, France
This is not Free or Open Source software.
Please contact Bull S. A. S. for details about its license.
"""

import os
import unittest
from unittest.mock import patch
import glob
from shutil import copy, rmtree
from datetime import datetime
from bbo.optimizer import BBOptimizer
from little_shaman.acc_blackbox import AccBlackBox
from little_shaman.shaman_experiment import ShamanExperiment

CURRENT_DIR = os.getcwd()
FILE_DIR = os.path.dirname(os.path.realpath(__file__))
TEST_DATA = os.path.join(FILE_DIR, "test_data")
CONFIG = os.path.join(TEST_DATA, "test_config.cfg")
CONFIG_ASYNC_DEFAULT = os.path.join(TEST_DATA, "config_shaman_async_default.cfg")
CONFIG_NOISE = os.path.join(TEST_DATA, "test_config_noise_reduction.cfg")
SBATCH = os.path.join(TEST_DATA, "test_sbatch.sbatch")
FAKE_SLURMS = os.path.join(TEST_DATA, "fake_slurms")
FAKE_SBATCH = os.path.join(TEST_DATA, "fake_sbatch")
SLURM_DIR = os.path.join(TEST_DATA, "slurm_save")
SBATCH_DIR = os.path.join(TEST_DATA, "sbatch_save")


class TestShamanExperiment(unittest.TestCase):
    """ TestCase used to test the 'ShamanExperiment' class. """
    def setUp(self):
        """Copy the slurms in FAKE_SLURMS folder in the current directory, to test the cleaning method of the ShamanExperiment class."""
        _ = [copy(os.path.join(FAKE_SLURMS, file_), CURRENT_DIR) for file_ in os.listdir(FAKE_SLURMS)]

    def test_init(self):
        """ Test the attribute of the class 'ShamanExperiment' are properly set. """
        se = ShamanExperiment(accelerator_name='fiol',
                            nbr_iteration=3,
                            sbatch_file=SBATCH,
                            experiment_name="test_experiment",
                            configuration_file=CONFIG,
                            sbatch_dir=SBATCH_DIR,
                            slurm_dir=SLURM_DIR
                            )
        self.assertEqual(se.accelerator_name, "fiol")
        self.assertEqual(se.nbr_iteration, 3)
        self.assertEqual(se.sbatch_file, SBATCH)
        self.assertEqual(se.experiment_name, "test_experiment")
        self.assertEqual(se.sbatch_dir, SBATCH_DIR)
        self.assertEqual(se.slurm_dir, SLURM_DIR)
        self.assertEqual(se.result_file, None)
        self.assertIsInstance(datetime.strptime(se.experiment_start, "%y/%m/%d %H:%M:%S"),
                              datetime)
        self.assertIsInstance(se.acc_black_box, AccBlackBox)
        self.assertIsInstance(se.bb_optimizer, BBOptimizer)

    def test_init_noisereduction(self):
        """Tests the proper initialization of the class when using a noise reduction strategy.
        """        
        se = ShamanExperiment(accelerator_name='fiol',
                            nbr_iteration=3,
                            sbatch_file=SBATCH,
                            experiment_name="test_experiment",
                            configuration_file=CONFIG_NOISE,
                            sbatch_dir=SBATCH_DIR,
                            slurm_dir=SLURM_DIR)

    def test_init_assert(self):
        """ Test the AssertionError is raised if the accelerator name is not valid. 
        In this test, the accelerator does not exist."""
        self.assertRaises(AssertionError, ShamanExperiment, accelerator_name='acc_no_exist', nbr_iteration=3, sbatch_file=SBATCH, experiment_name="test_experiment")

    def test_init_except(self):
        """Test the FileNotFoundError is raised if the sbatch file is not reachable. 
        In this test, sbatch_file does not exist."""
        self.assertRaises(FileNotFoundError, ShamanExperiment, accelerator_name='fiol', nbr_iteration=3, sbatch_file="/tmp/no_sbatch", experiment_name="test_experiment")

    def test_keep_slurm_outputs(self):
        """Tests that if there is a value for the slurm output, the outputs are kept in the proper folder."""
        se = ShamanExperiment(accelerator_name='fiol',
                            nbr_iteration=3,
                            sbatch_file=SBATCH,
                            experiment_name="test_experiment",
                            configuration_file=CONFIG,
                            sbatch_dir=SBATCH_DIR,
                            slurm_dir=SLURM_DIR)
        print(f"SLURM_DIR: {se.slurm_dir}")
        print(f"{SLURM_DIR}")
        # Check that the slurm directory does not yet exist
        self.assertFalse(os.path.isdir(SLURM_DIR))
        # Call clean method
        se.clean()
        # Check that calling the cleaning method moves the slurm outputs to the SLURM_DIR folder
        self.assertEqual(os.listdir(SLURM_DIR), ["slurm-42.out", "slurm-666.out"])
        # Check that the current working directory does not have any slurm files
        for file_ in os.listdir(CURRENT_DIR):
            self.assertFalse("slurm" in file_, "Remaining slurm file in current working directory.")

    def test_remove_slurm_outputs(self):
        """Tests that if there is no value for the slurm outputs, the working directory is kept clean."""
        se = ShamanExperiment(accelerator_name='fiol',
                            nbr_iteration=3,
                            sbatch_file=SBATCH,
                            experiment_name="test_experiment",
                            configuration_file=CONFIG,
                            sbatch_dir=SBATCH_DIR)
        # Check that the slurm directory does not exist
        self.assertFalse(os.path.isdir(SLURM_DIR))
        # Call the clean method
        se.clean()
        # Check that there is no slurm file in the current directory
        for file_ in os.listdir(CURRENT_DIR):
            self.assertFalse("slurm" in file_, "Remaining slurm file in current working directory.")

    def test_write_sbatch_in_directory_and_keep(self):
        """Tests that if another directory is specified, the sbatch is written in this directory and not removed"""
        se = ShamanExperiment(accelerator_name='fiol',
                            nbr_iteration=3,
                            sbatch_file=SBATCH,
                            experiment_name="test_experiment",
                            configuration_file=CONFIG,
                            sbatch_dir=SBATCH_DIR)
        # Check that the sbatch directory does not exist
        self.assertTrue(os.path.isdir(SBATCH_DIR))
        # Call the clean method
        se.clean()
        # Check that the sbatch directory still exist and has the sbatch file in it
        self.assertTrue(os.path.isdir(SBATCH_DIR))
        self.assertTrue(os.listdir(SBATCH_DIR), ["test_sbatch_shaman.sbatch"])

    def test_write_sbatch_remove(self):
        """Tests that if another directory is not specified, the folder containing the sbatch is deleted from the working directory."""
        se = ShamanExperiment(accelerator_name='fiol',
                            nbr_iteration=3,
                            sbatch_file=SBATCH,
                            experiment_name="test_experiment",
                            configuration_file=CONFIG)
        # Check that a sbatch file is created
        self.assertTrue("test_sbatch_shaman.sbatch" in os.listdir(CURRENT_DIR))
        # Call the clean method
        se.clean()
        # Check that the sbatch file is deleted
        self.assertFalse("test_sbatch_shaman.sbatch" in os.listdir(CURRENT_DIR)) 

    @patch('little_shaman.acc_blackbox.run_default')
    def test_setup_optimizer_async_default(self):
        """
        Tests that when running the optimization in asynchronous mode using default
        as max time, the max duration step of the black-box optimizer is properly setup.
        """
        mock_launch.return_value = 10
        se = ShamanExperiment(accelerator_name='fiol',
                            nbr_iteration=3,
                            sbatch_file=SBATCH,
                            experiment_name="test_experiment",
                            configuration_file=CONFIG_ASYNC_DEFAULT)
        se.acc_black_box.default_execution_time = 10
        se.setup_bb_optimizer()
        self.assertEqual(se.bb_optimizer.max_step_cost, 10)

    def tearDown(self):
        """Remove all slurm files from current dir.
        Clean all new created files and directories: SLURM_DIR and SBATCH_DIR """
        for file_ in os.listdir(FILE_DIR):
            if file_.startswith("slurm") and file_.endswith(".out"):
                os.remove(os.path.join(FILE_DIR, file_))
        if os.path.isdir(SLURM_DIR):
            rmtree(SLURM_DIR)
        if os.path.isdir(SBATCH_DIR):
            rmtree(SBATCH_DIR)


class TestShamanExperimentStatic(unittest.TestCase):
    """ TestCase used to test the static methods of the 'ShamanExperiment' class. """

    def test_build_parameter_dict(self):
        """ Test the 'build_parameter_dict' method returns the proper dict. """
        parameter_names = ['param1', 'param2', 'param3']
        parameter_values = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        expected_out = [{'param1': 1, 'param2': 2, 'param3': 3},
                        {'param1': 4, 'param2': 5, 'param3': 6},
                        {'param1': 7, 'param2': 8, 'param3': 9}]
        dict_param = ShamanExperiment.build_parameter_dict(parameter_names, parameter_values)
        self.assertListEqual(dict_param, expected_out)

    def test_build_parameter_dict_2(self):
        """ Test the 'build_parameter_dict' method returns the proper dict. """
        parameter_names = ['param1', 'param2', 'param3']
        parameter_values = [[1, 2, 3], [4, 5], [6]]
        expected_out = [{'param1': 1, 'param2': 2, 'param3': 3},
                        {'param1': 4, 'param2': 5},
                        {'param1': 6}]
        dict_param = ShamanExperiment.build_parameter_dict(parameter_names, parameter_values)
        self.assertListEqual(dict_param, expected_out)


if __name__ == '__main__':
    unittest.main(verbosity=2)
