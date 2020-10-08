"""Module to test the shaman_config.py module.
"""

import unittest
from pathlib import Path
from shaman_core.models.shaman_config_model import SHAManConfig
from shaman_worker.shaman_config.shaman_config import SHAManConfigBuilder

DEFAULT_FILE = Path(__file__).parent / "test_shaman_template" / "shaman_template.yaml"
OUTPUT_FILE = Path(__file__).parent / "output_config.yaml"


class TestSHAManSettings(unittest.TestCase):
    """Tests that the shaman settings behaves as expected.
    """


class TestSHAManConfigTemplate(unittest.TestCase):
    """Tests that the templating tool of the shaman_worker behaves as expected.
    """

    POST_DATA = {
        "component_name": "component_1",
        "crossover_method": "one_point_crossover",
        "estimator": "numpy.mean",
        "experiment_name": "trtrtr",
        "fitness_aggregation": "simple_fitness_aggregation",
        "heuristic": "genetic_algorithm",
        "initial_sample_size": "2",
        "max_step_duration": "default",
        "mutation_method": "mutate_neighbor",
        "mutation_rate": "0.2",
        "nbr_iteration": "5",
        "nbr_resamples": "3",
        "resampling_policy": "simple_resampling",
        "parameter_max_param_1": "20",
        "parameter_max_param_2": "54",
        "parameter_min_param_1": "1",
        "parameter_min_param_2": "21",
        "parameter_step_param_1": "1",
        "parameter_step_param_2": "1",
        "sbatch": "Write your sbatch here !",
        "selection_method": "tournament_pick",
    }

    def setUp(self):
        """Sets up the unit test by initializing an object of class SHAManConfig
        """
        self.shaman_config = SHAManConfigBuilder(DEFAULT_FILE, OUTPUT_FILE)

    def test_build_parametric_space(self):
        """Tests that building the parametric space works as expected.
        """
        expected_parametric_space = {
            "param_1": {"max": "20", "min": "1", "step": "1"},
            "param_2": {"max": "54", "min": "21", "step": "1"},
        }
        self.assertDictEqual(
            expected_parametric_space,
            self.shaman_config.build_parametric_space(self.POST_DATA),
        )

    def test_filter_post_data(self):
        """Tests that filtering the post data works as expected.
        """
        expected_filter = {
            "experiment": {},
            "pruning": {"max_step_duration": "default"},
            "noise_reduction": {
                "resampling_policy": "simple_resampling",
                "fitness_aggregation": "simple_fitness_aggregation",
                "nbr_resamples": "3",
                "estimator": "numpy.mean",
            },
            "bbo": {
                "heuristic": "genetic_algorithm",
                "initial_sample_size": "2",
                "selection_method": "tournament_pick",
                "crossover_method": "one_point_crossover",
                "mutation_method": "mutate_neighbor",
                "mutation_rate": "0.2",
            },
            "components": {
                "component_1": {
                    "param_1": {"max": "20", "min": "1", "step": "1"},
                    "param_2": {"max": "54", "min": "21", "step": "1"},
                }
            },
        }
        self.assertDictEqual(
            self.shaman_config.filter_post_data(self.POST_DATA), expected_filter
        )

    def test_update_section(self):
        """Tests that updating the section works as expected, by:
        - Checking the content of the default bbo section
        - Updating the section
        - Checking that the update happened properly
        """
        self.assertFalse("heuristic" in self.shaman_config.config["bbo"])
        filtered_data = self.shaman_config.filter_post_data(self.POST_DATA)
        self.shaman_config.update_section("bbo", filtered_data["bbo"])
        self.assertTrue("heuristic" in self.shaman_config.config["bbo"])

    def test_buid_configuration(self):
        """Tests that building the configuration worzks as expected.
        Writes down the configuration and then try loading it using the Pydantic model.
        """
        self.shaman_config.build_configuration(self.POST_DATA)
        SHAManConfig.from_yaml(OUTPUT_FILE, "component_1")

    def tearDown(self):
        """Remove the built configuration file.
        """
        try:
            OUTPUT_FILE.unlink()
        except FileNotFoundError:
            pass


if __name__ == "__main__":
    unittest.main()
