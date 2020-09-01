"""
UnitTesting for the Accelerator module.
"""

__copyright__ = """
Copyright (C) 2020 Bull S. A. S. - All rights reserved
Bull, Rue Jean Jaures, B.P.68, 78340, Les Clayes-sous-Bois, France
This is not Free or Open Source software.
Please contact Bull S. A. S. for details about its license.
"""

import unittest
import os
from iomodules_handler.io_modules.accelerators.accelerator import Accelerator

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
TEST_DATA = os.path.join(CURRENT_DIR, "test_data")
TEST_CONFIG = os.path.join(TEST_DATA, "test_configuration.yaml")
# Test configuration to test default parametrization
TEST_CONFIG_DEFAULT = os.path.join(TEST_DATA, "test_configuration_default.yaml")
# Test configuration with flag
TEST_CONFIG_FLAG = os.path.join(TEST_DATA, "test_configuration_flag.yaml")

# Save current environment variable into a variable
current_var_env = os.environ.copy()

parameters = {"TOTO": 10, "TITI": 11}
parameters_optional = {"TOTO": 10, "TITI": 11, "TATA": 5}
parameters_default = {"TITI": 4}
parameters_missing = {"TOTO": 3}


class TestAccelerator(unittest.TestCase):
    """Tests that the Accelerator class works properly."""

    def test_accelerator_name(self):
        """Tests that the Accelerator class intializes properly and stores correctly
        the parameters"""
        acc = Accelerator(parameters, TEST_CONFIG)
        self.assertDictEqual(acc.parameters, parameters)

    def test_initialization(self):
        """Tests that the Accelerator class initializes properly and returns
        the correct accelerator name."""
        acc = Accelerator(parameters, TEST_CONFIG)
        self.assertEqual(acc.accelerator_name, "abstract_accelerator")

    def test_wrong_parameters_format(self):
        """Tests that setting parameters that are not dict as parameters raises a type error."""
        no_dict_parameters = [1, 2, 3]
        with self.assertRaises(TypeError):
            Accelerator(no_dict_parameters, TEST_CONFIG)

    def test_get_default_parameters(self):
        """Tests that the default parameters are properly selected from the IO Module
        configuration file."""
        acc = Accelerator(parameters_default, TEST_CONFIG)
        expected_parameters = {"TITI": 4, "TOTO": 4}
        self.assertDictEqual(acc.parameters, expected_parameters)

    def test_missing_parameters(self):
        """Tests that a ValueError is raised when a parameter present in the configuration
        file is missing."""
        with self.assertRaises(ValueError):
            Accelerator(parameters_missing, TEST_CONFIG)

    def test_empty_parameters(self):
        """Tests that an empty parametrization returns all the defaults in the file"""
        acc = Accelerator(module_configuration=TEST_CONFIG_DEFAULT)
        expected_parameters = {"TITI": 2, "TOTO": 4}
        self.assertDictEqual(acc.parameters, expected_parameters)

    def test_setup_var_env_default(self):
        """Tests that the environment variables are properly setup using default values."""
        acc = Accelerator(parameters_default, TEST_CONFIG)
        acc.setup_var_env()
        expected_var_env = {"TOTO": "4"}
        expected_var_env.update(current_var_env)
        self.assertDictEqual(acc.var_env, expected_var_env)

    def test_setup_var_env(self):
        """Tests that the environment variables are properly setup using non-default values."""
        acc = Accelerator(parameters, TEST_CONFIG)
        acc.setup_var_env()
        expected_var_env = {"TOTO": "10"}
        expected_var_env.update(current_var_env)
        self.assertDictEqual(acc.var_env, expected_var_env)

    def test_setup(self):
        """Tests that the environment variables are properly setup using non-default values."""
        acc = Accelerator(parameters, TEST_CONFIG)
        acc.setup()
        expected_var_env = {"TOTO": "10"}
        expected_var_env.update(current_var_env)
        self.assertDictEqual(acc.var_env, expected_var_env)

    def test_optional_parameters(self):
        """Tests that when an optional parameter is specified, it is taken into account."""
        acc = Accelerator(parameters_optional, module_configuration=TEST_CONFIG)
        self.assertDictEqual(acc.parameters, parameters_optional)

    def test_build_cmdline(self):
        """Tests that the command line is correctly built"""
        acc = Accelerator(module_configuration=TEST_CONFIG_FLAG)
        expected_cmdline = "--dede 3 -d 3"
        self.assertEqual(acc.cmdline, expected_cmdline)


if __name__ == '__main__':
    unittest.main()
