# Copyright 2020 BULL SAS All rights reserved
"""
Tests that the component model behaves as expected.
"""
import unittest
from unittest.mock import patch
from pathlib import Path

from pydantic import ValidationError
from shaman_core.models.component_model import (
    TunableComponentModel,
    TunableParameter,
    TunableComponentsModel,
)


TEST_MODEL = {
    "plugin": "test",
    "header": "test",
    "command": "test",
    "ld_preload": "test",
}


TEST_PARAMETERS_OK = {
    "param_1": {"type": "int", "default": 1, "optional": True, "env_var": True}
}

TEST_PARAMETERS_UNKNOWN_TYPE = {
    "param_1": {"type": "toto", "default": 1, "optional": True, "env_var": True}
}

TEST_PARAMETERS_SUFFIX = {
    "param_1": {
        "type": "int",
        "default": 1,
        "optional": True,
        "env_var": True,
        "suffix": "K",
    }
}

TEST_PARAMETERS_CLI_VAR = {
    "param_1": {
        "type": "int",
        "default": 1,
        "optional": True,
        "cli_var": True,
        "suffix": "K",
    }
}

TEST_PARAMETERS_CMD_NO_FLAG = {
    "param_1": {
        "type": "int",
        "default": 1,
        "optional": True,
        "env_var": True,
        "description": "Test description",
        "cmd_var": True,
    }
}


TEST_PARAMETERS_NO_CMD_NO_ENV = {
    "param_1": {"type": "int", "optional": True, "description": "Test description"}
}


TEST_PARAMETERS_WRONG_TYPE = {
    "param_1": {"type": "int", "default": "home", "optional": True, "env_var": True}
}

TEST_COMPONENT_CONFIG = Path(__file__).parent / \
    "test_component_config" / "test.yaml"


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
    elif args[0] == "http://mock_api:5000/component":
        mock_components = {"state": "failure"}
        return MockResponse(mock_components, 504)


class TestComponentModels(unittest.TestCase):
    """Test that the component model behaves as expected.
    As the configuration relies on Pydantic, this tests only the custom validators.
    """

    def test_unknown_type(self):
        """Tests that an error is raised when the specified type is unknown.
        """
        TEST_MODEL.update({"parameters": TEST_PARAMETERS_UNKNOWN_TYPE})
        with self.assertRaises(AttributeError):
            TunableComponentModel(**TEST_MODEL)

    def test_parameters_ok(self):
        """Tests that when the parameters are properly specified, everything is ok.
        """
        TEST_MODEL.update({"parameters": TEST_PARAMETERS_OK})
        tunable_component = TunableComponentModel(**TEST_MODEL)

    def test_parameters_suffix(self):
        """Tests that when there is a suffix, everything is ok.
        """
        TEST_MODEL.update({"parameters": TEST_PARAMETERS_SUFFIX})
        tunable_component = TunableComponentModel(**TEST_MODEL)
        self.assertEqual(tunable_component.parameters["param_1"].suffix, "K")

    def test_parameters_cli_var(self):
        """Tests that when a variable is a CLI variable, everything is ok.
        """
        TEST_MODEL.update({"parameters": TEST_PARAMETERS_CLI_VAR})
        tunable_component = TunableComponentModel(**TEST_MODEL)
        self.assertEqual(tunable_component.parameters["param_1"].cli_var, True)

    def test_no_cmd_no_env(self):
        """Tests that when a parameter is not specified to be either a environment variable or a
        command line variable.
        """
        TEST_MODEL.update({"parameters": TEST_PARAMETERS_NO_CMD_NO_ENV})
        with self.assertRaises(ValueError):
            TunableComponentModel(**TEST_MODEL)

    def test_parameters_wrong_type(self):
        """Tests that when the type of the default does not match the announced type, a TypeError is
        raised.
        """
        TEST_MODEL.update({"parameters": TEST_PARAMETERS_WRONG_TYPE})
        with self.assertRaises(ValidationError):
            TunableComponentModel(**TEST_MODEL)

    def test_load_component_from_yaml(self):
        """
        Tests that loading a component from a YAML file behaves as expected.
        """
        tunable_components = TunableComponentsModel.from_yaml(
            TEST_COMPONENT_CONFIG)
        assert tunable_components.components["component_1"].plugin == "example_1"
        assert tunable_components.components["component_2"].plugin == "example_2"

    @patch("httpx.get", side_effect=mocked_requests_get)
    def test_load_component_from_api(self, mocked_request):
        """
        Tests that loading a component configuration file from the API behaves as expected.
        """
        tunable_components = TunableComponentsModel.from_api(
            "http://mock_api:5000/components"
        )
        assert tunable_components.components["component_1"].plugin == "example_1"
        assert tunable_components.components["component_2"].plugin == "example_2"

    @patch("httpx.get", side_effect=mocked_requests_get)
    def test_load_component_from_api_error(self, mocked_request):
        """
        Tests that loading a component configuration from the API fails when the status code is <= 200 and > 400
        """
        with self.assertRaises(Exception):
            tunable_components = TunableComponentsModel.from_api(
                "http://mock_api:5000/component"
            )


if __name__ == "__main__":
    unittest.main()
