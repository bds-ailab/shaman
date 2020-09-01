"""
UnitTesting for the SBBSlurmAccelerator module.
"""

__copyright__ = """
Copyright (C) 2020 Bull S. A. S. - All rights reserved
Bull, Rue Jean Jaures, B.P.68, 78340, Les Clayes-sous-Bois, France
This is not Free or Open Source software.
Please contact Bull S. A. S. for details about its license.
"""

import unittest
import os
from iomodules_handler.io_modules.accelerators.sbb_slurm import SBBSlurmAccelerator

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
TEST_DATA = os.path.join(CURRENT_DIR, "test_data")
TEST_CONFIG = os.path.join(TEST_DATA, "test_sbb_slurm_configuration.yaml")

# Save current environment variable into a variable
current_var_env = os.environ.copy()
parameters = {"TOTO": 10, "TITI": 11}


class TestSBBSlurmAccelerator(unittest.TestCase):
    """Tests that the SBBSlurmAccelerator class works properly."""

    def setUp(self):
        """Initialize the required variables."""
        self.acc = SBBSlurmAccelerator(parameters, TEST_CONFIG)

    def test_accelerator_name(self):
        """Tests that the SBBSlurmAccelerator class initializes properly and returns
        the correct accelerator name."""
        self.assertEqual(self.acc.accelerator_name, "sbb_slurm_accelerator")

    def test_build_header(self):
        """Tests that the "build_header" methods returns the correct haeder."""
        self.assertEqual(self.acc.header, "#SBB titi=11")

    def test_setup(self):
        """Tests that the environment variables are properly setup using non-default values."""
        self.acc.setup()
        expected_var_env = {"TOTO": "10"}
        expected_var_env.update(current_var_env)
        self.assertDictEqual(self.acc.var_env, expected_var_env)


if __name__ == '__main__':
    unittest.main()
