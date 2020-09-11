"""
Tests that the BBWrapper class behaves as expected.
"""
import unittest

from bb_wrapper.bb_wrapper import BBWrapper

# Test config component
TEST_CONFIG = Path(__file__).parent / \
    "test_config"
COMPONENT_CONFIG = TEST_DATA / "component_config.yaml"

# Test slurms
TEST_SLURMS = Path(__file__).parent / \
    "test_slurm_outputs"

# Test sbatch
TEST_SBATCH = Path(__file__).parent / \
    "test_sbatch"


class TestBBWrapper(unittest.TestCase):
    """Tests that the BBWrapper class behaves as expected.
    """

    def test_initialization(self):
        """Tests the proper initialization of the class.
        """

    def test_copy_sbatch_time(self):
        """Tests that copying the sbatch to add a time command behaves as expected.
        """

    def test_copy_sbatch_no_time(self):
        """Tests that copying the sbatch to add a time command to a non-timed sbatch behaves as
        expected.
        """

    def test_compute(self):
        """Tests that the compute method behaves as expected.
        """

    def test_run_default(self):
        """Tests that running the default parametrization behaves as expected.
        """

    def test_parse_slurm_times(self):
        """Tests that the slurm times are properly parsed from a slurm out file.
        """

    def test_parse_slurm_times_except_no_time(self):
        """ Test the "_parse_slurm_times" method raises a ValueError if the slurm output file does
        not contains the time."""
        # self.assertRaises(ValueError,
        #                   self.acc_blackbox._parse_slurm_times,
        #                   f"{FAKE_SLURMS}/slurm-666.out")

    def test_parse_slurm_times_except_no_file(self):
        """ Test the "_parse_slurm_times" method raises a FileNotFoundError if the slurm output file
        does not exist."""
        # self.assertRaises(FileNotFoundError,
        #                   self.acc_blackbox._parse_slurm_times,
        #                   f"{FAKE_SLURMS}/slurm-00.out")

    def test_parse_milliseconds(self):
        """Tests that parsing milliseconds work as expected.
        """
        time = BBWrapper.parse_milliseconds('01m01.01s')
        self.assertEqual(time, 61.001)
        time = BBWrapper.parse_milliseconds('123m45.67s')
        self.assertEqual(time, 7425.067)

    def test_parse_job_elapsed_time(self):
        """Tests that parsing a job elapsed time through a subprocess call calling the
        squeue command works as expected.
        """

    def test_scancel_job(self):
        """Tests that scanceling a job through a subprocess call of the scancel command works as
        expected.
        """
