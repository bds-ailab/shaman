"""
This module proposes unit tests for the shaman_experiment module.
"""
import os
import unittest
from unittest.mock import patch
import io
import sys
from pathlib import Path
from shutil import copy, rmtree
from datetime import datetime

import numpy as np

from bbo.optimizer import BBOptimizer
from bb_wrapper.bb_wrapper import BBWrapper
from bb_wrapper.shaman_experiment import SHAManExperiment


CURRENT_DIR = Path.cwd()

CONFIG = Path(__file__).parent / "test_config" / "vanilla.yaml"
CONFIG_ASYNC_DEFAULT = Path(__file__).parent / "test_config" / "pruning_default.yaml"
CONFIG_ASYNC = Path(__file__).parent / "test_config" / "pruning.yaml"
CONFIG_NOISE = Path(__file__).parent / "test_config" / "noise_reduction.yaml"
SBATCH = Path(__file__).parent / "test_sbatch" / "test_sbatch.sbatch"
TEST_SLURMS = Path(__file__).parent / "test_slurm_outputs"
SLURM_DIR = Path(__file__).resolve().parent / "slurm_save"
SBATCH_DIR = Path(__file__).resolve().parent / "sbatch_save"

# Class to test the POST and GET requests responses


class MockResponse:
    def __init__(self, json_data, status_code):
        self.json_data = json_data
        self.status_code = status_code

    def json(self):
        return self.json_data


def mocked_requests_post(*args, **kwargs):
    """Mocks the post requests."""
    if args[0] == "experiments":
        return MockResponse({"id": "123"}, 200)


def mocked_requests_post_fail(*args, **kwargs):
    """Mocks the post requests."""
    if args[0] == "experiments":
        return MockResponse({"id": "failed"}, 500)


def mocked_requests_put(*args, **kwargs):
    """Mocks the put request."""
    # Successful update
    if args[0] == "experiments/123/update":
        return MockResponse({"id": "ok"}, 200)
    # Failed update
    if args[0] == "experiments/321/update":
        return MockResponse({"id": "nok"}, 500)
    # Successful end of experiment
    if args[0] == "experiments/123/finish":
        return MockResponse({"id": "ok"}, 200)
    # Failed end of experiment
    if args[0] == "experiments/321/finish":
        return MockResponse({"id": "ok"}, 500)
    # Successful fail
    if args[0] == "experiments/123/fail":
        return MockResponse({"id": "ok"}, 200)
    if args[0] == "experiments/321/fail":
        return MockResponse({"id": "ok"}, 200)
    # Failed fail
    if args[0] == "experiments/322/fail":
        return MockResponse({"id": "nok"}, 500)
    # Successful stop
    if args[0] == "experiments/123/stop":
        return MockResponse({"id": "ok"}, 200)
    # Failed stop
    if args[0] == "experiments/321/stop":
        return MockResponse({"id": "ok"}, 500)


def mocked_requests_get(*args, **kwargs):
    """Mock the get requests containing the data of the experiment."""
    if args[0] == "http://127.0.0.1:5000/components":
        mock_components = {
            "components": {
                "component_1": {
                    "plugin": "example_1",
                    "header": "example_header",
                    "command": "example_cmd",
                    "ld_preload": "example_lib",
                    "parameters": {
                        "param_1": {
                            "type": "int",
                            "default": 1,
                            "optional": False,
                            "env_var": True,
                            "description": None,
                            "cmd_var": None,
                            "flag": None,
                        },
                        "param_2": {
                            "type": "str",
                            "default": "/home/",
                            "optional": False,
                            "env_var": None,
                            "description": None,
                            "cmd_var": "True",
                            "flag": "folder",
                        },
                    },
                    "custom_component": None,
                },
                "component_2": {
                    "plugin": "example_2",
                    "header": "example_header",
                    "command": "example_cmd",
                    "ld_preload": "example_lib",
                    "parameters": {
                        "param_1": {
                            "type": "int",
                            "default": 1,
                            "optional": False,
                            "env_var": True,
                            "description": None,
                            "cmd_var": None,
                            "flag": None,
                        },
                        "param_2": {
                            "type": "str",
                            "default": "/home/",
                            "optional": False,
                            "env_var": None,
                            "description": None,
                            "cmd_var": "True",
                            "flag": "folder",
                        },
                        "param_3": {
                            "type": "str",
                            "default": None,
                            "optional": False,
                            "env_var": None,
                            "description": None,
                            "cmd_var": "True",
                            "flag": "f",
                        },
                    },
                    "custom_component": None,
                },
                "component_3": {
                    "plugin": "example_3",
                    "header": "example_header",
                    "command": None,
                    "ld_preload": "example_lib",
                    "parameters": {
                        "param_1": {
                            "type": "int",
                            "default": None,
                            "optional": False,
                            "env_var": True,
                            "description": None,
                            "cmd_var": None,
                            "flag": None,
                        },
                        "param_2": {
                            "type": "int",
                            "default": 2,
                            "optional": False,
                            "env_var": True,
                            "description": None,
                            "cmd_var": None,
                            "flag": None,
                        },
                    },
                    "custom_component": None,
                },
                "component_4": {
                    "plugin": "example_4",
                    "header": "example_header",
                    "command": "example_cmd",
                    "ld_preload": "example_lib",
                    "parameters": {
                        "xxx": {
                            "type": "int",
                            "default": None,
                            "optional": True,
                            "env_var": True,
                            "description": None,
                            "cmd_var": None,
                            "flag": None,
                        }
                    },
                    "custom_component": None,
                },
            }
        }
        return MockResponse(mock_components, 200)


class TestSHAManExperiment(unittest.TestCase):
    """ TestCase used to test the 'SHAManExperiment' class. """

    def setUp(self):
        """Copy the slurms in FAKE_SLURMS folder in the current directory, to test the cleaning method of the SHAManExperiment class."""
        _ = [
            copy(os.path.join(TEST_SLURMS, file_), CURRENT_DIR)
            for file_ in os.listdir(TEST_SLURMS)
        ]

    @patch("httpx.get", side_effect=mocked_requests_get)
    def test_init(self, mocked_get):
        """ Test the attribute of the class 'SHAManExperiment' are properly set. """
        se = SHAManExperiment(
            component_name="component_1",
            nbr_iteration=3,
            sbatch_file=SBATCH,
            experiment_name="test_experiment",
            configuration_file=CONFIG,
            sbatch_dir=SBATCH_DIR,
            slurm_dir=SLURM_DIR,
        )
        self.assertEqual(se.component_name, "component_1")
        self.assertEqual(se.nbr_iteration, 3)
        self.assertEqual(se.sbatch_file, SBATCH)
        self.assertEqual(se.experiment_name, "test_experiment")
        self.assertEqual(se.sbatch_dir, SBATCH_DIR)
        self.assertEqual(se.slurm_dir, SLURM_DIR)
        self.assertEqual(se.result_file, None)
        self.assertIsInstance(
            datetime.strptime(se.experiment_start, "%y/%m/%d %H:%M:%S"), datetime
        )
        self.assertIsInstance(se.bb_wrapper, BBWrapper)
        self.assertIsInstance(se.bb_optimizer, BBOptimizer)

    @patch("httpx.get", side_effect=mocked_requests_get)
    def test_init_noisereduction(self, mocked_requests_get):
        """Tests the proper initialization of the class when using a noise reduction strategy."""
        se = SHAManExperiment(
            component_name="component_1",
            nbr_iteration=3,
            sbatch_file=SBATCH,
            experiment_name="test_experiment",
            configuration_file=CONFIG_NOISE,
            sbatch_dir=SBATCH_DIR,
            slurm_dir=SLURM_DIR,
        )
        assert se.configuration.noise_reduction

    @patch("httpx.get", side_effect=mocked_requests_get)
    def test_init_assert(self, mocked_requests_get):
        """Test the AssertionError is raised if the component name is not valid.
        In this test, the component does not exist."""
        self.assertRaises(
            KeyError,
            SHAManExperiment,
            component_name="comp_no_exist",
            nbr_iteration=3,
            sbatch_file=SBATCH,
            experiment_name="test_experiment",
            configuration_file=CONFIG,
        )

    @patch("httpx.get", side_effect=mocked_requests_get)
    def test_init_except(self, mocked_requests_get):
        """Test the FileNotFoundError is raised if the sbatch file is not reachable.
        In this test, sbatch_file does not exist."""
        self.assertRaises(
            FileNotFoundError,
            SHAManExperiment,
            component_name="component_1",
            nbr_iteration=3,
            sbatch_file="/tmp/no_sbatch",
            experiment_name="test_experiment",
            configuration_file=CONFIG,
        )

    @patch("httpx.get", side_effect=mocked_requests_get)
    def test_init_no_path_sbatch(self, mocked_requests_get):
        """Tests that the initialization works as expected when given a path as a string as sbatch_dir."""
        se = SHAManExperiment(
            component_name="component_1",
            nbr_iteration=3,
            sbatch_file=SBATCH,
            experiment_name="test_experiment",
            configuration_file=CONFIG,
            sbatch_dir=str(SBATCH_DIR),
            slurm_dir=SLURM_DIR,
        )
        self.assertTrue(isinstance(se.sbatch_dir, Path))

    @patch("httpx.get", side_effect=mocked_requests_get)
    def test_init_no_path_slurm(self, mocked_requests_get):
        """Tests that the initialization works as expected when given a path as a string as slurm_dir."""
        se = SHAManExperiment(
            component_name="component_1",
            nbr_iteration=3,
            sbatch_file=SBATCH,
            experiment_name="test_experiment",
            configuration_file=CONFIG,
            sbatch_dir=SBATCH_DIR,
            slurm_dir=str(SLURM_DIR),
        )
        self.assertTrue(isinstance(se.slurm_dir, Path))

    @patch("httpx.get", side_effect=mocked_requests_get)
    def test_keep_slurm_outputs(self, mocked_requests_get):
        """Tests that if there is a value for the slurm output, the outputs are kept in the proper folder."""
        se = SHAManExperiment(
            component_name="component_1",
            nbr_iteration=3,
            sbatch_file=SBATCH,
            experiment_name="test_experiment",
            configuration_file=CONFIG,
            sbatch_dir=SBATCH_DIR,
            slurm_dir=SLURM_DIR,
        )
        # Check that the slurm directory does not yet exist
        self.assertFalse(SLURM_DIR.is_dir())
        # Call clean method
        se.clean()
        # Check that calling the cleaning method moves the slurm outputs to the SLURM_DIR folder
        self.assertEqual(
            [file_.name for file_ in SLURM_DIR.glob("*")],
            ["slurm-42.out", "slurm-666.out"],
        )
        # Check that the current working directory does not have any slurm files
        self.assertFalse(
            list(CURRENT_DIR.glob("*slurm*.out")),
            "Remaining slurm file in current working directory.",
        )

    @patch("httpx.get", side_effect=mocked_requests_get)
    def test_remove_slurm_outputs(self, mocked_requests_get):
        """Tests that if there is no value for the slurm outputs, the working directory is kept clean."""
        se = SHAManExperiment(
            component_name="component_1",
            nbr_iteration=3,
            sbatch_file=SBATCH,
            experiment_name="test_experiment",
            configuration_file=CONFIG,
            sbatch_dir=SBATCH_DIR,
        )
        # Check that the slurm directory does not exist
        self.assertFalse(SLURM_DIR.is_dir())
        # Call the clean method
        se.clean()
        # Check that there is no slurm file in the current directory
        self.assertFalse(
            list(CURRENT_DIR.glob("*slurm*.out")),
            "Remaining slurm file in current working directory.",
        )

    @patch("httpx.get", side_effect=mocked_requests_get)
    def test_write_sbatch_in_directory_and_keep(self, mocked_requests_get):
        """Tests that if another directory is specified, the sbatch is written in this directory and not removed"""
        se = SHAManExperiment(
            component_name="component_1",
            nbr_iteration=3,
            sbatch_file=SBATCH,
            experiment_name="test_experiment",
            configuration_file=CONFIG,
            sbatch_dir=SBATCH_DIR,
        )
        # Check that the sbatch directory does not exist
        self.assertTrue(SBATCH_DIR.is_dir())
        # Call the clean method
        se.clean()
        # Check that the sbatch directory still exist and has the sbatch file in it
        self.assertTrue(SBATCH_DIR.is_dir())
        self.assertTrue(list(SBATCH_DIR.glob("*")), ["test_sbatch_shaman.sbatch"])

    @patch("httpx.get", side_effect=mocked_requests_get)
    def test_write_sbatch_remove(self, mocked_requests_get):
        """Tests that if another directory is not specified, the folder containing the sbatch is deleted from the working directory."""
        se = SHAManExperiment(
            component_name="component_1",
            nbr_iteration=3,
            sbatch_file=SBATCH,
            experiment_name="test_experiment",
            configuration_file=CONFIG,
        )
        # Check that a sbatch file is created
        self.assertTrue("test_sbatch_shaman.sbatch" in os.listdir())
        # Call the clean method
        se.clean()
        # Check that the sbatch file is deleted
        self.assertFalse("test_sbatch_shaman.sbatch" in os.listdir())

    @patch("httpx.get", side_effect=mocked_requests_get)
    @patch("bb_wrapper.tunable_component.component.TunableComponent.submit_sbatch")
    @patch("bb_wrapper.bb_wrapper.BBWrapper._parse_slurm_times")
    def test_setup_optimizer_async_default(
        self, mock_submit, mock_parse, mocked_requests_get
    ):
        """
        Tests that when running the optimization in asynchronous mode using default
        as max time, the max duration step of the black-box optimizer is properly setup.
        """
        mock_submit.return_value = 10
        mock_parse.return_value = 10
        se = SHAManExperiment(
            component_name="component_1",
            nbr_iteration=3,
            sbatch_file=SBATCH,
            experiment_name="test_experiment",
            configuration_file=CONFIG_ASYNC_DEFAULT,
        )
        se.bb_wrapper.run_default()
        se.setup_bb_optimizer()
        self.assertEqual(se.bb_optimizer.max_step_cost, 10)

    @patch("httpx.get", side_effect=mocked_requests_get)
    @patch("httpx.Client.post", side_effect=mocked_requests_post)
    @patch("bb_wrapper.bb_wrapper.BBWrapper.run_default")
    @patch("bbo.optimizer.BBOptimizer.optimize")
    @patch("bb_wrapper.shaman_experiment.SHAManExperiment.summarize")
    def test_launch_experiment(
        self,
        mock_summarize,
        mock_optimize,
        mock_default,
        mock_post,
        mocked_requests_get,
    ):
        """Tests the launch of an experiment."""
        mock_default.return_value = 10
        se = SHAManExperiment(
            component_name="component_1",
            nbr_iteration=3,
            sbatch_file=SBATCH,
            experiment_name="test_experiment",
            configuration_file=CONFIG,
            result_file="test_result.out",
        )
        se.launch()
        # Check that result file was created
        assert Path("test_result.out").is_file()
        # Remove file
        Path("test_result.out").unlink()

    @patch("httpx.get", side_effect=mocked_requests_get)
    def test_summarize(self, mocked_requests_get):
        """Tests that the summary of an experiment works as expected."""
        fake_history = {
            "fitness": np.array([2, 2, 3]),
            "parameters": np.array([[1, 2], [2, 2], [1, 2]]),
            "truncated": np.array([True, True, False]),
            "resampled": np.array([False, False, False]),
            "initialization": np.array([False, False, False]),
        }
        se = SHAManExperiment(
            component_name="component_1",
            nbr_iteration=3,
            sbatch_file=SBATCH,
            experiment_name="test_experiment",
            configuration_file=CONFIG_ASYNC_DEFAULT,
        )
        se.bb_optimizer.history = fake_history
        se.bb_optimizer.best_parameters_in_grid = [2, 2]
        se.bb_optimizer.best_fitness = 2
        se.bb_optimizer.launched = True
        se.bb_wrapper.default_execution_time = 10
        expected_summary = """Optimal time: 2
Improvement compared to default:80.0%
Optimal parametrization: [{'param_1': 2, 'param_2': 2}]
Number of early stops: 2
Average noise within each parametrization: [0.5, 0.0]
------ Optimization loop summary ------
Number of iterations: 2
Elapsed time: 0
Best parameters: [2, 2]
Best fitness value: 2
Percentage of explored space: 22.22222222222222
Percentage of static moves: 33.33333333333333
Cost of global exploration: 1
Mean fitness gain per iteration: 0.5
Number of iterations until best fitness: 0
Average variation within each parametrization: [0.5, 0.0]
--- Heuristic specific summary ---
Number of mutations: 0
Family tree:
None
"""
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        se.summarize()
        sys.stdout = sys.__stdout__
        self.assertEqual(expected_summary, capturedOutput.getvalue())

    def tearDown(self):
        """Remove all slurm files from current dir.
        Clean all new created files and directories: SLURM_DIR and SBATCH_DIR"""
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
        parameter_names = ["param1", "param2", "param3"]
        parameter_values = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        expected_out = [
            {"param1": 1, "param2": 2, "param3": 3},
            {"param1": 4, "param2": 5, "param3": 6},
            {"param1": 7, "param2": 8, "param3": 9},
        ]
        dict_param = SHAManExperiment.build_parameter_dict(
            parameter_names, parameter_values
        )
        self.assertListEqual(dict_param, expected_out)

    def test_build_parameter_dict_2(self):
        """ Test the 'build_parameter_dict' method returns the proper dict. """
        parameter_names = ["param1", "param2", "param3"]
        parameter_values = [[1, 2, 3], [4, 5], [6]]
        expected_out = [
            {"param1": 1, "param2": 2, "param3": 3},
            {"param1": 4, "param2": 5},
            {"param1": 6},
        ]
        dict_param = SHAManExperiment.build_parameter_dict(
            parameter_names, parameter_values
        )
        self.assertListEqual(dict_param, expected_out)

    def test_build_parameter_dict_no_list(self):
        """Tests that the build_parameter_dict method returns the proper value if not list of list."""
        parameter_names = ["param1", "param2", "param3"]
        parameter_values = [1, 2, 3]
        expected_out = [{"param1": 1, "param2": 2, "param3": 3}]
        dict_param = SHAManExperiment.build_parameter_dict(
            parameter_names, parameter_values
        )
        self.assertListEqual(dict_param, expected_out)


class TestSHAManAPI(unittest.TestCase):
    """Unit tests for the integration of SHAMan with the REST API."""

    @patch("httpx.get", side_effect=mocked_requests_get)
    def test_api_url(self, mocked_requests_get):
        """
        Tests that the API url is properly built from the settings.
        """
        se = SHAManExperiment(
            component_name="component_1",
            nbr_iteration=3,
            sbatch_file=SBATCH,
            experiment_name="test_experiment",
            configuration_file=CONFIG,
        )
        self.assertEqual(se.api_url, "http://127.0.0.1:5000")

    @patch("httpx.get", side_effect=mocked_requests_get)
    def test_start_experiment_dict_vanilla(self, mocked_requests_get):
        """
        Tests that the dictionnary describing the experiment from its start works as expected.
        No pruning and no noise reduction.
        """
        se = SHAManExperiment(
            component_name="component_1",
            nbr_iteration=3,
            sbatch_file=SBATCH,
            experiment_name="test_experiment",
            configuration_file=CONFIG,
        )
        expected_dict = {
            "experiment_name": "test_experiment",
            "experiment_start": datetime.utcnow().strftime("%y/%m/%d %H:%M:%S"),
            "experiment_budget": 3,
            "component": "component_1",
            "experiment_parameters": {
                "heuristic": "genetic_algorithm",
                "initial_sample_size": 2,
                "selection_method": "bbo.heuristics.genetic_algorithm.selections.tournament_pick",
                "crossover_method": "bbo.heuristics.genetic_algorithm.crossover.single_point_crossover",
                "mutation_method": "bbo.heuristics.genetic_algorithm.mutations.mutate_chromosome_to_neighbor",
                "pool_size": 5,
                "mutation_rate": 0.4,
                "elitism": False,
            },
            "noise_reduction_strategy": {},
            "pruning_strategy": {"pruning_strategy": None},
            "sbatch": "#!/bin/bash\n#SBATCH --job-name=TestJob\n#SBATCH --ntasks=3\nhostname",
        }
        self.assertDictEqual(expected_dict, se.start_experiment_dict)

    @patch("httpx.get", side_effect=mocked_requests_get)
    def test_start_experiment_dict_pruning(self, mocked_requests_get):
        """Tests that the experiment dict is as expected when pruning is enabled."""
        se = SHAManExperiment(
            component_name="component_1",
            nbr_iteration=3,
            sbatch_file=SBATCH,
            experiment_name="test_experiment",
            configuration_file=CONFIG_ASYNC,
        )
        expected_dict = {
            "experiment_name": "test_experiment",
            "experiment_start": datetime.utcnow().strftime("%y/%m/%d %H:%M:%S"),
            "experiment_budget": 3,
            "component": "component_1",
            "experiment_parameters": {
                "heuristic": "genetic_algorithm",
                "initial_sample_size": 2,
                "selection_method": "bbo.heuristics.genetic_algorithm.selections.tournament_pick",
                "crossover_method": "bbo.heuristics.genetic_algorithm.crossover.single_point_crossover",
                "mutation_method": "bbo.heuristics.genetic_algorithm.mutations.mutate_chromosome_to_neighbor",
                "pool_size": 5,
                "mutation_rate": 0.4,
                "elitism": False,
            },
            "noise_reduction_strategy": {},
            "pruning_strategy": {"pruning_strategy": 5},
            "sbatch": "#!/bin/bash\n#SBATCH --job-name=TestJob\n#SBATCH --ntasks=3\nhostname",
        }
        self.assertDictEqual(se.start_experiment_dict, expected_dict)

    @patch("httpx.get", side_effect=mocked_requests_get)
    def test_start_experiment_dict_noise_reduction(self, mocked_requests_get):
        """Tests that the experiment dict is as expected when noise reduction is enabled."""
        se = SHAManExperiment(
            component_name="component_1",
            nbr_iteration=3,
            sbatch_file=SBATCH,
            experiment_name="test_experiment",
            configuration_file=CONFIG_NOISE,
        )
        expected_dict = {
            "experiment_name": "test_experiment",
            "experiment_start": datetime.utcnow().strftime("%y/%m/%d %H:%M:%S"),
            "experiment_budget": 3,
            "component": "component_1",
            "experiment_parameters": {
                "heuristic": "genetic_algorithm",
                "initial_sample_size": 2,
                "selection_method": "bbo.heuristics.genetic_algorithm.selections.tournament_pick",
                "crossover_method": "bbo.heuristics.genetic_algorithm.crossover.single_point_crossover",
                "mutation_method": "bbo.heuristics.genetic_algorithm.mutations.mutate_chromosome_to_neighbor",
                "pool_size": 5,
                "mutation_rate": 0.4,
                "elitism": False,
            },
            "noise_reduction_strategy": {
                "resampling_policy": "simple_resampling",
                "nbr_resamples": 3,
                "fitness_aggregation": "simple_fitness_aggregation",
                "estimator": "numpy.median",
            },
            "pruning_strategy": {"pruning_strategy": None},
            "sbatch": "#!/bin/bash\n#SBATCH --job-name=TestJob\n#SBATCH --ntasks=3\nhostname",
        }
        self.assertEqual(se.start_experiment_dict, expected_dict)

    @patch("httpx.get", side_effect=mocked_requests_get)
    @patch("httpx.Client.post", side_effect=mocked_requests_post)
    def test_create_experiment(self, mock_httpx, mocked_requests_get):
        """
        Tests that the creation of the experiment behaves as expected, by adding the experiemnt_id
        as an attribute.
        """
        # Create the experiment
        se = SHAManExperiment(
            component_name="component_1",
            nbr_iteration=3,
            sbatch_file=SBATCH,
            experiment_name="test_experiment",
            configuration_file=CONFIG,
        )
        se.create_experiment()
        self.assertEqual(se.experiment_id, "123")

    @patch("httpx.get", side_effect=mocked_requests_get)
    @patch("httpx.Client.post", side_effect=mocked_requests_post_fail)
    def test_create_experiment_fail(self, mock_httpx, mocked_requests_get):
        """
        Tests that when the create experiment fails, an exception is raised.
        """
        # Create the experiment
        se = SHAManExperiment(
            component_name="component_1",
            nbr_iteration=3,
            sbatch_file=SBATCH,
            experiment_name="test_experiment",
            configuration_file=CONFIG,
        )
        with self.assertRaises(Exception):
            se.create_experiment()

    @patch("httpx.get", side_effect=mocked_requests_get)
    def test_best_time(self, mocked_requests_get):
        """Tests that the best time is properly computed."""
        se = SHAManExperiment(
            component_name="component_1",
            nbr_iteration=3,
            sbatch_file=SBATCH,
            experiment_name="test_experiment",
            configuration_file=CONFIG,
        )
        se.bb_optimizer.history = {
            "fitness": np.array([2, 2, 3]),
            "parameters": np.array([[1, 2], [2, 2], [1, 2]]),
        }
        self.assertEqual(se.best_time, 2)

    @patch("httpx.get", side_effect=mocked_requests_get)
    def test_average_noise(self, mocked_requests_get):
        """Tests that the average noise is properly computed."""
        se = SHAManExperiment(
            component_name="component_1",
            nbr_iteration=3,
            sbatch_file=SBATCH,
            experiment_name="test_experiment",
            configuration_file=CONFIG,
        )
        se.bb_optimizer.history = {
            "fitness": np.array([2, 2, 3]),
            "parameters": np.array([[1, 2], [2, 2], [1, 2]]),
        }
        self.assertEqual(se.average_noise, 0.25)

    @patch("httpx.get", side_effect=mocked_requests_get)
    @patch("bb_wrapper.tunable_component.component.TunableComponent.submit_sbatch")
    @patch("bb_wrapper.bb_wrapper.BBWrapper._parse_slurm_times")
    def test_improvement_default(self, mock_submit, mock_parse, mocked_requests_get):
        """Tests that the improvement is properly computed."""
        mock_submit.return_value = 10
        mock_parse.return_value = 10
        se = SHAManExperiment(
            component_name="component_1",
            nbr_iteration=3,
            sbatch_file=SBATCH,
            experiment_name="test_experiment",
            configuration_file=CONFIG,
        )
        se.bb_wrapper.run_default()
        se.bb_optimizer.history = {
            "fitness": np.array([2, 2, 3]),
            "parameters": np.array([[1, 2], [2, 2], [1, 2]]),
        }
        self.assertEqual(se.improvement_default, 80)

    @patch("httpx.get", side_effect=mocked_requests_get)
    @patch("bb_wrapper.tunable_component.component.TunableComponent.submit_sbatch")
    @patch("bb_wrapper.bb_wrapper.BBWrapper._parse_slurm_times")
    def test_update_history_dict(self, mock_submit, mock_parse, mocked_requests_get):
        """
        Tests that the update history dict is filled as expected.
        """
        mock_parse.return_value = 10
        mock_submit.return_value = 10
        fake_history = {
            "fitness": np.array([2, 2, 3]),
            "parameters": np.array([[1, 2], [2, 2], [1, 2]]),
            "truncated": np.array([True, True, False]),
            "resampled": np.array([False, False, False]),
            "initialization": np.array([False, False, False]),
        }
        expected_dict = {
            "jobids": 10,
            "execution_time": 3,
            "parameters": {"param_1": 1, "param_2": 2},
            "truncated": False,
            "resampled": False,
            "initialization": False,
            "improvement_default": 80,
            "average_noise": 0.25,
        }
        se = SHAManExperiment(
            component_name="component_1",
            nbr_iteration=3,
            sbatch_file=SBATCH,
            experiment_name="test_experiment",
            configuration_file=CONFIG,
        )
        # Compute once to build the .component
        se.bb_wrapper.compute([1, 2])
        se.bb_optimizer.history = fake_history
        se.bb_wrapper.component.submitted_jobids = [10, 10]
        se.bb_wrapper.run_default()
        self.assertEqual(se._updated_dict(fake_history), expected_dict)

    @patch("httpx.get", side_effect=mocked_requests_get)
    @patch("bb_wrapper.tunable_component.component.TunableComponent.submit_sbatch")
    @patch("bb_wrapper.bb_wrapper.BBWrapper._parse_slurm_times")
    @patch("httpx.Client.put", side_effect=mocked_requests_put)
    def test_update_history(
        self, mock_update, mock_parse, mock_submit, mocked_requests_get
    ):
        """
        Tests that the update_history function works as expected.
        """
        mock_submit.return_value = 10
        mock_parse.return_value = 10
        se = SHAManExperiment(
            component_name="component_1",
            nbr_iteration=3,
            sbatch_file=SBATCH,
            experiment_name="test_experiment",
            configuration_file=CONFIG,
        )
        update_dict = {
            "jobids": 10,
            "execution_time": 3,
            "parameters": {"param_1": 1, "param_2": 2},
            "truncated": False,
            "resampled": False,
            "initialization": False,
            "improvement_default": 80,
            "average_noise": 0.25,
        }
        se.experiment_id = "123"

        # Compute enough information to get update dict
        se.bb_wrapper.compute([1, 2])
        fake_history = {
            "fitness": np.array([2, 2, 3]),
            "parameters": np.array([[1, 2], [2, 2], [1, 2]]),
            "truncated": np.array([True, True, False]),
            "resampled": np.array([False, False, False]),
            "initialization": np.array([False, False, False]),
        }
        se.bb_wrapper.component.submitted_jobids = [10, 10]
        se.bb_wrapper.run_default()
        se.bb_optimizer.history = fake_history
        se.update_history(fake_history)

    @patch("httpx.get", side_effect=mocked_requests_get)
    @patch("bb_wrapper.tunable_component.component.TunableComponent.submit_sbatch")
    @patch("bb_wrapper.bb_wrapper.BBWrapper._parse_slurm_times")
    @patch("httpx.Client.put", side_effect=mocked_requests_put)
    def test_update_history_fail(
        self, mock_update, mock_parse, mock_submit, mocked_requests_get
    ):
        """
        Tests that the update_history function works as expected when there is a failure.
        """
        mock_submit.return_value = 10
        mock_parse.return_value = 10
        se = SHAManExperiment(
            component_name="component_1",
            nbr_iteration=3,
            sbatch_file=SBATCH,
            experiment_name="test_experiment",
            configuration_file=CONFIG,
        )
        update_dict = {
            "jobids": 10,
            "execution_time": 3,
            "parameters": {"param_1": 1, "param_2": 2},
            "truncated": False,
            "resampled": False,
            "initialization": False,
            "improvement_default": 80,
            "average_noise": 0.25,
        }
        se.experiment_id = "321"

        se.bb_wrapper.compute([1, 2])
        fake_history = {
            "fitness": np.array([2, 2, 3]),
            "parameters": np.array([[1, 2], [2, 2], [1, 2]]),
            "truncated": np.array([True, True, False]),
            "resampled": np.array([False, False, False]),
            "initialization": np.array([False, False, False]),
        }
        se.bb_optimizer.history = fake_history
        se.bb_wrapper.component.submitted_jobids = [10, 10]
        se.bb_wrapper.run_default()
        with self.assertRaises(Exception):
            se.update_history(fake_history)

    @patch("httpx.get", side_effect=mocked_requests_get)
    @patch("bb_wrapper.tunable_component.component.TunableComponent.submit_sbatch")
    @patch("bb_wrapper.bb_wrapper.BBWrapper._parse_slurm_times")
    def test_end_dict(self, mock_parse, mock_submit, mocked_requests_get):
        """Tests that the improvement is properly computed."""
        self.maxDiff = None
        mock_submit.return_value = 10
        mock_parse.return_value = 10
        se = SHAManExperiment(
            component_name="component_1",
            nbr_iteration=3,
            sbatch_file=SBATCH,
            experiment_name="test_experiment",
            configuration_file=CONFIG,
        )
        se.bb_wrapper.run_default()
        fake_history = {
            "fitness": np.array([2, 2, 3]),
            "parameters": np.array([[1, 2], [2, 2], [1, 2]]),
            "truncated": np.array([True, True, False]),
            "resampled": np.array([False, False, False]),
            "initialization": np.array([False, False, False]),
        }
        se.bb_optimizer.history = fake_history
        expected_dict = {
            "averaged_execution_time": [2.0, 2.0, 3.0],
            "min_execution_time": [2.0, 2.0, 3.0],
            "max_execution_time": [2.0, 2.0, 3.0],
            "std_execution_time": [0.5, 0.0],
            "resampled_nbr": [1.0, 1.0, 1.0],
            "improvement_default": 80.0,
            "elapsed_time": 0,
            "default_run": {
                "execution_time": 10.0,
                "job_id": 10,
                "parameters": {"param_1": 1, "param_2": "/home/"},
            },
            "average_noise": 0.25,
            "explored_space": 22.22222222222222,
        }
        self.assertDictEqual(expected_dict, se.end_dict)

    @patch("httpx.get", side_effect=mocked_requests_get)
    @patch("bb_wrapper.tunable_component.component.TunableComponent.submit_sbatch")
    @patch("bb_wrapper.bb_wrapper.BBWrapper._parse_slurm_times")
    @patch("httpx.Client.put", side_effect=mocked_requests_put)
    def test_end(self, mock_put, mock_parse, mock_submit, mocked_requests_get):
        """
        Tests that calling the end endpoint works as expected.
        """
        mock_submit.return_value = 10
        mock_parse.return_value = 10
        se = SHAManExperiment(
            component_name="component_1",
            nbr_iteration=3,
            sbatch_file=SBATCH,
            experiment_name="test_experiment",
            configuration_file=CONFIG,
        )
        se.experiment_id = "123"
        se.bb_wrapper.run_default()
        fake_history = {
            "fitness": np.array([2, 2, 3]),
            "parameters": np.array([[1, 2], [2, 2], [1, 2]]),
            "truncated": np.array([True, True, False]),
            "resampled": np.array([False, False, False]),
            "initialization": np.array([False, False, False]),
        }
        se.bb_optimizer.history = fake_history
        se.end()

    @patch("httpx.get", side_effect=mocked_requests_get)
    @patch("bb_wrapper.tunable_component.component.TunableComponent.submit_sbatch")
    @patch("bb_wrapper.bb_wrapper.BBWrapper._parse_slurm_times")
    @patch("httpx.Client.put", side_effect=mocked_requests_put)
    def test_end_fail(self, mock_put, mock_parse, mock_submit, mocked_requests_get):
        """
        Tests that calling the end endpoint works as expected when the api returns a 500 status
        code.
        """
        mock_submit.return_value = 10
        mock_parse.return_value = 10
        se = SHAManExperiment(
            component_name="component_1",
            nbr_iteration=3,
            sbatch_file=SBATCH,
            experiment_name="test_experiment",
            configuration_file=CONFIG,
        )
        se.experiment_id = "321"
        se.bb_wrapper.run_default()
        fake_history = {
            "fitness": np.array([2, 2, 3]),
            "parameters": np.array([[1, 2], [2, 2], [1, 2]]),
            "truncated": np.array([True, True, False]),
            "resampled": np.array([False, False, False]),
            "initialization": np.array([False, False, False]),
        }
        se.bb_optimizer.history = fake_history
        with self.assertRaises(Exception):
            se.end()

    @patch("httpx.get", side_effect=mocked_requests_get)
    @patch("httpx.Client.put", side_effect=mocked_requests_put)
    def test_fail_fail(self, mock_put, mocked_requests_get):
        """Tests the right error code is returned when the submitted experiment fails."""
        se = SHAManExperiment(
            component_name="component_1",
            nbr_iteration=3,
            sbatch_file=SBATCH,
            experiment_name="test_experiment",
            configuration_file=CONFIG,
        )
        se.experiment_id = "322"
        with self.assertRaises(Exception):
            se.fail()

    @patch("httpx.get", side_effect=mocked_requests_get)
    @patch("httpx.Client.put", side_effect=mocked_requests_put)
    def test_stop(self, mock_put, mocked_requests_get):
        """Tests that stopping the experiment works as expected."""
        se = SHAManExperiment(
            component_name="component_1",
            nbr_iteration=3,
            sbatch_file=SBATCH,
            experiment_name="test_experiment",
            configuration_file=CONFIG,
        )
        se.experiment_id = "123"
        se.stop()

    @patch("httpx.get", side_effect=mocked_requests_get)
    @patch("httpx.Client.put", side_effect=mocked_requests_put)
    def test_stop_fail(self, mock_put, mocked_requests_get):
        """Tests that stopping the experiment works as expected when failing."""
        se = SHAManExperiment(
            component_name="component_1",
            nbr_iteration=3,
            sbatch_file=SBATCH,
            experiment_name="test_experiment",
            configuration_file=CONFIG,
        )
        se.experiment_id = "321"
        with self.assertRaises(Exception):
            se.stop()


if __name__ == "__main__":
    unittest.main(verbosity=2)
