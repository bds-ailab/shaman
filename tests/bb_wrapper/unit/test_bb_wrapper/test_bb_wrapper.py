# Copyright 2020 BULL SAS All rights reserved
"""
Tests that the BBWrapper class behaves as expected.
"""
import unittest
from unittest.mock import patch

import subprocess
from pathlib import Path
from shutil import copy
from bb_wrapper.bb_wrapper import BBWrapper

# Test config component
TEST_CONFIG = Path(__file__).parent / "test_config"
COMPONENT_CONFIG = TEST_CONFIG / "component_config.yaml"

# Test slurms
TEST_SLURMS = Path(__file__).parent / "test_slurm_outputs"

# Test sbatch
TEST_SBATCH = Path(__file__).parent / "test_sbatch"


CURRENT_DIR = Path.cwd()


class MockResponse:
    def __init__(self, json_data, status_code):
        self.json_data = json_data
        self.status_code = status_code

    def json(self):
        return self.json_data


def mocked_requests_get(*args, **kwargs):
    """Mocks the post requests.
    """
    if args[0] == "http://mock_api:5000/components":
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
    if args[0] == "http://mock_api:500/component":
        return MockResponse({}, 404)


class TestBBWrapper(unittest.TestCase):
    """Tests that the BBWrapper class behaves as expected.
    """

    def setUp(self):
        """
        Creates a bb_wrapper attribute to be tested.
        """
        self.bb_wrapper = BBWrapper(
            component_name="component_1",
            parameter_names=["param_1", "param_2"],
            component_configuration=COMPONENT_CONFIG,
            sbatch_file=str(TEST_SBATCH / "test_sbatch.sbatch"),
            sbatch_dir=str(TEST_SBATCH),
        )

    def test_initialization(self):
        """Tests the proper initialization of the class.
        """
        self.assertEqual(self.bb_wrapper.component_name, "component_1")

    def test_initialization_api(self):
        """Tests the proper initialization of the class when succesfully loading the component configuration
        file from the API.

        #TODO
        """

    def test_copy_sbatch_time(self):
        """Tests that copying the sbatch to add a time command behaves as expected.
        """
        sbatch_file = TEST_SBATCH / "test_sbatch.sbatch"
        expected_lines = [
            "#!/bin/bash\n",
            "#SBATCH --job-name=TestJob\n",
            "#SBATCH --ntasks=3\n",
            "time (\n",
            "hostname)",
        ]
        new_path = self.bb_wrapper.copy_sbatch(sbatch_file)
        with open(new_path) as read_file:
            lines = read_file.readlines()
        self.assertEqual(new_path, TEST_SBATCH / "test_sbatch_shaman.sbatch")
        self.assertListEqual(lines, expected_lines)

    def test_copy_sbatch_no_time(self):
        """Tests that copying the sbatch to add a time command to a non-timed sbatch behaves as
        expected.
        """
        original_file = TEST_SBATCH / "test_sbatch_timed.sbatch"
        with open(original_file) as orig_file:
            expected_lines = orig_file.readlines()
        new_path = self.bb_wrapper.copy_sbatch(original_file)
        with open(new_path) as read_file:
            lines = read_file.readlines()
        self.assertEqual(
            new_path,
            TEST_SBATCH /
            "test_sbatch_timed_shaman.sbatch")
        self.assertListEqual(lines, expected_lines)
        Path(new_path).unlink()

    @patch("bb_wrapper.tunable_component.component.TunableComponent.submit_sbatch")
    def test_compute(self, mock_submit_sbatch):
        """Tests that the compute method behaves as expected.
        """
        mock_submit_sbatch.return_value = 42
        # Move the test slurm-42.out file into current directory
        copy(TEST_SLURMS / "slurm-42.out", CURRENT_DIR)
        param = [6, 9]
        time = self.bb_wrapper.compute(param)
        self.assertListEqual(self.bb_wrapper.jobids, [42])
        self.assertEqual(time, 1508.085)

    @patch("bb_wrapper.tunable_component.component.TunableComponent.submit_sbatch")
    def test_run_default(self, mock_submit_sbatch):
        """Tests that running the default parametrization behaves as expected.
        """
        mock_submit_sbatch.return_value = 42
        # Move the test slurm-42.out file into current directory
        copy(TEST_SLURMS / "slurm-42.out", CURRENT_DIR)
        _ = self.bb_wrapper.run_default()
        # Check that the default jobid is properly stored
        self.assertEqual(self.bb_wrapper.default_jobid, 42)
        # Check that the execution time is properly stored
        self.assertEqual(self.bb_wrapper.default_execution_time, 1508.085)
        # Check that the default parameters of the accelerator are properly
        # stored
        default_parameters = {"param_1": 1, "param_2": "/home/"}
        self.assertDictEqual(
            self.bb_wrapper.default_parameters,
            default_parameters)
            
    @patch("subprocess.run")
    def test_parse_job_elapsed_time(self, mock_stdout):
        """Tests that parsing a job elapsed time through a subprocess call calling the
        squeue command works as expected.
        """
        mock_stdout.return_value.stdout = "'             JOBID PARTITION     NAME     USER ST       TIME  NODES NODELIST(REASON)\n                 9       all    sleep     root  R       0:30      1 compute1\n'".encode(
        )
        time = self.bb_wrapper.parse_job_elapsed_time(2)
        self.assertEqual(30, time)

    @patch("subprocess.run")
    def test_scancel_job(self, mock_stdout):
        """Tests that scanceling a job through a subprocess call of the scancel command works as
        expected. Test is bogus.
        """
        mock_stdout.return_value.returncode = 0

    def tearDown(self):
        """
        Cleans out the test repository by deleting copied slurm file.
        """
        try:
            Path.unlink(TEST_SBATCH / "test_sbatch_shaman.sbatch")
        except FileNotFoundError:
            pass
        try:
            Path.unlink(CURRENT_DIR / "slurm-42.out")
        except FileNotFoundError:
            pass


if __name__ == "__main__":
    unittest.main()
