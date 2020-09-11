#!/usr/bin/env python
"""
This module proposes unit tests for the acc_blackbox module.
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
import glob
import unittest
from shutil import copy
from unittest.mock import patch
import numpy as np
from iomodules_handler.io_modules import SROAccelerator
from little_shaman.acc_blackbox import AccBlackBox

CURRENT_DIR = os.getcwd()
FILE_DIR = os.path.dirname(os.path.realpath(__file__))
TEST_DATA = os.path.join(FILE_DIR, "test_data")
TEST_SBATCH_DIR = os.path.join(TEST_DATA, "test_sbatch_dir")
FAKE_SLURMS = os.path.join(TEST_DATA, "fake_slurms")
TEST_IOMODULES_CONFIG = os.path.join(TEST_DATA, "iomodules_config.yaml")


class TestAccBlackbox(unittest.TestCase):
    """ TestCase used to test the 'AccBlackbox' class. """
    def setUp(self):
        """ """
        self.sbatch_file = f"{TEST_DATA}/test_sbatch.sbatch"
        self.acc_blackbox = AccBlackBox('fiol',
                               ['param1', 'param2'],
                               self.sbatch_file,
                               sbatch_dir=TEST_SBATCH_DIR,
                               acc_configuration_file=TEST_IOMODULES_CONFIG)
        # Move the test slurm-42.out file into current directory
        copy(os.path.join(FAKE_SLURMS, "slurm-42.out"), CURRENT_DIR)

    def test_init(self):
        """ Test the attribute of the class 'AccBlackbox' are properly set. """
        self.assertEqual(self.acc_blackbox.accelerator_name, 'fiol')
        self.assertListEqual(self.acc_blackbox.parameter_names, ['param1', 'param2'])
        self.assertEqual(self.acc_blackbox.acc_configuration_file, TEST_IOMODULES_CONFIG)
        self.assertEqual(self.acc_blackbox.sbatch_dir, TEST_SBATCH_DIR)
        self.assertEqual(self.acc_blackbox.accelerator, SROAccelerator)
        self.assertEqual(self.acc_blackbox.sbatch_file, os.path.join(TEST_SBATCH_DIR,
                                                       "test_sbatch_shaman.sbatch"))
        self.assertEqual(self.acc_blackbox.instrumented, False)
        self.assertListEqual(self.acc_blackbox.jobids, list())

    def test_copy_sbatch(self):
        """ Test the "copy_sbatch" method build the proper sbatch file. """
        expected_lines = ['#!/bin/bash\n',
                           '#SBATCH --job-name=TestJob\n',
                           '#SBATCH --ntasks=3\n',
                           'time (\n',
                           'hostname)']
        new_path = self.acc_blackbox.copy_sbatch(self.sbatch_file)
        with open(new_path) as read_file:
            lines = read_file.readlines()
        self.assertEqual(new_path, os.path.join(TEST_SBATCH_DIR,
                                                "test_sbatch_shaman.sbatch"))
        self.assertListEqual(lines, expected_lines)

    def test_copy_sbatch_timed(self):
        """ Test the "copy_sbatch" method just copy the content of the file if it is already
        timed. """
        original_file = f"{TEST_DATA}/test_sbatch_timed.sbatch"
        with open(original_file) as orig_file:
            expected_lines = orig_file.readlines()
        new_path = self.acc_blackbox.copy_sbatch(original_file)
        with open(new_path) as read_file:
            lines = read_file.readlines()
        self.assertEqual(new_path, os.path.join(TEST_SBATCH_DIR,
                                                "test_sbatch_timed_shaman.sbatch"))
        self.assertListEqual(lines, expected_lines)
        os.remove(new_path)

    def test_parse_milliseconds(self):
        """ Test the "parse_milliseconds" method convert properly the date in time. """
        time = AccBlackBox.parse_milliseconds('01m01.01s')
        self.assertEqual(time, 61.001)
        time = AccBlackBox.parse_milliseconds('123m45.67s')
        self.assertEqual(time, 7425.067)

    def test_parse_slurm_times(self):
        """ Test the "_parse_slurm_times" method extracts proprely the time from a slurm output
        file. """
        time = self.acc_blackbox._parse_slurm_times(f"{FAKE_SLURMS}/slurm-42.out")
        self.assertEqual(time, 1508.085)

    def test_parse_slurm_times_except_no_time(self):
        """ Test the "_parse_slurm_times" method raises a ValueError if the slurm output file does
        not contains the time. """
        self.assertRaises(ValueError,
                          self.acc_blackbox._parse_slurm_times,
                          f"{FAKE_SLURMS}/slurm-666.out")

    def test_parse_slurm_times_except_no_file(self):
        """ Test the "_parse_slurm_times" method raises a FileNotFoundError if the slurm output file
        does not exist. """
        self.assertRaises(FileNotFoundError,
                          self.acc_blackbox._parse_slurm_times,
                          f"{FAKE_SLURMS}/slurm-00.out")

    @patch('iomodules_handler.io_modules.SROAccelerator.submit_sbatch')
    def test_compute(self, mock_submit_sbatch):
        """ Test the "compute" method works properly. """
        mock_submit_sbatch.return_value = 42
        param = np.array([6, 9])
        time = self.acc_blackbox.compute(param)
        self.assertListEqual(self.acc_blackbox.jobids, [42])
        self.assertEqual(time, 1508.085)

    @patch('iomodules_handler.io_modules.SROAccelerator.submit_sbatch')
    def test_compute_default(self, mock_submit_sbatch):
        mock_submit_sbatch.return_value = 42
        _ = self.acc_blackbox.run_default()
        # Check that the default jobid is properly stored
        self.assertEqual(self.acc_blackbox.default_jobid, 42)
        # Check that the execution time is properly stored
        self.assertEqual(self.acc_blackbox.default_execution_time, 1508.085)
        # Check that the default parameters of the accelerator are properly stored
        default_parameters = {
            "SLURM_CONF":"/etc/slurm/slurm.conf",
            "SRO_CLUSTER_THRESHOLD": 2,
            "SRO_DSC_BINSIZE": 1048576,
            "SRO_PREFETCH_SIZE":20971520,
            "SRO_SEQUENCE_LENGTH": 100
        }
        self.assertDictEqual(self.acc_blackbox.default_parameters, default_parameters)

    def tearDown(self):
        out_file = f"{TEST_SBATCH_DIR}/test_sbatch_shaman.sbatch"
        if glob.glob(out_file):
            os.remove(out_file)
        os.remove(os.path.join(CURRENT_DIR, "slurm-42.out"))


if __name__ == '__main__':
    unittest.main(verbosity=2)
