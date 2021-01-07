"""
Module for unit-testing of the parsing plugins.
"""

import unittest
from pathlib import Path
from bb_wrapper.tunable_component.plugins.parse_execution_time import parse_milliseconds, parse_slurm_times

TEST_SLURMS = Path(__file__).parent / "test_slurm_outputs"


class TestPlugins(unittest.TestCase):

    def test_parse_slurm_times(self):
        """Tests that the slurm times are properly parsed from a slurm out file.
        """
        time = parse_slurm_times("42", path=TEST_SLURMS)
        self.assertEqual(time, 1508.085)

    def test_parse_slurm_times_except_no_time(self):
        """ Test the "_parse_slurm_times" function raises a ValueError if the slurm output file does
        not contains the time."""
        self.assertRaises(
            ValueError,
            parse_slurm_times,
            "666",
            TEST_SLURMS
        )

    def test_parse_slurm_times_except_no_file(self):
        """ Test the "_parse_slurm_times" function raises a FileNotFoundError if the slurm output file
        does not exist."""
        self.assertRaises(
            FileNotFoundError,
            parse_slurm_times,
            "00",
            TEST_SLURMS,
        )

    def test_parse_milliseconds(self):
        """Tests that parsing milliseconds work as expected.
        """
        time = parse_milliseconds("01m01.01s")
        self.assertEqual(time, 61.001)
        time = parse_milliseconds("123m45.67s")
        self.assertEqual(time, 7425.067)


if __name__ == "__main__":
    unittest.main()
