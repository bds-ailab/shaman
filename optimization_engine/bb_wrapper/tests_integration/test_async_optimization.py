"""
The goal of this module is to provide integration test of the little-shaman command, when using:
- Asynchronous optimization
- The FIOL as an accelerator

In order to run, this test requires:
- Slurm
- The iomodules handler module configured to work appropriately with the accelerators
- The SRO installed to testing
"""
import unittest
import os
import subprocess
from shlex import split

CURRENT_DIR = os.getcwd()
FILE_DIR = os.path.dirname(os.path.realpath(__file__))
TEST_DATA = os.path.join(FILE_DIR, "test_data")
CONFIG_ASYNC_DEFAULT = os.path.join(TEST_DATA, "config_shaman_async_default.cfg")
CONFIG_ASYNC_STEP = os.path.join(TEST_DATA, "config_shaman_async_default.cfg")
CONFIG_ASYNC_MEDIAN = os.path.join(TEST_DATA, "config_shaman_async_median.cfg")
TEST_SBATCH = os.path.join(TEST_DATA, "test_sbatch.sbatch")

#TODO: check in database if the data has been properly written

class TestAsyncOptimization(unittest.TestCase):
    """
    Unittests for testing that the optimization runs properly in an asynchronous setting.
    """
    def setUp(self):
        """
        Setup the test by writing down the little-shaman command line.
        """
        self.cmd_default = f"little-shaman --accelerator_name fiol --nbr_iteration 1 --sbatch_file "\
                   f"{TEST_SBATCH} --configuration_file {CONFIG_ASYNC_DEFAULT} --experiment_name test"
        self.cmd_step = f"little-shaman --accelerator_name fiol --nbr_iteration 1 --sbatch_file "\
                   f"{TEST_SBATCH} --configuration_file {CONFIG_ASYNC_STEP} --experiment_name test"
        self.cmd_median = f"little-shaman --accelerator_name fiol --nbr_iteration 1 --sbatch_file "\
                   f"{TEST_SBATCH} --configuration_file {CONFIG_ASYNC_MEDIAN} --experiment_name test"

    def test_run_command_default(self):
        """
        Run the little-shaman command in a subprocess.
        """
        sub_ps = subprocess.run(split(self.cmd_default),
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        output_stdout = sub_ps.stdout.decode()
        output_stderr = sub_ps.stderr.decode()
        print(output_stdout)
        print(output_stderr)

    def test_run_command_step(self):
        """
        Run the little-shaman command in a subprocess.
        """
        sub_ps = subprocess.run(split(self.cmd_step),
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        output_stdout = sub_ps.stdout.decode()
        output_stderr = sub_ps.stderr.decode()
        print(output_stdout)
        print(output_stderr)

    def test_run_command_median(self):
        """
        Run the little-shaman command in a subprocess.
        """
        sub_ps = subprocess.run(split(self.cmd_median),
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        output_stdout = sub_ps.stdout.decode()
        output_stderr = sub_ps.stderr.decode()
        print(output_stdout)
        print(output_stderr)

if __name__ == '__main__':
    unittest.main(verbosity=2)

