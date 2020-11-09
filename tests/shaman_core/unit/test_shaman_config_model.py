# Copyright 2020 BULL SAS All rights reserved
"""
Tests the SHAMan configuration model.
"""
import unittest
from pathlib import Path
import numpy
from numpy.testing import assert_array_equal
from pydantic import ValidationError

from shaman_core.models.shaman_config_model import SHAManConfig, PruningParameters

from bbo.optimizer import BBOptimizer
from bbo.heuristics.genetic_algorithm.selections import tournament_pick
from bbo.heuristics.genetic_algorithm.crossover import single_point_crossover
from bbo.heuristics.genetic_algorithm.mutations import mutate_chromosome_to_neighbor

TEST_DATA = Path(__file__).parent / "test_shaman_config"
# Test config component

VANILLA_CONFIG = TEST_DATA / "vanilla.yaml"
VANILLA_CONFIG_WRONG = TEST_DATA / "vanilla_wrong_config.yaml"
NOISE_REDUCTION_CONFIG = TEST_DATA / "noise_reduction.yaml"
PRUNING_CONFIG = TEST_DATA / "pruning.yaml"


class FakeBlackBox:
    """Fake class to act as BlackBox to test the BBOptimizer proper initialization.
    """

    def compute(self, x):
        """
        Do nothing.
        """
        return x


class TestSHAManModelVanilla(unittest.TestCase):
    """
    Tests that the SHAMan model parses the configuration correctly, when there is no pruning and
    noise reduction.
    """

    def test_unknown_component(self):
        """Tests that loading the config from yaml with an unknown component, a key error is raised."""
        with self.assertRaises(KeyError):
            SHAManConfig.from_yaml(VANILLA_CONFIG, "do_not_exist")

    def test_load_config_vanilla_component_1(self):
        """Tests that loading the config from yaml behaves as expected for component_1."""
        shaman_config = SHAManConfig.from_yaml(VANILLA_CONFIG, "component_1")
        self.assertEqual(
            shaman_config.component_parameter_names, ["param_1", "param_2"]
        )

    def test_load_config_vanilla_component_2(self):
        """Tests that loading the config from yaml behaves as expected for component_2."""
        shaman_config = SHAManConfig.from_yaml(VANILLA_CONFIG, "component_2")
        self.assertEqual(shaman_config.component_parameter_names, ["param_1"])

    def test_bbo_kwargs(self):
        """Tests that the BBO kwargs are properly parsed."""
        shaman_config = SHAManConfig.from_yaml(VANILLA_CONFIG, "component_2")
        expected_kwargs = {
            "heuristic": "genetic_algorithm",
            "initial_sample_size": 2,
            "selection_method": tournament_pick,
            "crossover_method": single_point_crossover,
            "mutation_method": mutate_chromosome_to_neighbor,
            "pool_size": 5,
            "mutation_rate": 0.4,
            "elitism": False,
        }
        self.assertDictEqual(shaman_config.bbo_parameters, expected_kwargs)

    def test_parameter_space(self):
        """Tests that the parameter space is properly parsed."""
        shaman_config = SHAManConfig.from_yaml(VANILLA_CONFIG, "component_1")
        expected_parameter_space = numpy.array(
            [numpy.array([1, 2]), numpy.array([1, 2, 3])]
        )
        assert_array_equal(
            expected_parameter_space[0], shaman_config.component_parameter_space[0]
        )
        assert_array_equal(
            expected_parameter_space[1], shaman_config.component_parameter_space[1]
        )

    def test_bbo_init(self):
        """Tests that the BBO kwargs allow to initialize an object of class BBOptimizer"""
        shaman_config = SHAManConfig.from_yaml(VANILLA_CONFIG, "component_2")
        BBOptimizer(
            black_box=FakeBlackBox,
            parameter_space=shaman_config.component_parameter_space,
            **shaman_config.bbo_parameters
        )

    def test_empty_pruning(self):
        """Tests that when there is no pruning specified, it returns None."""
        shaman_config = SHAManConfig.from_yaml(VANILLA_CONFIG, "component_2")
        self.assertEqual(shaman_config.pruning, None)

    def test_empty_noise_reduction(self):
        """Tests that when there is no noise reduction, it returns None."""
        shaman_config = SHAManConfig.from_yaml(VANILLA_CONFIG, "component_2")
        self.assertEqual(shaman_config.noise_reduction, None)

    def test_wrong_parameter_space(self):
        """Tests that when the parametric space makes no sense, an error is raised."""
        with self.assertRaises(ValueError):
            shaman_config = SHAManConfig.from_yaml(VANILLA_CONFIG_WRONG, "component_1")


class TestSHAManNoiseReduction(unittest.TestCase):
    """
    Tests that parsing the noise reduction parameters work as expected.
    """

    def test_noise_reduction(self):
        """Tests that the noise reduction parameters are properly parsed.
        """
        shaman_config = SHAManConfig.from_yaml(NOISE_REDUCTION_CONFIG, "component_1")
        expected_noise_reduction_parameters = {
            "resampling_policy": "simple_resampling",
            "estimator": "numpy.median",
            "nbr_resamples": 3,
            "fitness_aggregation": "simple_fitness_aggregation",
        }
        self.assertDictEqual(
            shaman_config.noise_reduction, expected_noise_reduction_parameters
        )

    def test_noise_reduction_bbo(self):
        """Tests that the noise reduction parameters are properly added to the bbo_kwargs and
        the BBOptimizer object can be initialized.
        """
        shaman_config = SHAManConfig.from_yaml(NOISE_REDUCTION_CONFIG, "component_1")
        # Check that the dictionary has been properly updated
        assert "nbr_resamples" in shaman_config.bbo_parameters
        assert "fitness_aggregation" in shaman_config.bbo_parameters
        assert "resampling_policy" in shaman_config.bbo_parameters
        # Check that the estimator function is properly parsed
        self.assertEqual(shaman_config.bbo_parameters["estimator"], numpy.median)
        # Check that the BBOptimizer class can be properly instanciated
        BBOptimizer(
            black_box=FakeBlackBox,
            parameter_space=shaman_config.component_parameter_space,
            **shaman_config.bbo_parameters
        )


class TestSHAManPruning(unittest.TestCase):
    """
    Tests that the pruning parameters work as expected, by testing the model PruningParameters.
    """

    def test_pruning_parameters_int(self):
        """Tests that the pruning parameters are properly parsed when max_step_duration is an int.
        """
        pruning_parameters = PruningParameters(max_step_duration=6)
        self.assertEqual(pruning_parameters.max_step_duration, 6)

    def test_pruning_parameters_default(self):
        """Tests that the pruning parameters are properly parsed when max_step_duration is equal to
        the default.
        """
        pruning_parameters = PruningParameters(max_step_duration="default")
        self.assertEqual(pruning_parameters.max_step_duration, "default")

    def test_pruning_parameters_function(self):
        """Tests that the pruning parameters are properly parsed when max_step_duration is a function.
        """
        pruning_parameters = PruningParameters(max_step_duration="numpy.median")
        self.assertEqual(pruning_parameters.max_step_duration, numpy.median)

    def test_pruning_parameters_wrong_type(self):
        """Tests that an error is raised when the max_step_duration makes no sense.
        """
        with self.assertRaises(ValidationError):
            PruningParameters(max_step_duration="titi")

    def test_pruning_parameters_config(self):
        """Tests that parsing the config is done properly and that the BBOptimizer class can be
        properly instanciated.
        """
        shaman_config = SHAManConfig.from_yaml(PRUNING_CONFIG, "component_1")
        BBOptimizer(
            black_box=FakeBlackBox,
            parameter_space=shaman_config.component_parameter_space,
            async_optim=True,
            max_step_cost=shaman_config.pruning.max_step_duration,
            **shaman_config.bbo_parameters
        )


if __name__ == "__main__":
    unittest.main()
