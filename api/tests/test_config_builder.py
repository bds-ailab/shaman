"""
Tests that the configuration is properly built when receiving post data from the user.
"""
import os
import configparser
import unittest
from shaman_api.shaman_config.shaman_config import ShamanConfig

FILE_DIR = os.path.dirname(os.path.realpath(__file__))
TEST_DATA = os.path.join(FILE_DIR, "test_data")


DEFAULT_FILE = os.path.join(TEST_DATA, "default_config.cfg")
OUTPUT_FILE = os.path.join(TEST_DATA, "output_config.cfg")

# Test sent post data
TEST_POST_DATA = {"with_ioi": 'False', "max_step_duration": "numpy.median",
                  "resampling_policy": "static_resampling", "fitness_aggregation": 'numpy.median'}
FULL_TEST_POST_DATA = {
    "accelerator_name": "sbb",
    "experiment_name": "trtrtr",
    "heuristic": "surrogate_models",
    "initial_sample_size": "2",
    "iterations": "5",
    "max_step_duration": "default",
    "nbr_resamples": "4",
    "next_parameter_strategy": "maximum_probability_improvement",
    "pruning_strategy": "default",
    "regression_model": "sklearn.gaussian_process.GaussianProcessRegressor",
    "resampling_policy": "static_resampling",
    "sbatch": "#SBATCH oiore",
    "with_ioi": 'True'
}


class TestConfigBuilder(unittest.TestCase):
    """
    Tests that the config builder works properly.
    """

    def setUp(self):
        """Tests that the class initializes properly by setting it up
        with a
        """
        self.config = ShamanConfig(DEFAULT_FILE, OUTPUT_FILE)

    def test_filter_post_data(self):
        """Tests that the post data is properly filtered when sent to the class.
        """
        filtered_data = self.config.filter_post_data(TEST_POST_DATA)
        self.assertDictEqual(filtered_data['EXPERIMENT'], {'with_ioi': 'False'})
        self.assertDictEqual(filtered_data['PRUNING_STRATEGY'], {
                             'max_step_duration': 'numpy.median'})
        self.assertDictEqual(filtered_data['NOISE_REDUCTION'], {
                             'resampling_policy': 'static_resampling', 'fitness_aggregation': 'numpy.median'})

    def test_update_section(self):
        """Tests that sections are properly updated.
        """
        filtered_data = self.config.filter_post_data(TEST_POST_DATA)
        # Check that current value is set to False
        self.assertEqual(self.config.config["EXPERIMENT"]["with_ioi"], 'True')
        # Update value
        self.config.update_section("EXPERIMENT", filtered_data["EXPERIMENT"])
        # Check that value is updated to True
        self.assertEqual(self.config.config["EXPERIMENT"]["with_ioi"], 'False')

    def test_save_configuration(self):
        """Tests that the configuration is properly saved.
        """
        self.config.build_configuration(FULL_TEST_POST_DATA)
        self.assertTrue("output_config.cfg" in os.listdir(TEST_DATA))

    def test_build_configuration(self):
        """Tests that the configuration is properly built.
        """
        # Build the configuration from post data
        self.config.build_configuration(FULL_TEST_POST_DATA)
        # Load the expected configuration
        expected_config = configparser.ConfigParser()
        expected_config.read(os.path.join(TEST_DATA, "expected_config.cfg"))
        # Check that each section is equal to the expected configuration
        self.assertDictEqual(dict(self.config.config["EXPERIMENT"]), dict(
            expected_config["EXPERIMENT"]))
        self.assertDictEqual(dict(self.config.config["BBO"]), dict(
            expected_config["BBO"]))
        self.assertDictEqual(dict(self.config.config["NOISE_REDUCTION"]), dict(
            expected_config["NOISE_REDUCTION"]))
        self.assertDictEqual(dict(self.config.config["PRUNING_STRATEGY"]), dict(
            expected_config["PRUNING_STRATEGY"]))

    def tearDown(self):
        """Remove test configuration file.
        """
        # Check in configuration file has been generated
        if "output_config.cfg" in os.listdir(TEST_DATA):
            # Remove test configuration file
            os.remove(os.path.join(TEST_DATA, "output_config.cfg"))


if __name__ == "__main__":
    unittest.main()
