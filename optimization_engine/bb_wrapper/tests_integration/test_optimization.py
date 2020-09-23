"""Tests the optimization process, using a bogus component. This component simply calls a
sleep command, with varying number of 

This test requires:
    - The Slurm workload manager
    - A running instance of the API
    - A running instance of the mongo database

This tests:
    - Running an optimization experiment using the run function
    - Running an optimization experiment using the command line interface
"""
import unittest


class testIntegrationAPI(unittest.TestCase):
    """
    Integration test with the API.
    """

    def test_create_experiment(self):
        """Tests that creating the experiment works as expected.
        """

    def test_fail_experiment(self):
        """Tests that calling the /fail endpoint works as expected.
        """

    def test_stop(self):
        """Tests that calling the /stop endpoint works as expected.
        """

    def test_end(self):
        """Tests that calling the /end endpoint works as expected.
        """

    def test_update(self):
        """Tests that calling the /update endpoint works as expected.
        """


class testOptimizationExperiment(unittest.TestCase):
    """
    Test that the optimization experiment runs as expected, when:
        - Launched interactively through a function call
        - Launched with a command line interface
    """

    def test_run_vanilla(self):
        """Tests that the optimization is ok when running without pruning or noise reduction.
        """

    def test_run_pruning(self):
        """Tests that the optimization is ok when running with pruning.
        """

    def test_run_noise_reduction(self):
        """Tests that the optimization is ok when running with noise reduction.
        """
