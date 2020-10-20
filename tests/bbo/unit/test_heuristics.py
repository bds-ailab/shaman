"""
Tests each heuristic possible heuristic.

WARNING:
If you want to add a new heuristic, please use the following format when writing out
unittests:
    - Create a test_my_heuristic.py file for unit testing of the methods included in the heuristic.
    - Add a section in this file for testing that the use of the new heuristics work properly
    when using it through the optimizer interface.
"""

# Disable the could be a function for unit testing
# pylint: disable=no-self-use
# Disable name too longs (necessary for clarity in testing)
# pylint: disable=invalid-name

import unittest
import numpy as np
import time
from sklearn.neighbors import KNeighborsRegressor
from sklearn.gaussian_process import GaussianProcessRegressor

from bbo.optimizer import BBOptimizer
from bbo.heuristics.heuristics import Heuristic

# Imports for genetic algorithm
from bbo.heuristics.genetic_algorithm.selections import (
    tournament_pick,
    probabilistic_pick,
)
from bbo.heuristics.genetic_algorithm.mutations import mutate_chromosome_to_neighbor
from bbo.heuristics.genetic_algorithm.crossover import (
    single_point_crossover,
    double_point_crossover,
)

# Imports for simulated_annealing
from bbo.heuristics.simulated_annealing.restart_functions import random_restart
from bbo.heuristics.simulated_annealing.neighbor_functions import hop_to_next_value
from bbo.heuristics.simulated_annealing.cooldown_functions import (
    multiplicative_schedule,
)

# Imports for surrogate models
from bbo.heuristics.surrogate_models.next_parameter_strategies import (
    maximum_probability_improvement,
    expected_improvement,
    l_bfgs_b_minimizer,
)
from bbo.heuristics.surrogate_models.regression_models import (
    DecisionTreeSTDRegressor,
    CensoredGaussianProcesses,
)


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


class AsyncParabola:
    """
    Black-box class that will be used for testing heuristics that censors some data.
    """

    def __init__(self):
        """
        Initialization of the black-box
        """
        print("I'm the async Parabola function ! Good luck finding my optimum !")

    def compute(self, array_2d):
        """
        Computes the value of the parabola at data point array_2d
        """
        random_time = np.round(np.abs(np.random.normal(size=1, loc=3, scale=0.5)))[0]
        time.sleep(random_time)
        return array_2d[0] ** 2 + array_2d[1] ** 2


class TestHeuristic(unittest.TestCase):
    """
    Tests the different abstract methods raise an exception if called without overwritting.
    """

    def setUp(self):
        """
        Sets up the initialization of the Heuristic class.
        """
        self.heuristic = Heuristic()

    def test_init(self):
        """
        Tests that the attributes are well set.
        """
        self.assertFalse(self.heuristic.stop)

    def test_choose_next_parameter(self):
        """
        Tests that the "choose_next_parameter" method raises a NotImplementedError.
        """
        self.assertRaises(NotImplementedError, self.heuristic.choose_next_parameter, {})

    def test_summary(self):
        """
        Tests that the "summary" method raises a NotImplementedError.
        """
        self.assertRaises(NotImplementedError, self.heuristic.summary)

    def test_reset(self):
        """
        Tests that the "reset" method raises a NotImplementedError.
        """
        self.assertRaises(NotImplementedError, self.heuristic.reset)


class TestGeneticAlgorithms(unittest.TestCase):
    """
    Tests the different selection methods for selecting the two fittest parents in the population.
    """

    def setUp(self):
        """
        Sets up the testing procedure by initializing the parabola as the black-box function.
        """
        self.fake_black_box = Parabola()

    def test_tournament_pick_single_crossover(self):
        """
        Tests that the optimization works properly when using the tournament pick method for
        selection of the fittest parents + a single crossover method.
        """
        bb_obj = BBOptimizer(
            black_box=self.fake_black_box,
            parameter_space=np.array(
                [np.arange(-5, 5, 1), np.arange(-6, 6, 1), np.arange(-6, 6, 1)]
            ).T,
            heuristic="genetic_algorithm",
            initial_sample_size=2,
            max_iteration=10,
            selection_method=tournament_pick,
            crossover_method=single_point_crossover,
            mutation_method=mutate_chromosome_to_neighbor,
            pool_size=5,
            mutation_rate=0.1,
            elitism=False,
        )
        bb_obj.optimize()

    def test_probabilistic_pick_single_crossover(self):
        """
        Tests that the optimization works properly when using the probabilistic pick method for
        selection of the fittest parents + a single crossover method.
        """
        bb_obj = BBOptimizer(
            black_box=self.fake_black_box,
            parameter_space=np.array(
                [
                    np.arange(-5, 5, 1),
                    np.arange(-6, 6, 1),
                    np.arange(-5, 5, 1),
                    np.arange(-6, 6, 1),
                    np.arange(-5, 5, 1),
                    np.arange(-6, 6, 1),
                    np.arange(-5, 5, 1),
                    np.arange(-6, 6, 1),
                ]
            ).T,
            heuristic="genetic_algorithm",
            initial_sample_size=2,
            max_iteration=10,
            selection_method=probabilistic_pick,
            crossover_method=single_point_crossover,
            mutation_method=mutate_chromosome_to_neighbor,
            mutation_rate=0.2,
        )
        bb_obj.optimize()

    def test_tournament_pick_double_crossover(self):
        """
        Tests that the optimization works properly when using the tournament pick method for
        selection of the fittest parents + double crossover method.
        """
        bb_obj = BBOptimizer(
            black_box=self.fake_black_box,
            parameter_space=np.array(
                [np.arange(-5, 5, 1), np.arange(-6, 6, 1), np.arange(-6, 6, 1)]
            ).T,
            heuristic="genetic_algorithm",
            initial_sample_size=2,
            max_iteration=10,
            selection_method=tournament_pick,
            crossover_method=double_point_crossover,
            mutation_method=mutate_chromosome_to_neighbor,
            pool_size=5,
            mutation_rate=0.1,
            elitism=False,
        )
        bb_obj.optimize()

    def test_probabilistic_pick_double_crossover(self):
        """
        Tests that the optimization works properly when using the tournament pick method for
        selection of the fittest parents + double crossover method.
        """
        bb_obj = BBOptimizer(
            black_box=self.fake_black_box,
            parameter_space=np.array(
                [
                    np.arange(-5, 5, 1),
                    np.arange(-6, 6, 1),
                    np.arange(-6, 6, 1),
                    np.arange(-6, 6, 1),
                ]
            ).T,
            heuristic="genetic_algorithm",
            initial_sample_size=2,
            max_iteration=10,
            selection_method=tournament_pick,
            crossover_method=double_point_crossover,
            mutation_method=mutate_chromosome_to_neighbor,
            pool_size=5,
            mutation_rate=0.1,
            elitism=False,
        )
        bb_obj.optimize()


class TestSimulatedAnnealing(unittest.TestCase):
    """
    Tests that the optimization process works properly when using simulated annealing as an
    heuristic.
    """

    def setUp(self):
        """
        Sets up the testing procedure by initializing the parabola as the black-box function.
        """
        self.fake_black_box = Parabola()

    def test_simulated_annealing_no_restart(self):
        """
        Tests that the simulated annealing algorithm works properly when used through the
        optimizer interface and without using any restart.
        """
        bb_obj = BBOptimizer(
            black_box=self.fake_black_box,
            parameter_space=np.array(
                [
                    np.arange(-5, 5, 1),
                    np.arange(-6, 6, 1),
                    np.arange(-6, 6, 1),
                    np.arange(-6, 6, 1),
                ]
            ).T,
            heuristic="simulated_annealing",
            initial_sample_size=2,
            max_iteration=10,
            initial_temperature=1000,
            cooldown_function=multiplicative_schedule,
            neighbor_function=hop_to_next_value,
            cooling_factor=3,
        )
        bb_obj.optimize()

    def test_simulated_annealing_with_restart(self):
        """
        Tests that the simulated annealing algorithm works properly when used through the
        optimizer interface when using a restart.
        """
        bb_obj = BBOptimizer(
            black_box=self.fake_black_box,
            parameter_space=np.array(
                [
                    np.arange(-5, 5, 1),
                    np.arange(-6, 6, 1),
                    np.arange(-6, 6, 1),
                    np.arange(-6, 6, 1),
                ]
            ).T,
            heuristic="simulated_annealing",
            initial_sample_size=2,
            max_iteration=10,
            initial_temperature=1000,
            cooldown_function=multiplicative_schedule,
            neighbor_function=hop_to_next_value,
            cooling_factor=3,
            restart=random_restart,
            bernouilli_parameter=0.2,
        )
        bb_obj.optimize()
        print(bb_obj.history["fitness"])


class TestSurrogateModels(unittest.TestCase):
    """
    Tests that the optimization process works properly when using surrogate model as an
    heuristic.
    """

    def setUp(self):
        """
        Sets up the testing procedure by initializing the parabola as the black-box function.
        """
        self.fake_black_box = Parabola()
        self.fake_async_black_box = AsyncParabola()

    def test_surrogate_model_gp_ei(self):
        """
        Tests that the optimization process surrogate models integrates properly in the
        BBOptimizer when using GP + EI.
        """
        bb_obj = BBOptimizer(
            black_box=self.fake_black_box,
            parameter_space=np.array(
                [
                    np.arange(-5, 5, 1),
                    np.arange(-6, 6, 1),
                    np.arange(-6, 6, 1),
                    np.arange(-6, 6, 1),
                ]
            ).T,
            heuristic="surrogate_model",
            regression_model=GaussianProcessRegressor,
            next_parameter_strategy=expected_improvement,
            initial_sample_size=2,
            max_iteration=10,
        )
        bb_obj.optimize()

    def test_surrogate_model_gp_mpi(self):
        """
        Tests that the optimization process surrogate models integrates properly in the
        BBOptimizer when using GP + MPI.
        """
        bb_obj = BBOptimizer(
            black_box=self.fake_black_box,
            parameter_space=np.array(
                [
                    np.arange(-5, 5, 1),
                    np.arange(-6, 6, 1),
                    np.arange(-6, 6, 1),
                    np.arange(-6, 6, 1),
                ]
            ).T,
            heuristic="surrogate_model",
            regression_model=GaussianProcessRegressor,
            next_parameter_strategy=maximum_probability_improvement,
            initial_sample_size=2,
            max_iteration=10,
        )
        bb_obj.optimize()

    # def test_surrogate_model_knn_min(self):
    #     """
    #     Tests that the optimization process surrogate models integrates properly in the
    #     BBOptimizer when using KNearestNeighbor regressor and the regressed function as the merit
    #     one.
    #     """
    #     bb_obj = BBOptimizer(black_box=self.fake_black_box,
    #                          parameter_space=np.array([np.arange(-5, 5, 1), np.arange(-6, 6, 1),
    #                                                    np.arange(-6, 6, 1), np.arange(-6, 6, 1)]).T,
    #                          heuristic="surrogate_model",
    #                          regression_model=KNeighborsRegressor,
    #                          next_parameter_strategy=l_bfgs_b_minimizer,
    #                          initial_sample_size=6,
    #                          max_iteration=10)
    #     bb_obj.optimize()

    def test_surrogate_model_regression_tree_ei(self):
        """
        Tests that the optimization with regression trees and expected improvement behaves as
        expected.
        """
        bb_obj = BBOptimizer(
            black_box=self.fake_black_box,
            parameter_space=np.array(
                [
                    np.arange(-5, 5, 1),
                    np.arange(-6, 6, 1),
                    np.arange(-6, 6, 1),
                    np.arange(-6, 6, 1),
                ]
            ).T,
            heuristic="surrogate_model",
            regression_model=DecisionTreeSTDRegressor,
            next_parameter_strategy=expected_improvement,
            initial_sample_size=5,
            max_iteration=10,
            max_retry=10,
        )
        bb_obj.optimize()
        print(bb_obj.history)

    def test_surrogate_model_censored_bayesian_ei(self):
        """
        Tests that the optimization with regression trees and expected improvement behaves as
        expected.
        """
        bb_obj = BBOptimizer(
            black_box=self.fake_async_black_box,
            parameter_space=np.array(
                [
                    np.arange(-5, 5, 1),
                    np.arange(-6, 6, 1),
                    np.arange(-6, 6, 1),
                    np.arange(-6, 6, 1),
                ]
            ).T,
            heuristic="surrogate_model",
            regression_model=CensoredGaussianProcesses,
            next_parameter_strategy=expected_improvement,
            initial_sample_size=5,
            async_optim=True,
            max_step_cost=1,
            max_iteration=10,
            max_retry=10,
        )
        bb_obj.optimize()
        print(bb_obj.history)


class TestExhaustiveSearch(unittest.TestCase):
    """Tests the exhaustive_search heuristic.
    """

    def setUp(self):
        """
        Sets up the testing procedure by initializing the parabola as the black-box function.
        """
        self.fake_black_box = Parabola()

    def test_exhaustive_search(self):
        """
        Tests that the exhaustive search heuristic tests all the parametrization when the budget is
        equal to the size of the parametric grid.
        """
        parametric_grid = np.array([np.arange(-5, 5, 1), np.arange(-6, 6, 1),]).T
        bb_obj = BBOptimizer(
            black_box=self.fake_black_box,
            parameter_space=parametric_grid,
            heuristic="exhaustive_search",
            initial_sample_size=2,
            max_iteration=120,
        )
        bb_obj.optimize()
        exhaustive_grid = np.array(np.meshgrid(*parametric_grid)).T.reshape(
            -1, len(parametric_grid)
        )
        np.testing.assert_array_equal(bb_obj.history["parameters"][2:], exhaustive_grid)


if __name__ == "__main__":
    unittest.main()
