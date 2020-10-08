"""
Integration testing of SHAMan within the API.

This tests require:
    - The running API
    - The slurm workload manager
There is of course a dependance between the API code and whether or not this script runs properly.

Tests the following scenario:
- The user creates a new component
- The user launches an experiment
- The user reads the experiment results
"""
import unittest


class TestOptimization(unittest.TestCase):
    """Tests the proper integration of the optimization engine within the API."""

    def setUp(self):
        """Sets up the environment by sending a component to the API (running the install script)"""
        # Run the installation script using the component_config file

        # Check that the API properly returns the component file

    def launch_experiment(self):
        """Launch an optimization experiment."""
        # Launch an optimization experiment using SHAMan run function

    def tearDown(self):
        """Reads the results from the experiment to ensure proper running."""
        # Get the results of the experiment back by reading from the API
