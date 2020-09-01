"""
UnitTesting for the SROAccelerator module.
"""

__copyright__ = """
Copyright (C) 2020 Bull S. A. S. - All rights reserved
Bull, Rue Jean Jaures, B.P.68, 78340, Les Clayes-sous-Bois, France
This is not Free or Open Source software.
Please contact Bull S. A. S. for details about its license.
"""

import unittest
import os
from iomodules_handler.io_modules.accelerators.sro import SROAccelerator

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
TEST_DATA = os.path.join(CURRENT_DIR, "test_data")
TEST_CONFIG = os.path.join(TEST_DATA, "test_sro_configuration.yaml")

# Save current environment variable into a variable
current_var_env = os.environ.copy()
parameters = {"SRO_CLUSTER_THRESHOLD": "10"}


class TestSROAccelerator(unittest.TestCase):
    """Tests that the SROAccelerator class works properly."""

    def setUp(self):
        """Initialize the required variables."""
        self.acc = SROAccelerator(parameters, TEST_CONFIG)

    def test_init_default(self):
        """Tests that the SROAccelerator class initializes properly and returns
        the correct accelerator name with default value at initialization."""
        acc = SROAccelerator(module_configuration=TEST_CONFIG)
        self.assertEqual(acc.accelerator_name, "fiol_accelerator")

    def test_accelerator_name(self):
        """Tests that the SROAccelerator class initializes properly and returns
        the correct accelerator name."""
        self.assertEqual(self.acc.accelerator_name, "fiol_accelerator")

    def test_header(self):
        """Tests that the header is the correct header."""
        self.assertEqual(self.acc.header, "clush -w $(hostname) -l root 'sync ; "
                                          "echo 3 > /proc/sys/vm/drop_caches'")


if __name__ == '__main__':
    unittest.main()
