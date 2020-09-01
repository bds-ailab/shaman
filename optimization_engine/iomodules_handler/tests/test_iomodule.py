"""
Unit testing for the IOModule.
"""

__copyright__ = """
Copyright (C) 2020 Bull S. A. S. - All rights reserved
Bull, Rue Jean Jaures, B.P.68, 78340, Les Clayes-sous-Bois, France
This is not Free or Open Source software.
Please contact Bull S. A. S. for details about its license.
"""

import unittest
import os
from unittest.mock import patch
from subprocess import CompletedProcess
from iomodules_handler.io_modules.iomodule import IOModule

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
TEST_DATA = os.path.join(CURRENT_DIR, "test_data")


class TestIOModule(unittest.TestCase):
    """Tests that the IOModule class works properly."""

    def test_class_initialization(self):
        """Checks the proper initialization of the IOModule class."""
        IOModule(f"{TEST_DATA}/test_configuration.yaml")

    def test_configuration_not_found(self):
        """Check that a file not found error is raised when the configuration module can't be found.
        """
        with self.assertRaises(FileNotFoundError):
            IOModule("/file/which/does/not/exist")

    def test_cmd_line(self):
        """Tests that the command line is correctly built, given the different
        possible configuration."""
        io_module = IOModule(f"{TEST_DATA}/test_configuration.yaml")
        # Command line without wait option
        cmd_line_no_wait = io_module._build_cmd_line(f"{TEST_DATA}/test_sbatch.sbatch",
                                                     wait=False,
                                                     instrumented=False)
        expected_cmd_line_no_wait = f"sbatch {TEST_DATA}/test_sbatch.sbatch"
        self.assertEqual(cmd_line_no_wait, expected_cmd_line_no_wait,
                         "Problem with building command line building without wait mode.")
        # Command line with wait option
        cmd_line_wait = io_module._build_cmd_line(f"{TEST_DATA}/test_sbatch.sbatch",
                                                  wait=True,
                                                  instrumented=False)
        expected_cmd_line_wait = f"sbatch --wait {TEST_DATA}/test_sbatch.sbatch"
        self.assertEqual(cmd_line_wait, expected_cmd_line_wait,
                         "Problem with building command line building with wait mode activated.")
        # Command line with instrumented option
        cmd_line_instrumented = io_module._build_cmd_line(f"{TEST_DATA}/test_sbatch.sbatch",
                                                          wait=False,
                                                          instrumented=True)
        expected_cmd_line_instrumented = f"sbatch --ioinstrumentation=yes " \
                                         f"{TEST_DATA}/test_sbatch.sbatch"
        self.assertEqual(cmd_line_instrumented, expected_cmd_line_instrumented,
                         "Problem with building command line with ioinstrumentation activated.")
        # Command line with plugin option
        io_module.plugin = "my_plugin=yes"
        cmd_line_with_plugin = io_module._build_cmd_line(f"{TEST_DATA}/test_sbatch.sbatch",
                                                          wait=False,
                                                          instrumented=True)
        expected_cmd_line_with_plugin = f"sbatch --ioinstrumentation=yes " \
                                         f"--my_plugin=yes " \
                                         f"{TEST_DATA}/test_sbatch.sbatch"
        self.assertEqual(cmd_line_with_plugin, expected_cmd_line_with_plugin,
                         "Problem with building command line with ioinstrumentation activated.")

    def test_edit_sbatch(self):
        """Tests that editing the sbatch by adding a header works properly."""
        io_module = IOModule(f"{TEST_DATA}/test_configuration.yaml")
        # Artifically add header to the io_module object
        io_module.header = "this is a test!"
        # Create new sbatch
        new_sbatch = io_module.add_header_sbatch(f"{TEST_DATA}/test_sbatch.sbatch")
        # Checks that the header has been added
        with open(new_sbatch, "r") as f:
            lines = [line.strip() for line in f.readlines()]
            self.assertTrue(io_module.header in lines)
        # Close the file and remove the new sbatch
        f.close()
        os.remove(new_sbatch)

    @patch('subprocess.run')
    def test_submit_sbatch_jobid(self, mocked_subproc):
        """Tests that "submit_sbatch" returns the proper jobid for this use cases."""
        io_module = IOModule(f"{TEST_DATA}/test_configuration.yaml")
        mocked_subproc.return_value = CompletedProcess("args",
                                                       returncode=0,
                                                       stdout=b"Submitted batch job 55296",
                                                       stderr=b"")
        jobid = io_module.submit_sbatch("my_sbatch")
        self.assertEqual(jobid, 55296)

    @patch('subprocess.run')
    def test_submit_sbatch_jobid_header(self, mocked_subproc):
        """Tests that "submit_sbatch" returns the proper jobid with a header in the file."""
        io_module = IOModule(f"{TEST_DATA}/test_configuration.yaml")
        io_module.header = "ld_preload=ld_preload"
        mocked_subproc.return_value = CompletedProcess("args",
                                                       returncode=0,
                                                       stdout=b"Submitted batch job 55296",
                                                       stderr=b"")
        jobid = io_module.submit_sbatch(f"{TEST_DATA}/test_sbatch.sbatch")
        self.assertEqual(jobid, 55296)
        os.remove(f"{TEST_DATA}/test_sbatch_header.sbatch")

    @patch('subprocess.run')
    def test_submit_sbatch_verbose(self, mocked_subproc):
        """Tests that "submit_sbatch" returns the proper stderr and stdout for this use cases."""
        io_module = IOModule(f"{TEST_DATA}/test_configuration.yaml")
        mocked_subproc.return_value = CompletedProcess("args",
                                                       returncode=0,
                                                       stdout=b"Submitted batch job 55296",
                                                       stderr=b"No error")
        stderr, sdtout = io_module.submit_sbatch("my_sbatch", verbose=True)
        self.assertEqual(sdtout, "Submitted batch job 55296")
        self.assertEqual(stderr, "No error")

    @patch('subprocess.run')
    def test_submit_sbatch_except(self, mocked_subproc):
        """Tests that "submit_sbatch" raises the proper exception for this use cases."""
        io_module = IOModule(f"{TEST_DATA}/test_configuration.yaml")
        mocked_subproc.return_value = CompletedProcess("args",
                                                       returncode=1,
                                                       stdout=b"Submitted batch job 55296",
                                                       stderr=b"No error")
        self.assertRaises(Exception, io_module.submit_sbatch, "my_sbatch")


if __name__ == '__main__':
    unittest.main()
