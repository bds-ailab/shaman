"""
Tests that the component model behaves as expected.
"""
import unittest
from pathlib import Path

from pydantic import ValidationError
from bb_wrapper.tunable_component.component_model import TunableComponentModel, TunableParameter, TunableComponentsModel


TEST_MODEL = {
    "plugin": "test",
    "header": "test",
    "command": "test",
    "ld_preload": "test",
}


TEST_PARAMETERS_OK = {
    "param_1": {
        "type": "int",
        "default": 1,
        "optional": True,
        "env_var": True
    }
}

TEST_PARAMETERS_UNKNOWN_TYPE = {
    "param_1": {
        "type": "toto",
        "default": 1,
        "optional": True,
        "env_var": True
    }
}


TEST_PARAMETERS_CMD_NO_FLAG = {
    "param_1": {
        "type": "int",
        "default": 1,
        "optional": True,
        "env_var": True,
        "description": "Test description",
        "cmd_var": True
    }
}


TEST_PARAMETERS_NO_CMD_NO_ENV = {
    "param_1": {
        "type": "int",
        "optional": True,
        "description": "Test description"
    }
}


TEST_PARAMETERS_WRONG_TYPE = {
    "param_1": {
        "type": "int",
        "default": "home",
        "optional": True,
        "env_var": True
    }
}

TEST_COMPONENT_CONFIG = Path(__file__).parent / \
    "test_component_config" / "test.yaml"


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

    def test_cmd_no_flag(self):
        """Tests that when a parameter is specified as a command line argument without any flag; an
        error is raised.
        """
        TEST_MODEL.update({"parameters": TEST_PARAMETERS_CMD_NO_FLAG})
        with self.assertRaises(ValueError):
            TunableComponentModel(**TEST_MODEL)

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


if __name__ == "__main__":
    unittest.main()