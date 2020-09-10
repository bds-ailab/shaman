"""
Tests the integration of the AccBlackBox class in the slurm environment.

This test requires:
    - The Slurm workload manager
"""

import unittest
import os
import glob
import time
from concurrent.futures import ThreadPoolExecutor

from little_shaman.acc_blackbox import AccBlackBox
# Import the Slurm manipulation tools from IOModules
# TODO: Move them in a common integration test module
from iomodules_handler.tools.server_tools import check_slurm_queue_name, check_slurm_queue_id

CURRENT_DIR = os.getcwd()
FILE_DIR = os.path.dirname(os.path.realpath(__file__))
TEST_DATA = os.path.join(FILE_DIR, "test_data")
TEST_SBATCH_DIR = os.path.join(TEST_DATA, "test_sbatch_dir")
TEST_IOMODULES_CONFIG = os.path.join(TEST_DATA, "iomodules_config.yaml")
TEST_SBATCH = os.path.join(TEST_DATA, "test_sbatch.sbatch")
TEST_SBATCH_SLEEP = os.path.join(TEST_DATA, "test_sbatch_sleep.sbatch")


class TestAccBlackBox(unittest.TestCase):
    """
    Tests the methods of AccBlackBox that are relative to the Slurm Workload manager.
    """

    def setUp(self):
        """
        Save as attribute of the testclass an object of class AccBlackBox.
        """
        self.acc_blackbox = AccBlackBox(accelerator_name='fiol',
                                        parameter_names=['SRO_CLUSTER_THRESHOLD', 'SRO_DSC_BINSIZE'],
                                        sbatch_file=TEST_SBATCH_SLEEP,
                                        sbatch_dir=TEST_SBATCH_DIR,
                                        acc_configuration_file=TEST_IOMODULES_CONFIG)

    def test_slurm_config(self):
        """
        Tests that the slurm configuration property is properly returned.
        """
        self.assertEqual(self.acc_blackbox.slurm_config, "/slurm/slurm.conf")

    def test_on_interrupt(self):
        """
        Tests that the on_interrupt method works as expected, by calling scancel on a running job.
        """
        # Setup the accelerator
        acc = self.acc_blackbox.accelerator(
            module_configuration=self.acc_blackbox.acc_configuration_file)
        # Submit the sbatch using the accelerator with default parameters
        job_id = acc.submit_sbatch(self.acc_blackbox.sbatch_file,
                                   wait=False,
                                   instrumented=self.acc_blackbox.instrumented)
        # Check that the sbatch has been properly submitted
        self.assertTrue(check_slurm_queue_id(job_id))
        # Kill the job using scancel
        self.acc_blackbox.scancel_job(job_id, self.acc_blackbox.slurm_config)
        # Check that the job is not running anymore
        self.assertFalse(check_slurm_queue_id(job_id))

    def test_parse_job_elapsed_time(self):
        """
        Tests that the parsing of the elapsed time in a slurm queue is properly computed.
        """
        # Setup the accelerator
        acc = self.acc_blackbox.accelerator(
            module_configuration=self.acc_blackbox.acc_configuration_file)
        # Submit the sbatch using the accelerator with default parameters
        job_id = acc.submit_sbatch(self.acc_blackbox.sbatch_file,
                                   wait=False,
                                   instrumented=self.acc_blackbox.instrumented)
        # Sleep to let Slurm have enough time to submit the job properly
        time.sleep(5)
        # Check that the job elapsed time is properly returned
        self.assertGreater(self.acc_blackbox.parse_job_elapsed_time(job_id,
                                                                    self.acc_blackbox.slurm_config), 
                           0)
        self.assertLess(self.acc_blackbox.parse_job_elapsed_time(job_id,
                                                                 self.acc_blackbox.slurm_config),
                        10)

    def test_compute_separate_thread(self):
        """Tests that when the compute method is ran in a separate thread, the time of the job can be
        monitored and it can be properly killed."""
        parameters = [2, 1048576]
        pool = ThreadPoolExecutor()
        future = pool.submit(self.acc_blackbox.compute, (parameters))
        while not future.done():
            while not self.acc_blackbox.acc_setup.submitted_jobids:
                time.sleep(1)
            running_job_id = self.acc_blackbox.acc_setup.submitted_jobids[0]
            # Let a few seconds elapse
            time.sleep(2)
            # Check that the job is running
            self.assertTrue(check_slurm_queue_id(running_job_id))
            # Let a few seconds elapse
            time.sleep(2)
            # Check that the elapsed time is superior to 0
            self.assertGreater(self.acc_blackbox.parse_job_elapsed_time(running_job_id,
                                                                        self.acc_blackbox.slurm_config), 
                                                                        0)
            # Scancel the job
            self.acc_blackbox.scancel_job(running_job_id, self.acc_blackbox.slurm_config)
            # Wait for 2 s
            time.sleep(2)
            # Check that the job died
            self.assertFalse(check_slurm_queue_id(running_job_id))

    def tearDown(self):
        out_file = f"{TEST_SBATCH_DIR}/test_sbatch_shaman.sbatch"
        if glob.glob(out_file):
            os.remove(out_file)
        for file in glob.glob("slurm-*.out"):
            os.remove(file)


if __name__ == '__main__':
    unittest.main(verbosity=2)