"""
Tests the integration of the BBWrapper class in the slurm environment.

This test requires:
    - The Slurm workload manager
"""

import unittest
import os
import glob
import time
from shlex import split
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from bb_wrapper.bb_wrapper import BBWrapper


TEST_SBATCH = Path(__file__).parent / "test_sbatch" / "test_sbatch.sbatch"
TEST_SBATCH_SLEEP = Path(__file__).parent / "test_sbatch" / "test_sbatch_sleep.sbatch"
TEST_CONFIG = Path(__file__).parent / "test_config" / "component_config.yaml"


# Helper functions for testing
def string_in_output(command, string):
    """This function checks if a string is located in the output of a bash command.
    Args:
        command (str): The command to run.
        string (str): The string to look for.
    Returns:
        A boolean which indicates if the string is located in the output of the bash command.
    """
    cmd = split(command)
    sub_ps = subprocess.run(cmd, stdout=subprocess.PIPE, shell=False)
    ps_stdout = sub_ps.stdout.decode()
    return string in ps_stdout and sub_ps.returncode == 0


def check_slurm_queue_name(job_name):
    """Returns true if the job called job_name is in the slurm queue.
    Note that the maximum length for the squeue slurm name is set to 8
    and this function truncates the job_name if it exceeds this number of
    characters.
    Args:
        job_name (str): The name of the job.
    Returns:
        A boolean indicating whether or not the slurm job is running.
    """
    return string_in_output("squeue", job_name[:8])


def check_slurm_queue_id(job_id):
    """Returns true if the job whose id is job_id is in the slurm queue.
    Args:
        job_id (int): The ID of the job.
    Returns:
        A boolean indicating whether or not the slurm job is running.
    """
    try:
        return string_in_output("squeue", str(int(job_id)))
    except TypeError:
        raise TypeError("Job id must be an integer.")


class TestBBWrapper(unittest.TestCase):
    """
    Tests the methods of AccBlackBox that are relative to the Slurm Workload manager.
    """

    def setUp(self):
        """
        Save as attribute of the testclass an object of class AccBlackBox.
        """
        self.bb_wrapper = BBWrapper(
            component_name="component_1",
            parameter_names=["param_1", "param_2"],
            sbatch_file=TEST_SBATCH,
            component_configuration_file=TEST_CONFIG,
        )

    def test_on_interrupt(self):
        """
        Tests that the on_interrupt method works as expected, by calling scancel on a running job.
        """
        # Setup the component
        self.bb_wrapper.setup_component(parameters={})
        # Submit the sbatch using the accelerator with default parameters
        job_id = self.bb_wrapper.component.submit_sbatch(
            self.bb_wrapper.sbatch_file, wait=False
        )
        # Check that the sbatch has been properly submitted
        self.assertTrue(check_slurm_queue_id(job_id))
        # Kill the job using scancel
        self.bb_wrapper.scancel_job(job_id)
        # Check that the job is not running anymore
        self.assertFalse(check_slurm_queue_id(job_id))

    def test_parse_job_elapsed_time(self):
        """
        Tests that the parsing of the elapsed time in a slurm queue is properly computed.
        """
        # Setup the component
        self.bb_wrapper.setup_component(parameters={})
        # Submit the sbatch using the accelerator with default parameters
        job_id = self.bb_wrapper.component.submit_sbatch(
            self.bb_wrapper.sbatch_file, wait=False
        )
        # Sleep to let Slurm have enough time to submit the job properly
        time.sleep(5)
        # Check that the job elapsed time is properly returned
        self.assertGreater(self.bb_wrapper.parse_job_elapsed_time(job_id), 0)
        self.assertLess(self.bb_wrapper.parse_job_elapsed_time(job_id), 10)

    def test_compute_separate_thread(self):
        """Tests that when the compute method is ran in a separate thread, the time of the job can be
        monitored and it can be properly killed."""
        parameters = [2, 1048576]
        pool = ThreadPoolExecutor()
        future = pool.submit(self.bb_wrapper.compute, (parameters))
        time.sleep(5)
        while not future.done():
            while not self.bb_wrapper.component.submitted_jobids:
                time.sleep(1)
            running_job_id = self.bb_wrapper.component.submitted_jobids[0]
            # Let a few seconds elapse
            time.sleep(2)
            # Check that the job is running
            self.assertTrue(check_slurm_queue_id(running_job_id))
            # Let a few seconds elapse
            time.sleep(2)
            # Check that the elapsed time is superior to 0
            self.assertGreater(
                self.bb_wrapper.parse_job_elapsed_time(running_job_id), 0
            )
            # Scancel the job
            self.bb_wrapper.scancel_job(running_job_id)
            # Wait for 5 s
            time.sleep(5)
            # Check that the job died
            self.assertFalse(check_slurm_queue_id(running_job_id))

    def tearDown(self):
        out_file = Path.cwd() / "test_sbatch_shaman.sbatch"
        out_file.unlink()
        for file_ in Path.cwd().glob("slurm-*.out"):
            file_.unlink()


if __name__ == "__main__":
    unittest.main(verbosity=2)
