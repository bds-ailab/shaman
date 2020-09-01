"""Integration tests that the SBBSlurmAccelerator class behaves as expected.
They require:
    - RHEL 7
    - Slurm
    - A flash accelerator library properly setup
"""
import os
import unittest

from iomodules_handler.io_modules import SBBSlurmAccelerator
from iomodules_handler.tools.server_tools import check_slurm_queue_id

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
WORKING_DIR = os.getcwd()
TEST_DATA_INTEGRATION = os.path.join(CURRENT_DIR, "test_data")
TEST_CONFIGURATION = os.path.join(TEST_DATA_INTEGRATION, "iomodules_config.yaml")


class IntTestSBBSlurmAccelerator(unittest.TestCase):
    """Tests that the SBBSlurmAccelerator class works properly."""

    def test_class_initialization_default(self):
        """Tests that the class initializes properly using default parameters."""
        acc = SBBSlurmAccelerator(module_configuration=TEST_CONFIGURATION)
        acc.setup()
        expected_header = "#SBB flavor=small targets=/fs1/roberts"
        self.assertEqual(expected_header, acc.header)

    def test_class_initialization_parameters(self):
        """Tests that the class initializes properly when giving a parameter."""
        parameters = {"WORKERS": 10}
        acc = SBBSlurmAccelerator(parameters=parameters, module_configuration=TEST_CONFIGURATION)
        acc.setup()
        expected_header = "#SBB workers=10 flavor=small targets=/fs1/roberts"
        self.assertEqual(expected_header, acc.header)

    def test_submit_sbatch(self):
        """Tests that sbatch submission works properly with the default parameters."""
        acc = SBBSlurmAccelerator(module_configuration=TEST_CONFIGURATION)
        acc.setup()
        jobid = acc.submit_sbatch(f"{os.path.join(TEST_DATA_INTEGRATION, 'sleep_sbatch.sbatch')}", wait=False)
        self.assertTrue(check_slurm_queue_id(jobid))


if __name__ == '__main__':
    unittest.main()
