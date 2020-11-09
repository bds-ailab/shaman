# Copyright 2020 BULL SAS All rights reserved
"""Tests the tunable component behavior.
"""

import os
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

from bb_wrapper.tunable_component.component import TunableComponent


TEST_COMPONENT_CONFIG = Path(__file__).parent / \
    "test_component_config" / "test.yaml"
# Test config component

TEST_SBATCH = Path(__file__).parent / "test_data" / "test_sbatch.sbatch"
# Test sbatch
TEST_SBATCH_HEADER = Path(__file__).parent / \
    "test_data" / "test_sbatch_header.sbatch"

# Save current environment variable into a variable
current_var_env = os.environ.copy()


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
                        "param_4": {
                            "type": "str",
                            "default": None,
                            "optional": False,
                            "env_var": None,
                            "description": None,
                            "cmd_var": "True",
                        },
                        "param_5": {
                            "type": "str",
                            "default": None,
                            "optional": False,
                            "env_var": None,
                            "description": None,
                            "cmd_var": "True",
                            "flag": "s",
                            "suffix": "K",
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


class TestTunableComponent(unittest.TestCase):
    """Tests that the TunableComponent class works properly."""

    def test_class_initialization_yaml(self):
        """Checks the proper initialization of the TunableComponent class through a YAML file."""
        TunableComponent(
            name="component_1",
            module_configuration=TEST_COMPONENT_CONFIG)

    def test_configuration_not_found(self):
        """Check that a file not found error is raised when the configuration module can't be found.
        """
        with self.assertRaises(FileNotFoundError):
            TunableComponent(
                name="component_1",
                module_configuration="/file/which/does/not/exist.yaml",
            )

    def test_configuration_wrong_format(self):
        """Check that if the configuration file has the wrong format an error is raised.
        """
        with self.assertRaises(ValueError):
            TunableComponent(
                name="component_1", module_configuration="/file/which/is/a/text.txt"
            )

    @patch("httpx.get", side_effect=mocked_requests_get)
    def test_configuration_api(self, mocked_request):
        """Check that loading the configuration through the API works as expected.
        """
        component = TunableComponent(
            name="component_1", module_configuration="http://mock_api:5000/components"
        )

    def test_configuration_unknown_name(self):
        """Check that a key error is raised when calling a component with an unknown name.
        """
        with self.assertRaises(KeyError):
            TunableComponent(
                name="component_0", module_configuration=TEST_COMPONENT_CONFIG
            )

    def test_build_cmdline(self):
        """Tests that the command line is correctly built, when:
            - There is a flag longer than 1 in length
            - There is a flag of size 1
            - There is no flag
            - There is a suffix
        """
        tunable_component = TunableComponent(
            name="component_2",
            module_configuration=TEST_COMPONENT_CONFIG,
            parameters={"param_3": "/home/", "param_4": "5", "param_5": "6"},
        )
        expected_cmdline = "example_cmd --folder /home/ -f /home/ param_4=5 -s 6K"
        self.assertEqual(tunable_component.cmd_line, expected_cmdline)

    def test_cmd_line_empty(self):
        """Tests that when the command line does not exist in the configuration file, an empty
        string is returned.
        """
        tunable_component = TunableComponent(
            "component_3", TEST_COMPONENT_CONFIG, parameters={}
        )
        self.assertEqual(tunable_component.cmd_line, "")

    def test_wrong_parameters_format(self):
        """Tests that setting parameters that are not dict as parameters raises a type error."""
        no_dict_parameters = [1, 2, 3]
        with self.assertRaises(TypeError):
            TunableComponent(
                name="component_2",
                module_configuration=TEST_COMPONENT_CONFIG,
                parameters=no_dict_parameters,
            )

    def test_get_default_parameters(self):
        """Tests that the default parameters are properly selected from the configuration file."""
        tunable_component = TunableComponent(
            "component_2", TEST_COMPONENT_CONFIG, {"param_3": "/home/"}
        )
        expected_parameters = {
            "param_1": 1,
            "param_2": "/home/",
            "param_3": "/home/",
            "param_4": "4",
            "param_5": "5",
        }
        self.assertDictEqual(tunable_component.parameters, expected_parameters)

    def test_overide_default_parameters(self):
        """Tests that the default parameters are properly overriden when specified out of the
        configuration file."""
        parameters = {
            "param_1": 10,
            "param_3": "/home/",
            "param_4": "8",
            "param_5": "7",
        }
        tunable_component = TunableComponent(
            "component_2", TEST_COMPONENT_CONFIG, parameters
        )
        expected_parameters = {
            "param_1": 10,
            "param_2": "/home/",
            "param_3": "/home/",
            "param_4": "8",
            "param_5": "7",
        }
        self.assertDictEqual(tunable_component.parameters, expected_parameters)

    def test_missing_parameters(self):
        """Tests that a ValueError is raised when a parameter present in the configuration
        file is missing, has no default and is not optional."""
        parameters_missing = {"param_2": 5}
        with self.assertRaises(ValueError):
            TunableComponent(
                "component_2",
                TEST_COMPONENT_CONFIG,
                parameters_missing)

    def test_setup_var_env_default(self):
        """Tests that the environment variables are properly setup using default values."""
        tunable_component = TunableComponent(
            "component_1", TEST_COMPONENT_CONFIG)
        tunable_component.setup_var_env()
        expected_var_env = {"param_1": "1"}
        expected_var_env.update(current_var_env)
        self.assertDictContainsSubset(
            tunable_component.var_env, expected_var_env)

    def test_setup_var_env(self):
        """Tests that the environment variables are properly setup using non-default values."""
        tunable_component = TunableComponent(
            "component_1", TEST_COMPONENT_CONFIG, {"param_1": 10}
        )
        tunable_component.setup_var_env()
        expected_var_env = {"param_1": "10"}
        expected_var_env.update(current_var_env)
        self.assertDictContainsSubset(
            tunable_component.var_env, expected_var_env)

    def test_optional_parameters(self):
        """Tests that when an optional parameter is specified, it is taken into account."""
        tunable_component = TunableComponent(
            "component_4", TEST_COMPONENT_CONFIG, {"param_1": 10}
        )
        self.assertDictEqual(tunable_component.parameters, {"param_1": 10})

    def test_optional_no_parameters(self):
        """Tests that when an optional parameter is not specified, it is not taken into account."""
        tunable_component = TunableComponent(
            "component_4", TEST_COMPONENT_CONFIG)
        # self.assertDictEqual(tunable_component.parameters,  {})

    def test_edit_sbatch(self):
        """Tests that editing the sbatch by adding a header, a ld_preload and the command line works properly."""
        tunable_component = TunableComponent(
            "component_1", TEST_COMPONENT_CONFIG)
        # Create new sbatch
        new_sbatch = tunable_component.add_header_sbatch(TEST_SBATCH)
        # Checks that the header has been added
        with open(new_sbatch, "r") as f:
            lines = [line.strip() for line in f.readlines()]
            self.assertTrue(tunable_component.description.header in lines)
            self.assertTrue(
                f"LD_PRELOAD={tunable_component.description.ld_preload}" in lines
            )
            self.assertTrue(tunable_component.cmd_line in lines)
        # Close the file and remove the new sbatch
        f.close()
        os.remove(new_sbatch)

    def test_cmd_line(self):
        """Tests that the command line is correctly built, given the different
        possible configuration."""
        tunable_component = TunableComponent(
            "component_1", TEST_COMPONENT_CONFIG)
        # Command line without wait option
        cmd_line_no_wait = tunable_component._build_sbatch_cmd_line(
            TEST_SBATCH, wait=False
        )
        expected_cmd_line_no_wait = f"sbatch --example_1 {TEST_SBATCH}"
        self.assertEqual(
            cmd_line_no_wait,
            expected_cmd_line_no_wait,
            "Problem with building command line building without wait mode.",
        )
        # Command line with wait option
        cmd_line_wait = tunable_component._build_sbatch_cmd_line(
            TEST_SBATCH, wait=True)
        expected_cmd_line_wait = f"sbatch --wait --example_1 {TEST_SBATCH}"
        self.assertEqual(
            cmd_line_wait,
            expected_cmd_line_wait,
            "Problem with building command line building with wait mode activated.",
        )

    def test_cmd_line_flag(self):
        """Tests that the command line is correctly builts when there are cli vars.
        """
        tunable_component_flag = TunableComponent(
            "component_5", TEST_COMPONENT_CONFIG, parameters={}
        )
        # Command line with full length flag
        # Command line with abbreviated flag
        # Command line with a suffix
        cmd_line_cli_var = tunable_component_flag._build_sbatch_cmd_line(
            TEST_SBATCH, wait=False
        )
        cmd_line_cli_var_expected = (
            f"sbatch --example_5 --folder /home/ -s 5 param_3=4K {TEST_SBATCH}"
        )
        self.assertEqual(
            cmd_line_cli_var,
            cmd_line_cli_var_expected,
            "Problem with building command line building with cli vars activated.",
        )


if __name__ == "__main__":
    unittest.main()
