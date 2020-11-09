# Copyright 2020 BULL SAS All rights reserved
"""
The goal of this module is to test that when performing the optimization asynchronously (i.e. by 
giving the optimizer a cost value that must not be exceeded), the optimizer behaves as expected.
"""
import unittest
import time
import io
import sys
import numpy as np

from sklearn.gaussian_process import GaussianProcessRegressor
from bbo.optimizer import BBOptimizer
from bbo.heuristics.surrogate_models.next_parameter_strategies import (
    expected_improvement,
)

# Test parameters
# parameter space
parameter_space = np.array(
    [np.arange(-5, 5, 1), np.arange(-6, 6, 1), np.arange(-6, 6, 1)]
).T
# maximum number of iterations
nbr_iteration = 5

# Test classes


class BlackBoxNoStopCompute:
    """
    Test class that does not have any on_interrupt method to test that proper errors are raised.
    """

    def __init__(self):
        print("Ain't got no on_interrupt !")

    def compute(self, parameter):
        print("I'm computing !")


class BlackBoxNoStop:
    """
    Test class whose computation method is fast enough to not be stopped.
    """

    def __init__(self):
        """Initializes a test """

    def compute(self, parameter):
        """Performs a sleep of length 2"""
        time.sleep(1)
        return 5


class BlackBoxStop:
    """
    Test class whose:
    - Method stop computes the time spent by the computation
    - Method computes consist in a sleep
    """

    def __init__(self):
        """Initializes a test """

    def compute(self, parameter):
        """Performs a sleep of length 2"""
        time.sleep(4)
        return 5


class BlackBoxStopCompute:
    """
    Test black-box that possesses a stop compute method, which prints
    'stopping'.
    """

    def compute(self, parameter):
        """Performs a sleep of length 2"""
        time.sleep(4)
        return 5

    def on_interrupt(self):
        """
        Print the words 'stopping' when called.
        """
        print("stopping")


class BlackBoxCostFunction:
    """Test class for cost function"""

    def compute(self, parameter):
        """Performs a sleep of length 2"""
        time.sleep(3)
        return 5

    def cost_function(self):
        """Always evaluate the cost at 0.5"""
        return 2


class BlackBoxRandomTime:
    """
    Test black box whose compute time follows a random law.
    """

    def compute(self, parameter):
        """
        Performs a sleep following a random law.
        """
        random_time = np.round(np.abs(np.random.normal(size=1, loc=3, scale=0.5)))[0]
        time.sleep(random_time)
        return 5


class TestAsyncOptimizer(unittest.TestCase):
    """Class to test that the optimizer works properly when used asynchronously.
    """

    def test_async_optimization_step_no_stop(self):
        """
        Tests that the async optimization step works properly when the process
        takes too long.
        """
        black_box = BlackBoxNoStop()
        bb_obj = BBOptimizer(
            black_box=black_box,
            heuristic="surrogate_model",
            max_iteration=nbr_iteration,
            initial_sample_size=2,
            parameter_space=parameter_space,
            regression_model=GaussianProcessRegressor,
            next_parameter_strategy=expected_improvement,
            async_optim=True,
            max_step_cost=3,
        )
        bb_obj._initialize()
        bb_obj._async_optimization_step(np.array([3, 2, 1]))
        self.assertFalse(bb_obj.history["truncated"][-1])

    def test_async_optimization_step_stop(self):
        """
        Tests that the async optimization step behaves as expected when there is no
        need to kill the process.
        """
        black_box = BlackBoxStop()
        bb_obj = BBOptimizer(
            black_box=black_box,
            heuristic="surrogate_model",
            max_iteration=nbr_iteration,
            initial_sample_size=2,
            parameter_space=parameter_space,
            regression_model=GaussianProcessRegressor,
            next_parameter_strategy=expected_improvement,
            async_optim=True,
            max_step_cost=3,
        )
        bb_obj._initialize()
        bb_obj._async_optimization_step(np.array([3, 2, 1]))
        self.assertTrue(bb_obj.history["truncated"][-1])

    def test_async_optimization(self):
        """
        Tests that asynchronous optimization happens properly when using a black-box whose
        execution time is a random law.
        """
        black_box = BlackBoxRandomTime()
        bb_obj = BBOptimizer(
            black_box=black_box,
            heuristic="surrogate_model",
            max_iteration=nbr_iteration,
            initial_sample_size=2,
            parameter_space=parameter_space,
            regression_model=GaussianProcessRegressor,
            next_parameter_strategy=expected_improvement,
            async_optim=True,
            max_step_cost=3,
        )
        bb_obj.optimize()

    def test_async_optimization_stopping(self):
        """
        Tests that asynchronous optimization happens properly when using a black-box whose
        execution time is a random law.
        """
        black_box = BlackBoxStopCompute()
        bb_obj = BBOptimizer(
            black_box=black_box,
            heuristic="surrogate_model",
            max_iteration=3,
            initial_sample_size=2,
            parameter_space=parameter_space,
            regression_model=GaussianProcessRegressor,
            next_parameter_strategy=expected_improvement,
            async_optim=True,
            max_step_cost=1,
        )
        captured_output = io.StringIO()
        sys.stdout = captured_output
        bb_obj.optimize()
        # Redirect the stdout to not mess with the system
        sys.stdout = sys.__stdout__
        self.assertEqual(captured_output.getvalue(), "stopping\nstopping\nstopping\n")

    def test_custom_cost_function(self):
        """Tests that having a custom cost function behaves as expected.
        """
        black_box = BlackBoxCostFunction()
        bb_obj = BBOptimizer(
            black_box=black_box,
            heuristic="surrogate_model",
            max_iteration=3,
            initial_sample_size=2,
            parameter_space=parameter_space,
            regression_model=GaussianProcessRegressor,
            next_parameter_strategy=expected_improvement,
            async_optim=True,
            max_step_cost=1,
        )
        bb_obj.optimize()
        self.assertTrue(sum(bb_obj.history["truncated"][-3:]) == 3)

    def test_custom_fun_stop_function(self):
        """
        Tests that using a function as max_step_cost strategy works as expected.
        """
        black_box = BlackBoxRandomTime()
        bb_obj = BBOptimizer(
            black_box=black_box,
            heuristic="surrogate_model",
            max_iteration=nbr_iteration,
            initial_sample_size=2,
            parameter_space=parameter_space,
            regression_model=GaussianProcessRegressor,
            next_parameter_strategy=expected_improvement,
            async_optim=True,
            max_step_cost=np.mean,
        )
        bb_obj.optimize()
        self.assertEqual(
            bb_obj.max_step_cost(bb_obj.history["fitness"]),
            np.mean(bb_obj.history["fitness"]),
        )


if __name__ == "__main__":
    unittest.main()
