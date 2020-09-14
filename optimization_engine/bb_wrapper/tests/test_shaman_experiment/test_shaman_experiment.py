"""
This module proposes unit tests for the shaman_experiment module.
"""
import os
import unittest
from unittest.mock import patch
from pathlib import Path
from shutil import copy, rmtree
from datetime import datetime
from bbo.optimizer import BBOptimizer
from bb_wrapper.bb_wrapper import BBWrapper
from bb_wrapper.shaman_experiment import SHAManExperiment


CURRENT_DIR = Path.cwd()

CONFIG = Path(__file__).parent / "test_config" / "vanilla.yaml"
CONFIG_ASYNC_DEFAULT = Path(__file__).parent / "test_config" / \
    "pruning_default.yaml"
CONFIG_NOISE = Path(__file__).parent / "test_config" / "noise_reduction.yaml"
SBATCH = Path(__file__).parent / "test_sbatch" / "test_sbatch.sbatch"
TEST_SLURMS = Path(__file__).parent / "test_slurm_outputs"
SLURM_DIR = Path(__file__).resolve().parent / "slurm_save"
SBATCH_DIR = Path(__file__).resolve().parent / "sbatch_save"


class TestSHAManExperiment(unittest.TestCase):
    """ TestCase used to test the 'SHAManExperiment' class. """

    def setUp(self):
        """Copy the slurms in FAKE_SLURMS folder in the current directory, to test the cleaning method of the SHAManExperiment class."""
        _ = [copy(os.path.join(TEST_SLURMS, file_), CURRENT_DIR)
             for file_ in os.listdir(TEST_SLURMS)]

    def test_init(self):
        """ Test the attribute of the class 'SHAManExperiment' are properly set. """
        se = SHAManExperiment(component_name='component_1',
                              nbr_iteration=3,
                              sbatch_file=SBATCH,
                              experiment_name="test_experiment",
                              configuration_file=CONFIG,
                              sbatch_dir=SBATCH_DIR,
                              slurm_dir=SLURM_DIR
                              )
        self.assertEqual(se.component_name, "component_1")
        self.assertEqual(se.nbr_iteration, 3)
        self.assertEqual(se.sbatch_file, SBATCH)
        self.assertEqual(se.experiment_name, "test_experiment")
        self.assertEqual(se.sbatch_dir, SBATCH_DIR)
        self.assertEqual(se.slurm_dir, SLURM_DIR)
        self.assertEqual(se.result_file, None)
        self.assertIsInstance(datetime.strptime(se.experiment_start, "%y/%m/%d %H:%M:%S"),
                              datetime)
        self.assertIsInstance(se.bb_wrapper, BBWrapper)
        self.assertIsInstance(se.bb_optimizer, BBOptimizer)

    def test_init_noisereduction(self):
        """Tests the proper initialization of the class when using a noise reduction strategy.
        """
        se = SHAManExperiment(component_name='component_1',
                              nbr_iteration=3,
                              sbatch_file=SBATCH,
                              experiment_name="test_experiment",
                              configuration_file=CONFIG_NOISE,
                              sbatch_dir=SBATCH_DIR,
                              slurm_dir=SLURM_DIR)
        assert se.configuration.noise_reduction

    def test_init_assert(self):
        """ Test the AssertionError is raised if the component name is not valid.
        In this test, the component does not exist."""
        self.assertRaises(KeyError, SHAManExperiment, component_name='comp_no_exist',
                          nbr_iteration=3, sbatch_file=SBATCH, experiment_name="test_experiment", configuration_file=CONFIG)

    def test_init_except(self):
        """Test the FileNotFoundError is raised if the sbatch file is not reachable.
        In this test, sbatch_file does not exist."""
        self.assertRaises(FileNotFoundError, SHAManExperiment, component_name='component_1',
                          nbr_iteration=3, sbatch_file="/tmp/no_sbatch", experiment_name="test_experiment", configuration_file=CONFIG)

    def test_keep_slurm_outputs(self):
        """Tests that if there is a value for the slurm output, the outputs are kept in the proper folder."""
        se = SHAManExperiment(component_name='component_1',
                              nbr_iteration=3,
                              sbatch_file=SBATCH,
                              experiment_name="test_experiment",
                              configuration_file=CONFIG,
                              sbatch_dir=SBATCH_DIR,
                              slurm_dir=SLURM_DIR)
        # Check that the slurm directory does not yet exist
        self.assertFalse(SLURM_DIR.is_dir())
        # Call clean method
        se.clean()
        # Check that calling the cleaning method moves the slurm outputs to the SLURM_DIR folder
        self.assertEqual([file_.name for file_ in SLURM_DIR.glob("*")], [
                         "slurm-42.out", "slurm-666.out"])
        # Check that the current working directory does not have any slurm files
        self.assertFalse(
            list(CURRENT_DIR.glob("*slurm*.out")), "Remaining slurm file in current working directory.")

    def test_remove_slurm_outputs(self):
        """Tests that if there is no value for the slurm outputs, the working directory is kept clean."""
        se = SHAManExperiment(component_name='component_1',
                              nbr_iteration=3,
                              sbatch_file=SBATCH,
                              experiment_name="test_experiment",
                              configuration_file=CONFIG,
                              sbatch_dir=SBATCH_DIR)
        # Check that the slurm directory does not exist
        self.assertFalse(SLURM_DIR.is_dir())
        # Call the clean method
        se.clean()
        # Check that there is no slurm file in the current directory
        self.assertFalse(
            list(CURRENT_DIR.glob("*slurm*.out")), "Remaining slurm file in current working directory.")

    def test_write_sbatch_in_directory_and_keep(self):
        """Tests that if another directory is specified, the sbatch is written in this directory and not removed"""
        se = SHAManExperiment(component_name='component_1',
                              nbr_iteration=3,
                              sbatch_file=SBATCH,
                              experiment_name="test_experiment",
                              configuration_file=CONFIG,
                              sbatch_dir=SBATCH_DIR)
        # Check that the sbatch directory does not exist
        self.assertTrue(SBATCH_DIR.is_dir())
        # Call the clean method
        se.clean()
        # Check that the sbatch directory still exist and has the sbatch file in it
        self.assertTrue(SBATCH_DIR.is_dir())
        self.assertTrue(list(SBATCH_DIR.glob("*")),
                        ["test_sbatch_shaman.sbatch"])

    def test_write_sbatch_remove(self):
        """Tests that if another directory is not specified, the folder containing the sbatch is deleted from the working directory."""
        se = SHAManExperiment(component_name='component_1',
                              nbr_iteration=3,
                              sbatch_file=SBATCH,
                              experiment_name="test_experiment",
                              configuration_file=CONFIG)
        # Check that a sbatch file is created
        self.assertTrue(
            "test_sbatch_shaman.sbatch" in os.listdir())
        # Call the clean method
        se.clean()
        # Check that the sbatch file is deleted
        self.assertFalse(
            "test_sbatch_shaman.sbatch" in os.listdir())

    @ patch('bb_wrapper.bb_wrapper.BBWrapper.run_default')
    def test_setup_optimizer_async_default(self, mock_launch):
        """
        Tests that when running the optimization in asynchronous mode using default
        as max time, the max duration step of the black-box optimizer is properly setup.
        """
        mock_launch.return_value = 10
        se = SHAManExperiment(component_name='component_1',
                              nbr_iteration=3,
                              sbatch_file=SBATCH,
                              experiment_name="test_experiment",
                              configuration_file=CONFIG_ASYNC_DEFAULT)
        se.bb_wrapper.default_execution_time = 10
        se.setup_bb_optimizer()
        self.assertEqual(se.bb_optimizer.max_step_cost, 10)

    def tearDown(self):
        """Remove all slurm files from current dir.
        Clean all new created files and directories: SLURM_DIR and SBATCH_DIR """
        for file_ in Path(__file__).glob("slurm*.out"):
            file_.unlink()
        if Path.is_dir(SLURM_DIR):
            rmtree(SLURM_DIR)
        if Path.is_dir(SBATCH_DIR):
            rmtree(SBATCH_DIR)


class TestSHAManExperimentStatic(unittest.TestCase):
    """ TestCase used to test the static methods of the 'SHAManExperiment' class. """

    def test_build_parameter_dict(self):
        """ Test the 'build_parameter_dict' method returns the proper dict. """
        parameter_names = ['param1', 'param2', 'param3']
        parameter_values = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        expected_out = [{'param1': 1, 'param2': 2, 'param3': 3},
                        {'param1': 4, 'param2': 5, 'param3': 6},
                        {'param1': 7, 'param2': 8, 'param3': 9}]
        dict_param = SHAManExperiment.build_parameter_dict(
            parameter_names, parameter_values)
        self.assertListEqual(dict_param, expected_out)

    def test_build_parameter_dict_2(self):
        """ Test the 'build_parameter_dict' method returns the proper dict. """
        parameter_names = ['param1', 'param2', 'param3']
        parameter_values = [[1, 2, 3], [4, 5], [6]]
        expected_out = [{'param1': 1, 'param2': 2, 'param3': 3},
                        {'param1': 4, 'param2': 5},
                        {'param1': 6}]
        dict_param = SHAManExperiment.build_parameter_dict(
            parameter_names, parameter_values)
        self.assertListEqual(dict_param, expected_out)


class TestSHAManAPI(unittest.TestCase):
    """Unit tests for the integration of SHAMan with the REST API.
    """


if __name__ == '__main__':
    unittest.main(verbosity=2)
