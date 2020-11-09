# Copyright 2020 BULL SAS All rights reserved
"""
This module tests that the BBOptimizer class behaves as expected.
"""

# Disable the could be a function for unit testing
# pylint: disable=no-self-use
# Disable name too longs (necessary for clarity in testing)
# pylint: disable=invalid-name

import io
import sys
import unittest
import numpy as np

# imports for surrogate models
from sklearn.gaussian_process import GaussianProcessRegressor
from bbo.optimizer import BBOptimizer
from bbo.heuristics.surrogate_models.next_parameter_strategies import (
    expected_improvement,
)

# imports for genetic algorithms
from bbo.heuristics.genetic_algorithm.selections import (
    tournament_pick,
    probabilistic_pick,
)
from bbo.heuristics.genetic_algorithm.crossover import double_point_crossover
from bbo.heuristics.genetic_algorithm.mutations import mutate_chromosome_to_neighbor


# Use parabola as fake black-box
class Parabola:
    """
    Black box class that will be used for testing purpose
    """

    def __init__(self):
        """
        Initialization of the black-box
        """
        print("I'm the Parabola function ! Good luck finding my optimum !")

    def compute(self, array_2d):
        """
        Computes the value of the parabola at data point array_2d
        """
        return array_2d[0] ** 2 + array_2d[1] ** 2


# Create mock class that does not have a compute method for testing purpose
class AintGotNoCompute:
    """
    Black box without a compute method.
    """

    def __init__(self):
        """
        Initialization of object
        """
        print("Ain't got no compute !")

    def not_compute(self):
        """
        Not a compute method
        """
        print("This is not a compute method.")


# Create mock callbacks


def mock_callback_1(history):
    """
    Prints to screen the square root value of the fitness values and the sum of the parameters.
    """
    fitness_transform = round(np.sqrt(np.sum(history["fitness"])))
    parameters_transform = round(np.sum(history["parameters"]))
    print(f"Result: {fitness_transform} + {parameters_transform}")


def mock_callback_2(history):
    """
    Prints to screen the square value of the fitness values and the square of the sum of the parameters.
    """
    fitness_transform = round(np.sum(history["fitness"]) ** 2)
    parameters_transform = round(np.sum(history["parameters"]) ** 2)
    print(f"Result: {fitness_transform} + {parameters_transform}")


# parameter space
parameter_space = np.array(
    [np.arange(-5, 5, 1), np.arange(-6, 6, 1), np.arange(-6, 6, 1)]
).T
# maximum number of iterations
nbr_iteration = 5
# maximum elapsed time
time_out = 100
# create fake history
fake_history = {
    "fitness": np.array([10, 5, 4, 2, 15, 20]),
    "parameters": np.array([[1, 2], [2, 3], [1, 3], [4, 3], [2, 1], [1, 5]]),
    "truncated": np.array([True, True, True, True, True, True]),
}


class TestOptimizer(unittest.TestCase):
    """
    Tests that the BBOptimizer works as expected.
    """

    def setUp(self):
        """
        Creates object of the class Parabola and AintGotNoCompute to test the optimization process.
        """
        self.parabola = Parabola()
        self.no_compute = AintGotNoCompute()

    def test_no_compute_method(self):
        """
        Tests that when there is no compute method, an error is raised.
        """
        with self.assertRaises(AttributeError):
            BBOptimizer(
                black_box=self.no_compute,
                heuristic="surrogate_model",
                max_iteration=nbr_iteration,
                parameter_space=parameter_space,
            )

    def test_transform_function(self):
        """
        Tests that the transform function works properly by transforming the output of the
        compute method of the black-box function.
        """

        def perf_function(x):
            return x + 2

        bb_obj = BBOptimizer(
            black_box=self.parabola,
            heuristic="surrogate_model",
            max_iteration=nbr_iteration,
            parameter_space=parameter_space,
            perf_function=perf_function,
            regression_model=GaussianProcessRegressor,
            next_parameter_strategy=expected_improvement,
        )
        self.assertEqual(
            bb_obj.compute_result(np.array([5, 0])),
            27,
            "Use of a transformation "
            "function black-box output "
            "did not work properly.",
        )

    def test_incorrect_heuristic_name(self):
        """
        Tests that when an incorrect heuristic name is passed as argument, an error is raised.
        """
        with self.assertRaises(ValueError):
            BBOptimizer(
                black_box=self.parabola,
                heuristic="makes no sense !",
                max_iteration=nbr_iteration,
                parameter_space=parameter_space,
                next_parameter_strategy=expected_improvement,
                regression_model=GaussianProcessRegressor,
            )

    def test_incorrect_selection_name(self):
        """
        Tests that when an incorrect name for the selection method is passed as an argument,
        a ValueError is raised.
        """
        with self.assertRaises(ValueError):
            BBOptimizer(
                black_box=self.parabola,
                heuristic="surrogate_model",
                max_iteration=nbr_iteration,
                parameter_space=parameter_space,
                next_parameter_strategy=expected_improvement,
                initial_draw_method="i do not exist!",
                regression_model=GaussianProcessRegressor,
            )

    def test_missing_heuristic_argument(self):
        """
        Tests that an exception is raised when there's a missing argument for a heuristic.
        """
        with self.assertRaises(Exception):
            BBOptimizer(
                black_box=self.parabola,
                heuristic="surrogate_model",
                max_iteration=nbr_iteration,
                parameter_space=parameter_space,
                next_parameter_strategy=expected_improvement,
            )

    def test_append_parameters(self):
        """
        Tests that the parameters are correctly added to the history.
        """
        # Manually create the history of the BBOptimizer
        bb_obj = BBOptimizer(
            black_box=self.parabola,
            heuristic="surrogate_model",
            max_iteration=nbr_iteration,
            parameter_space=parameter_space,
            next_parameter_strategy=expected_improvement,
            regression_model=GaussianProcessRegressor,
        )
        bb_obj.history = fake_history
        # Test the append method
        bb_obj._append_parameters([1, 3])
        np.testing.assert_array_equal(
            bb_obj.history["parameters"],
            np.array([[1, 2], [2, 3], [1, 3], [4, 3], [2, 1], [1, 5], [1, 3]]),
        )

    def test_append_parameters_new_history(self):
        """
        Tests that the parameters are correctly added to an empty history.
        """
        # Manually create the history of the BBOptimizer
        bb_obj = BBOptimizer(
            black_box=self.parabola,
            heuristic="surrogate_model",
            max_iteration=nbr_iteration,
            parameter_space=parameter_space,
            next_parameter_strategy=expected_improvement,
            regression_model=GaussianProcessRegressor,
        )
        # Test the append method
        bb_obj._append_parameters([1, 3])
        np.testing.assert_array_equal(bb_obj.history["parameters"], np.array([1, 3]))

    def test_append_performance(self):
        """
        Tests that appending a new fitness value on the performance history works properly.
        """
        # Manually create the history of the BBOptimizer
        bb_obj = BBOptimizer(
            black_box=self.parabola,
            heuristic="surrogate_model",
            max_iteration=nbr_iteration,
            parameter_space=parameter_space,
            next_parameter_strategy=expected_improvement,
            regression_model=GaussianProcessRegressor,
        )
        bb_obj.history = fake_history
        # Tests the append method
        bb_obj._append_fitness(10)
        np.testing.assert_array_equal(
            bb_obj.history["fitness"], np.array(np.array([10, 5, 4, 2, 15, 20, 10]))
        )

    def test_append_performance_new_history(self):
        """
        Tests that appending a fitness value on an empty history works properly.
        """
        # Manually create the history of the BBOptimizer
        bb_obj = BBOptimizer(
            black_box=self.parabola,
            heuristic="surrogate_model",
            max_iteration=nbr_iteration,
            parameter_space=parameter_space,
            next_parameter_strategy=expected_improvement,
            regression_model=GaussianProcessRegressor,
        )
        # Tests the append method
        bb_obj._append_fitness(10)
        np.testing.assert_array_equal(
            bb_obj.history["fitness"], np.array(np.array([10]))
        )

    def test_stop_rule_false(self):
        """
        Tests that the stop rule is built properly when the stop criteria are met.
        """
        bb_obj = BBOptimizer(
            black_box=self.parabola,
            heuristic="surrogate_model",
            max_iteration=nbr_iteration,
            time_out=time_out,
            parameter_space=parameter_space,
            next_parameter_strategy=expected_improvement,
            regression_model=GaussianProcessRegressor,
        )
        # If the number of iterations is exceeded
        bb_obj.nbr_iteration = nbr_iteration + 1
        self.assertFalse(
            bb_obj.stop_rule,
            "Exceeded number of iteration did not stop the " "optimizing loop.",
        )

        bb_obj = BBOptimizer(
            black_box=self.parabola,
            heuristic="surrogate_model",
            max_iteration=nbr_iteration,
            time_out=time_out,
            parameter_space=parameter_space,
            next_parameter_strategy=expected_improvement,
            regression_model=GaussianProcessRegressor,
        )
        # If the time elapsed is exceeded
        bb_obj.elapsed_time = time_out + 1
        self.assertFalse(
            bb_obj.stop_rule, "Exceeded elapsed time did not stop optimizing loop."
        )

        bb_obj = BBOptimizer(
            black_box=self.parabola,
            heuristic="surrogate_model",
            max_iteration=nbr_iteration,
            time_out=time_out,
            parameter_space=parameter_space,
            next_parameter_strategy=expected_improvement,
            regression_model=GaussianProcessRegressor,
        )
        # If the heuristic stop criterion is met
        bb_obj.heuristic.stop = True
        self.assertFalse(
            bb_obj.stop_rule,
            "Internal heuristic stop did not stop the optimizing " "loop.",
        )

    def test_stop_rule_true(self):
        """
        Tests that the stop rule is built properly when the stop criteria are not met.
        """
        bb_obj = BBOptimizer(
            black_box=self.parabola,
            heuristic="surrogate_model",
            max_iteration=nbr_iteration,
            time_out=time_out,
            parameter_space=parameter_space,
            next_parameter_strategy=expected_improvement,
            regression_model=GaussianProcessRegressor,
        )
        # If the number of iterations is exceeded
        bb_obj.nbr_iteration = nbr_iteration - 1
        self.assertTrue(
            bb_obj.stop_rule,
            "Exceeded number of iteration did not stop the " "optimizing loop.",
        )

        bb_obj = BBOptimizer(
            black_box=self.parabola,
            heuristic="surrogate_model",
            max_iteration=nbr_iteration,
            time_out=time_out,
            parameter_space=parameter_space,
            next_parameter_strategy=expected_improvement,
            regression_model=GaussianProcessRegressor,
        )
        # If the time elapsed is exceeded
        bb_obj.elapsed_time = time_out - 1
        self.assertTrue(
            bb_obj.stop_rule, "Exceeded elapsed time did not stop optimizing loop."
        )

        bb_obj = BBOptimizer(
            black_box=self.parabola,
            heuristic="surrogate_model",
            max_iteration=nbr_iteration,
            time_out=time_out,
            parameter_space=parameter_space,
            next_parameter_strategy=expected_improvement,
            regression_model=GaussianProcessRegressor,
        )
        # If the heuristic stop criterion is met
        bb_obj.heuristic.stop = False
        self.assertTrue(
            bb_obj.stop_rule,
            "Internal heuristic stop did not stop the optimizing " "loop.",
        )

    def test_evaluate_fitness_single_item(self):
        """
        Tests that the fitness is properly evaluated when applied on a single numpy array.
        """
        test_parameters = np.array([2, 3])
        expected_result = np.array([13])
        bb_obj = BBOptimizer(
            black_box=self.parabola,
            heuristic="surrogate_model",
            max_iteration=nbr_iteration,
            time_out=time_out,
            parameter_space=parameter_space,
            next_parameter_strategy=expected_improvement,
            regression_model=GaussianProcessRegressor,
        )
        result = bb_obj.compute_result(test_parameters)
        np.testing.assert_array_equal(
            expected_result,
            result,
            "Fitness evaluation on a parameter "
            "single item did not work as "
            "expected.",
        )

    def test_total_iteration(self):
        """
        Tests that the total number of iterations is properly computed (and indirectly that the
        stop criterion properly stops on the number of iterations).
        """
        bb_obj = BBOptimizer(
            black_box=self.parabola,
            heuristic="surrogate_model",
            max_iteration=nbr_iteration,
            initial_sample_size=2,
            parameter_space=parameter_space,
            next_parameter_strategy=expected_improvement,
            regression_model=GaussianProcessRegressor,
        )
        bb_obj.optimize()
        self.assertEqual(
            nbr_iteration + 2,
            bb_obj.total_iteration,
            "Total number of iterations " "was not computed properly.",
        )

    def test_summarize_except(self):
        """
        Tests that the call to "summarize" raises an exception if the experiment is not yet
        launched.
        """
        bb_obj = BBOptimizer(
            black_box=self.parabola,
            heuristic="surrogate_model",
            max_iteration=nbr_iteration,
            initial_sample_size=2,
            parameter_space=parameter_space,
            next_parameter_strategy=expected_improvement,
            regression_model=GaussianProcessRegressor,
        )
        self.assertRaises(Exception, bb_obj.summarize)

    def test_summarize(self):
        """
        Tests that the call to "summarize" does not raise an error.
        """
        bb_obj = BBOptimizer(
            black_box=self.parabola,
            heuristic="surrogate_model",
            max_iteration=nbr_iteration,
            initial_sample_size=2,
            parameter_space=parameter_space,
            next_parameter_strategy=expected_improvement,
            regression_model=GaussianProcessRegressor,
        )
        bb_obj.optimize()
        bb_obj.summarize()

    def test_closest_parameter(self):
        """
        Tests that the closest parameter in a grid are properly returned when using the
        closest_parameter static method.
        """
        bb_obj = BBOptimizer(
            black_box=self.parabola,
            heuristic="surrogate_model",
            max_iteration=nbr_iteration,
            initial_sample_size=2,
            parameter_space=parameter_space,
            next_parameter_strategy=expected_improvement,
            regression_model=GaussianProcessRegressor,
        )
        expected_parameter = np.array([0, 1, 3])
        parameter = np.array([0.2, 0.8, 2.89])
        actual_parameter = bb_obj.closest_parameters(parameter, parameter_space)
        np.testing.assert_array_equal(
            expected_parameter,
            actual_parameter,
            "Constriction to grid did not work properly.",
        )

    def test_size_explored_space(self):
        """
        Tests that the computation of the size of the explored space works properly, as well as
        the percentage of static moves.
        """
        history = {
            "fitness": np.array([10, 5, 4]),
            "parameters": np.array([[1, 2, 3], [2, 3, 4], [1, 2, 3]]),
            "truncated": np.array([True, True, True, True, True, True]),
        }
        bb_obj = BBOptimizer(
            black_box=self.parabola,
            heuristic="surrogate_model",
            max_iteration=nbr_iteration,
            initial_sample_size=2,
            parameter_space=parameter_space,
            next_parameter_strategy=expected_improvement,
            regression_model=GaussianProcessRegressor,
        )
        bb_obj.history = history
        expected_static_moves = 1 / 3 * 100
        expected_explored_space = 2 / 1440 * 100
        real_explored_space, real_static_moves = bb_obj.size_explored_space
        self.assertEqual(
            expected_static_moves,
            real_static_moves,
            "Percentage of static moves " "was not computed properly.",
        )
        self.assertEqual(
            expected_explored_space,
            real_explored_space,
            "Percentage of explored " "space was not computed " "properly.",
        )

    def test_local_exploration_cost(self):
        """
        Tests that the local exploration cost is properly computed.
        """
        history = {
            "fitness": np.array([10, 5, 6, 2, 15, 20]),
            "parameters": np.array([[1, 2], [2, 3], [1, 3], [4, 3], [2, 1], [1, 5]]),
            "truncated": np.array([True, True, True, True, True, True]),
        }

        bb_obj = BBOptimizer(
            black_box=self.parabola,
            heuristic="surrogate_model",
            max_iteration=nbr_iteration,
            initial_sample_size=2,
            parameter_space=parameter_space,
            next_parameter_strategy=expected_improvement,
            regression_model=GaussianProcessRegressor,
        )
        bb_obj.history = history
        expected_number_states = 3
        expected_performance_cost = 19
        real_number_states, real_performance_cost = bb_obj.local_exploration_cost
        self.assertEqual(
            expected_number_states,
            real_number_states,
            "Number of local regressions " "was not correctly computed.",
        )
        self.assertEqual(
            expected_performance_cost,
            real_performance_cost,
            "Loss due to " "regression was not " "correctly computed.",
        )

    def test_global_exploration_cost(self):
        """
        Tests that the global exploration cost is properly computed.
        """
        history = {
            "fitness": np.array([10, 5, 6, 2, 15, 4]),
            "parameters": np.array([[1, 2], [2, 3], [1, 3], [4, 3], [2, 1], [1, 5]]),
            "truncated": np.array([True, True, True, True, True, True]),
        }

        bb_obj = BBOptimizer(
            black_box=self.parabola,
            heuristic="surrogate_model",
            max_iteration=nbr_iteration,
            initial_sample_size=2,
            parameter_space=parameter_space,
            next_parameter_strategy=expected_improvement,
            regression_model=GaussianProcessRegressor,
        )
        bb_obj.history = history
        expected_number_states = 3
        expected_performance_cost = 16
        real_number_states, real_performance_cost = bb_obj.global_exploration_cost
        self.assertEqual(
            expected_number_states,
            real_number_states,
            "Percentage of static moves " "was not computed properly.",
        )
        self.assertEqual(
            expected_performance_cost,
            real_performance_cost,
            "Percentage of explored " "space was not computed " "properly.",
        )

    def test_fitness_gain_per_iteration(self):
        """
        Tests that the fitness gain per iteration is properly computed.
        """
        history = {
            "fitness": np.array([10, 5, 6, 2, 15, 4]),
            "parameters": np.array([[1, 2], [2, 3], [1, 3], [4, 3], [2, 1], [1, 5]]),
            "truncated": np.array([True, True, True, True, True, True]),
        }
        bb_obj = BBOptimizer(
            black_box=self.parabola,
            heuristic="surrogate_model",
            max_iteration=nbr_iteration,
            initial_sample_size=2,
            parameter_space=parameter_space,
            next_parameter_strategy=expected_improvement,
            regression_model=GaussianProcessRegressor,
        )
        bb_obj.history = history
        bb_obj.launched = True
        expected_gain_per_iteration = np.array([-5, 1, -4, 13, -11])
        np.testing.assert_array_equal(
            expected_gain_per_iteration,
            bb_obj.fitness_gain_per_iteration,
            "Computation of fitness gain per iteration did not work as " "expected.",
        )

    def test_fitness_gain_per_iteration_not_launched(self):
        """
        Tests that the fitness gain per iteration is None if the experiment is not launched.
        """
        bb_obj = BBOptimizer(
            black_box=self.parabola,
            heuristic="surrogate_model",
            max_iteration=nbr_iteration,
            initial_sample_size=2,
            parameter_space=parameter_space,
            next_parameter_strategy=expected_improvement,
            regression_model=GaussianProcessRegressor,
        )
        bb_obj.launched = False
        self.assertEqual(bb_obj.fitness_gain_per_iteration, None)

    def test_reevaluation(self):
        """Tests the proper implementation of the reevaluation feature.
        This feature is tested by checking in the history that no re-evaluation has been done
        (as is the case with this particular optimizer configuration).
        With re-evaluate set to True, there are only 3 different values in the history of
        parametrizations. With re-evaluate set to False, all parameters of the history are
        different.
        """
        nbr_iteration = 5
        bb_obj = BBOptimizer(
            black_box=self.parabola,
            heuristic="genetic_algorithm",
            max_iteration=nbr_iteration,
            initial_sample_size=2,
            parameter_space=parameter_space,
            selection_method=tournament_pick,
            crossover_method=double_point_crossover,
            mutation_method=mutate_chromosome_to_neighbor,
            mutation_rate=0.6,
            reevaluate=False,
            max_retry=5,
        )
        bb_obj.optimize()
        self.assertEqual(
            np.unique(bb_obj.history["parameters"], axis=0).shape[0],
            7,
            "Some parameter values have been evaluated several times",
        )

    def test_reset(self):
        """
        Tests that the "reset" method reset the attributes.
        """
        bb_obj = BBOptimizer(
            black_box=self.parabola,
            heuristic="surrogate_model",
            max_iteration=nbr_iteration,
            initial_sample_size=2,
            parameter_space=parameter_space,
            next_parameter_strategy=expected_improvement,
            regression_model=GaussianProcessRegressor,
        )
        bb_obj.optimize()
        bb_obj.reset()
        self.assertEqual(bb_obj.nbr_iteration, 0)
        self.assertEqual(bb_obj.elapsed_time, 0)
        self.assertEqual(bb_obj.launched, False)
        self.assertDictEqual(
            bb_obj.history,
            {
                "fitness": None,
                "parameters": None,
                "initialization": None,
                "resampled": None,
                "truncated": None,
            },
        )

    def test_initialize(self):
        """Tests that the initialization step happens correctly, by appending the proper
        number of fitness and parametrization values."""
        bb_obj = BBOptimizer(
            black_box=self.parabola,
            heuristic="surrogate_model",
            max_iteration=nbr_iteration,
            initial_sample_size=2,
            parameter_space=parameter_space,
            next_parameter_strategy=expected_improvement,
            regression_model=GaussianProcessRegressor,
        )
        bb_obj._initialize(callbacks=[lambda x: x])
        self.assertTrue(len(bb_obj.history["fitness"]), 2)
        self.assertTrue(len(bb_obj.history["parameters"]), 2)

    def test_initialize_callback(self):
        """Tests that the initialization step happens correctly when using a callback function,
        which prints the square root of the sum of the fitness values and the sum of the parameters"""
        np.random.seed(10)
        # Capture the stdout to check if the print happenned correctly
        captured_output = io.StringIO()
        sys.stdout = captured_output
        bb_obj = BBOptimizer(
            black_box=self.parabola,
            heuristic="surrogate_model",
            max_iteration=nbr_iteration,
            initial_sample_size=2,
            parameter_space=parameter_space,
            next_parameter_strategy=expected_improvement,
            regression_model=GaussianProcessRegressor,
        )
        bb_obj._initialize(callbacks=[mock_callback_1])
        # Redirect the stdout to not mess with the system
        sys.stdout = sys.__stdout__
        expected = "Result: 3 + 5\nResult: 4 + 6\n"
        self.assertEqual(expected, captured_output.getvalue())

    def test_initialize_callbacks(self):
        """
        Tests that the initialization step happens correctly when using two callback functions,
        which prints the square root of the sum of the fitness values and the sum of the parameters
        and prints the square of the sum of the fitness values and the square of the sum of the parameters
        """
        np.random.seed(10)
        # Capture the stdout to check if the print happenned correctly
        captured_output = io.StringIO()
        sys.stdout = captured_output
        bb_obj = BBOptimizer(
            black_box=self.parabola,
            heuristic="surrogate_model",
            max_iteration=nbr_iteration,
            initial_sample_size=2,
            parameter_space=parameter_space,
            next_parameter_strategy=expected_improvement,
            regression_model=GaussianProcessRegressor,
        )
        bb_obj._initialize(callbacks=[mock_callback_1, mock_callback_2])
        # Redirect the stdout to not mess with the system
        sys.stdout = sys.__stdout__
        expected = "Result: 3 + 5\nResult: 100 + 25\nResult: 4 + 6\nResult: 400 + 36\n"
        self.assertEqual(expected, captured_output.getvalue())

    def test_select_parameters(self):
        """Test the function _select_next_parameters when there is no retry."""
        np.random.seed(10)
        bb_obj = BBOptimizer(
            black_box=self.parabola,
            heuristic="surrogate_model",
            max_iteration=1,
            initial_sample_size=2,
            parameter_space=parameter_space,
            next_parameter_strategy=expected_improvement,
            regression_model=GaussianProcessRegressor,
        )
        bb_obj._initialize()
        parameter = bb_obj._select_next_parameters()
        np.testing.assert_array_equal(parameter, np.array([-5, 2, -6]))

    def test_select_parameters_retry_false(self):
        """Test the function _select_next_parameters when there is a retry and the parameter is not in the grid"""
        np.random.seed(10)
        bb_obj = BBOptimizer(
            black_box=self.parabola,
            heuristic="surrogate_model",
            max_iteration=1,
            initial_sample_size=2,
            parameter_space=parameter_space,
            next_parameter_strategy=expected_improvement,
            regression_model=GaussianProcessRegressor,
            reevaluate=False,
        )
        bb_obj._initialize()
        parameter = bb_obj._select_next_parameters()
        np.testing.assert_array_equal(parameter, np.array([-5, 2, -6]))

    def test_optimization_step(self):
        """Tests that the optimization step runs properly when using the default callback.
        It checks that the parameter and the corresponding performance measure is properly added to
        the history.
        """
        np.random.seed(10)
        bb_obj = BBOptimizer(
            black_box=self.parabola,
            heuristic="surrogate_model",
            max_iteration=1,
            initial_sample_size=2,
            parameter_space=parameter_space,
            next_parameter_strategy=expected_improvement,
            regression_model=GaussianProcessRegressor,
            reevaluate=False,
        )
        test_parameter = np.array([10, 10, 10])
        bb_obj._optimization_step(test_parameter)
        np.testing.assert_array_equal(bb_obj.history["parameters"][-1], test_parameter)
        self.assertEqual(bb_obj.history["fitness"][-1], 200)

    def test_optimization_callback(self):
        """Tests that the optimization step runs properly when using a custom callback.
        It checks that there is the proper output in the stdout.
        """
        np.random.seed(10)
        captured_output = io.StringIO()
        sys.stdout = captured_output
        bb_obj = BBOptimizer(
            black_box=self.parabola,
            heuristic="surrogate_model",
            max_iteration=1,
            initial_sample_size=2,
            parameter_space=parameter_space,
            next_parameter_strategy=expected_improvement,
            regression_model=GaussianProcessRegressor,
        )
        bb_obj.optimize(callbacks=[lambda x: print(x["fitness"][0])])
        # Redirect the stdout to not mess with the system
        sys.stdout = sys.__stdout__
        expected = "10.0\n10.0\n10.0\n"
        self.assertEqual(expected, captured_output.getvalue())

    def test_get_best_performance(self):
        """Tests that the best performance is properly returned when using the method
        _get_best_performance"""
        bb_obj = BBOptimizer(
            black_box=self.parabola,
            heuristic="surrogate_model",
            max_iteration=nbr_iteration,
            initial_sample_size=2,
            parameter_space=parameter_space,
            next_parameter_strategy=expected_improvement,
            regression_model=GaussianProcessRegressor,
        )
        bb_obj.history["fitness"] = np.array([2, 1, 3])
        bb_obj.history["parameters"] = np.array(
            [np.array([1, 2]), np.array([3, 4]), np.array([5, 6])]
        )
        expected_perf = 1
        expected_parameters = np.array([3, 4])
        best_param, best_fitness = bb_obj._get_best_performance()
        np.testing.assert_array_equal(best_param, expected_parameters)
        self.assertEqual(best_fitness, 1)

    def test_optimizer_resampling_no_exist(self):
        """Tests that an error is raised when the asked for resampling policy does
        not exist.
        """
        with self.assertRaises(ValueError):
            bb_obj = BBOptimizer(
                black_box=self.parabola,
                heuristic="surrogate_model",
                max_iteration=nbr_iteration,
                initial_sample_size=2,
                parameter_space=parameter_space,
                next_parameter_strategy=expected_improvement,
                regression_model=GaussianProcessRegressor,
                resampling_policy="i do not exist",
            )

    def test_optimizer_simple_resampling_resample(self):
        """Tests that the _select_next_parameters_method works as expected
        when using simple resampling strategy and the parameters should be resampled"""
        bb_obj = BBOptimizer(
            black_box=self.parabola,
            heuristic="surrogate_model",
            max_iteration=nbr_iteration,
            initial_sample_size=2,
            parameter_space=parameter_space,
            next_parameter_strategy=expected_improvement,
            regression_model=GaussianProcessRegressor,
            resampling_policy="simple_resampling",
            nbr_resamples=3,
        )
        bb_obj.history = {
            "fitness": np.array([10, 5, 4, 2, 15, 20]),
            "parameters": np.array(
                [[1, 2, 3], [2, 3, 3], [1, 3, 3], [1, 5, 3], [1, 1, 3], [1, 5, 3]]
            ),
            "truncated": np.array([True, True, True, True, True, True]),
            "resampled": np.array([True, True, True, True, True, True]),
            "initialization": np.array([True, True, True, True, True, True]),
        }
        parameter = bb_obj._select_next_parameters()
        np.testing.assert_array_equal(parameter, [1, 5, 3])

    def test_optimizer_simple_resampling_noresample(self):
        """Tests that the _select_next_parameters_method works as expected
        when using simple resampling strategy and the parameters should not be resampled"""
        np.random.seed(1)
        bb_obj = BBOptimizer(
            black_box=self.parabola,
            heuristic="surrogate_model",
            max_iteration=nbr_iteration,
            initial_sample_size=2,
            parameter_space=parameter_space,
            next_parameter_strategy=expected_improvement,
            regression_model=GaussianProcessRegressor,
            resampling_policy="simple_resampling",
            nbr_resamples=2,
        )
        bb_obj.history = {
            "fitness": np.array([10, 5, 4, 2, 15, 20]),
            "parameters": np.array(
                [[1, 2, 3], [2, 3, 3], [1, 3, 3], [1, 5, 3], [1, 1, 3], [1, 5, 3]]
            ),
            "truncated": np.array([True, True, True, True, True, True]),
            "resampled": np.array([True, True, True, True, True, True]),
            "initialization": np.array([True, True, True, True, True, True]),
        }
        parameter = bb_obj._select_next_parameters()
        np.testing.assert_array_equal(parameter, [1, 3, 2])

    def test_optimizer_process_simple_resampling(self):
        """Tests that the .optimize() method works correctly when using simple resampling"""
        np.random.seed(5)
        bb_obj = BBOptimizer(
            black_box=self.parabola,
            heuristic="surrogate_model",
            max_iteration=nbr_iteration,
            initial_sample_size=2,
            parameter_space=parameter_space,
            next_parameter_strategy=expected_improvement,
            regression_model=GaussianProcessRegressor,
            resampling_policy="simple_resampling",
            nbr_resamples=2,
        )
        bb_obj.optimize()
        np.testing.assert_array_equal(
            bb_obj.history["fitness"], np.array([16.0, 61.0, 61.0, 16.0, 9.0, 9.0, 0.0])
        )

    def test_fitness_aggregation_std(self):
        """Tests that the fitness aggregation is performed properly when using the std
        as the estimator for the fitness aggregation.
        """
        np.random.seed(5)
        bb_obj = BBOptimizer(
            black_box=self.parabola,
            heuristic="surrogate_model",
            max_iteration=nbr_iteration,
            initial_sample_size=2,
            parameter_space=parameter_space,
            next_parameter_strategy=expected_improvement,
            regression_model=GaussianProcessRegressor,
            resampling_policy="simple_resampling",
            nbr_resamples=2,
            fitness_aggregation="simple_fitness_aggregation",
            estimator=np.std,
        )
        bb_obj.history = {
            "fitness": np.array([10, 5, 4, 2, 15, 20]),
            "parameters": np.array(
                [[1, 2, 3], [2, 3, 3], [1, 3, 3], [1, 5, 3], [1, 1, 3], [1, 5, 3]]
            ),
            "truncated": np.array([True, True, True, True, True, True]),
            "resampled": np.array([True, True, True, True, True, True]),
            "initialization": np.array([True, True, True, True, True, True]),
        }
        aggregated_history = bb_obj.fitness_aggregation.transform(bb_obj.history)
        np.testing.assert_array_equal(
            aggregated_history["fitness"], np.array([0.0, 0.0, 0.0, 9.0, 0.0])
        )
        np.testing.assert_array_equal(
            aggregated_history["parameters"],
            np.array([[1, 2, 3], [2, 3, 3], [1, 3, 3], [1, 5, 3], [1, 1, 3]]),
        )

    def test_fitness_aggregation_optimization_process(self):
        """Tests that the optimization process happens properly when using a fitness aggregation
        component.
        """
        np.random.seed(5)
        bb_obj = BBOptimizer(
            black_box=self.parabola,
            heuristic="surrogate_model",
            max_iteration=nbr_iteration,
            initial_sample_size=2,
            parameter_space=parameter_space,
            next_parameter_strategy=expected_improvement,
            regression_model=GaussianProcessRegressor,
            resampling_policy="simple_resampling",
            nbr_resamples=5,
            fitness_aggregation="simple_fitness_aggregation",
            estimator=np.median,
        )
        bb_obj.optimize()
        np.testing.assert_array_equal(
            bb_obj.history["fitness"],
            np.array([16.0, 61.0, 61.0, 61.0, 61.0, 61.0, 16.0]),
        )

    def test_measured_noise_property(self):
        """
        Tests that the noise is properly computed by the optimizer.
        """

    def test_averaged_times_property(self):
        """
        Tests that the noise is properly averaged over each parametrization by the optimizer.
        """

    def test_nbr_resampled(self):
        """
        Tests that the number of resampling is properly computed over each parametrization.
        """


if __name__ == "__main__":
    unittest.main()
