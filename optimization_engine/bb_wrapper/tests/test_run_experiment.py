#!/usr/bin/env python
"""
This module proposes unit tests for the run_experiment module.
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
from little_shaman import run_experiment
from little_shaman import __DEFAULT_CONFIGURATION__

FILE_DIR = os.path.dirname(os.path.realpath(__file__))
TEST_DATA = os.path.join(FILE_DIR, "test_data")
CONFIG = os.path.join(TEST_DATA, "test_config.cfg")
SBATCH = os.path.join(TEST_DATA, "test_sbatch.sbatch")
WORKING_DIR = os.path.join(TEST_DATA, "working_dir")


class TestShamanExperiment(unittest.TestCase):
    """ TestCase used to test the 'ShamanExperiment' class. """

    def test_parser_all_args(self):
        """ Test the argument parser of the script. """
        args_list = ['--accelerator_name', 'fiol',
                     '--nbr_iteration', '3',
                     '--sbatch_file', SBATCH,
                     '--sbatch_dir', WORKING_DIR,
                     '--experiment_name', 'my_exp',
                     '--sbatch_dir', WORKING_DIR,
                     '--slurm_dir', WORKING_DIR,
                     '--result_file', os.path.join(WORKING_DIR, "results.out"),
                     '--configuration_file', CONFIG]

        args = run_experiment.parse_args(args_list)

        self.assertIsInstance(args.accelerator_name, str)
        self.assertEqual(args.accelerator_name, 'fiol')

        self.assertIsInstance(args.nbr_iteration, int)
        self.assertEqual(args.nbr_iteration, 3)

        self.assertIsInstance(args.sbatch_file, str)
        self.assertEqual(args.sbatch_file, SBATCH)

        self.assertIsInstance(args.experiment_name, str)
        self.assertEqual(args.experiment_name, 'my_exp')

        self.assertIsInstance(args.sbatch_dir, str)
        self.assertEqual(args.sbatch_dir, WORKING_DIR)

        self.assertIsInstance(args.slurm_dir, str)
        self.assertEqual(args.slurm_dir, WORKING_DIR)

        self.assertIsInstance(args.result_file, str)
        self.assertEqual(args.result_file, os.path.join(WORKING_DIR, "results.out"))

        self.assertIsInstance(args.configuration_file, str)
        self.assertEqual(args.configuration_file, CONFIG)

    def test_parser_some_args(self):
        """ Test the argument parser of the script. """
        args_list = ['--accelerator_name', 'sbb_slurm',
                     '--nbr_iteration', '10',
                     '--sbatch_file', SBATCH,
                     '--experiment_name', 'my_exp']

        args = run_experiment.parse_args(args_list)

        self.assertIsInstance(args.accelerator_name, str)
        self.assertEqual(args.accelerator_name, 'sbb_slurm')

        self.assertIsInstance(args.nbr_iteration, int)
        self.assertEqual(args.nbr_iteration, 10)

        self.assertIsInstance(args.sbatch_file, str)
        self.assertEqual(args.sbatch_file, SBATCH)

        self.assertIsInstance(args.experiment_name, str)
        self.assertEqual(args.experiment_name, 'my_exp')

        self.assertEqual(args.slurm_dir, None)
        self.assertEqual(args.result_file, None)

        self.assertIsInstance(args.configuration_file, str)
        self.assertEqual(args.configuration_file, __DEFAULT_CONFIGURATION__)

    @patch('little_shaman.shaman_experiment.ShamanExperiment.launch')
    @patch('little_shaman.shaman_experiment.ShamanExperiment.save')
    def test_main(self, mock_launch, mock_save):
        """ Test the ShamanExperiment initialize properly and the current folder is clean. """
        args_list = ['--accelerator_name', 'fiol',
                     '--nbr_iteration', '3',
                     '--sbatch_file', SBATCH,
                     '--experiment_name', 'my_exp',
                     '--configuration_file', CONFIG]

        mock_launch.return_value = None
        mock_save.return_value = None
        run_experiment.main(args_list)
        for file_ in os.listdir(FILE_DIR):
            self.assertFalse("slurm" in os.path.join(FILE_DIR, file_))
            self.assertFalse("_shaman.sbatch" in os.path.join(FILE_DIR, file_))


if __name__ == '__main__':
    unittest.main(verbosity=2)
