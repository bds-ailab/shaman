# Copyright 2020 BULL SAS All rights reserved
"""
Tests the various methods associated with the genetic algorithms:
    - Creation of the heuristic
    - Selection methods
    - Crossover methods
    - Mutation methods
"""

__copyright__ = """
Copyright (C) 2020 Bull S. A. S. - All rights reserved
Bull, Rue Jean Jaures, B.P.68, 78340, Les Clayes-sous-Bois, France
This is not Free or Open Source software.
Please contact Bull S. A. S. for details about its license.
"""

# Disable the could be a function for unit testing
# pylint: disable=no-self-use
# Disable name too longs (necessary for clarity in testing)
# pylint: disable=invalid-name

import unittest
import numpy as np
from numpy.testing import assert_array_equal, assert_almost_equal

from bbo.heuristics.genetic_algorithm.selections import (
    _select_by_fitness,
    _remove_from_history,
    _compute_weighted_probability,
    probabilistic_pick,
    tournament_pick,
    _sort_by_fitness,
)
from bbo.heuristics.genetic_algorithm.crossover import (
    single_point_crossover,
    double_point_crossover,
)
from bbo.heuristics.genetic_algorithm.mutations import mutate_chromosome_to_neighbor
from bbo.heuristics.genetic_algorithm.genetic_algorithm import GeneticAlgorithm

FAKE_HISTORY = {
    "fitness": np.array([10, 5, 4, 2, 15, 20]),
    "parameters": np.array([[1, 2], [2, 3], [1, 3], [4, 3], [2, 1], [1, 5]]),
}


class TestSelectionMethods(unittest.TestCase):
    """
    Tests the different selection methods for selecting the two fittest parents in the population.
    """

    def test_sort_by_fitness(self):
        """
        Tests that the sort by fitness function works properly by sorting the parameter vector
        according to the lowest fitness.
        """
        fake_fitness = np.array([20, 14, 10, 30, 32])
        fake_parameters = np.array([[1, 2], [2, 1], [3, 4], [3, 2], [1, 2]])
        sorted_values = _sort_by_fitness(fake_parameters, fake_fitness)
        expected_output = (
            np.array([[3, 4], [2, 1], [1, 2], [3, 2], [1, 2]]),
            np.array([10, 14, 20, 30, 32]),
        )
        assert_array_equal(
            sorted_values[0], expected_output[0], "Sorted parameters are " "correct."
        )
        assert_array_equal(
            sorted_values[1], expected_output[1], "Sorted fitness is correct."
        )

    def test_select_by_fitness(self):
        """
        Tests the function that selects the individuals using their minimum fitness value.
        """
        matingpool_size = 2
        selected_parameters, selected_fitness = _select_by_fitness(
            FAKE_HISTORY, matingpool_size
        )
        assert_array_equal(
            selected_parameters,
            np.array([[4, 3], [1, 3]]),
            "Selecting by fitness " "did not work " "properly.",
        )
        assert_array_equal(
            selected_fitness,
            np.array([2, 4]),
            "Selecting by fitness" " did not work properly.",
        )

    def test_remove_from_history(self):
        """
        Tests that the _remove_from_history function works properly.
        """
        filtered_parameter = np.array([2, 1])
        expected_fitness = np.array([10, 5, 4, 2, 20])
        expected_parameters = np.array([[1, 2], [2, 3], [1, 3], [4, 3], [1, 5]])
        filtered_parameters, filtered_fitness = _remove_from_history(
            FAKE_HISTORY["parameters"], FAKE_HISTORY["fitness"], filtered_parameter
        )
        assert_array_equal(
            filtered_parameters,
            expected_parameters,
            "Parameter filtering did not work properly.",
        )
        assert_array_equal(
            filtered_fitness,
            expected_fitness,
            "Fitness filtering did not work " "properly.",
        )

    def test_weighted_fitness(self):
        """
        Tests that given a weighted fitness, the associated probability vector is properly returned.
        """
        test_fitness = np.array([3, 3, 4, 2, 5, 8])
        expected_weighted_fitness = np.array(
            [0.1834061, 0.1834061, 0.1222707, 0.3668122, 0.0917031, 0.0524017]
        )
        assert_almost_equal(
            expected_weighted_fitness, _compute_weighted_probability(test_fitness)
        )

    def test_probabilistic_pick_no_elitism(self):
        """
        Tests that the probabilistic pick works properly, without elitism.
        """
        np.random.seed(20)
        expected_pick = np.array([[1, 3], [1, 2]])
        real_pick = probabilistic_pick(FAKE_HISTORY)
        assert_array_equal(
            expected_pick,
            real_pick,
            "Expected and real pick do not match when "
            "performing probabilistic pick.",
        )

    def test_probabilistic_pick_elitism(self):
        """
        Tests that the probabilistic pick works properly, with elitism.
        """
        np.random.seed(20)
        real_pick = probabilistic_pick(FAKE_HISTORY, elitism=True)
        elite_in_pick = np.any(real_pick == np.array([4, 3]))
        self.assertTrue(elite_in_pick, "Elite parameter was not selected.")

    def test_tournament_pick_no_elitism(self):
        """
        Tests that picking chromosomes using tournament pick works properly when not using elitism.
        """
        np.random.seed(20)
        expected_pick = np.array([[1, 3], [2, 1]])
        real_pick = tournament_pick(FAKE_HISTORY, pool_size=2)
        assert_array_equal(
            expected_pick,
            real_pick,
            "Expected and real pick do not match when " "performing tournament pick.",
        )

    def test_tournament_pick_big_size(self):
        """
        Tests that picking chromosomes using tournament pick works properly when using a pool
        size larger than the number of potential individuals.
        """
        np.random.seed(20)
        expected_pick = np.array([[4, 3], [1, 3]])
        real_pick = tournament_pick(FAKE_HISTORY, pool_size=50)
        assert_array_equal(
            expected_pick,
            real_pick,
            "Expected and real pick do not match when " "performing tournament pick.",
        )

    def test_tournament_pick_elitism(self):
        """
        Tests that picking chromosomes using tournament pick works properly when using elitism.
        """
        np.random.seed(20)
        real_pick = tournament_pick(FAKE_HISTORY, pool_size=2, elitism=True)
        elite_in_pick = np.any(real_pick == np.array([4, 3]))
        self.assertTrue(elite_in_pick, "Elite parameter was not selected.")


class TestCrossOverMethods(unittest.TestCase):
    """
    Tests the crossover module.
    """

    def test_single_point_crossover(self):
        """
        Tests that the single point crossover works properly.
        """
        np.random.seed(55)
        parent_1 = np.array([1, 2, 1, 4])
        parent_2 = np.array([3, 10, 20, 5])
        expected_child = np.array([1, 2, 20, 5])
        real_child = single_point_crossover(parent_1, parent_2)
        assert_array_equal(
            real_child,
            expected_child,
            "Single point crossover did not perform " "as expected.",
        )

    def test_double_point_crossover(self):
        """
        Tests that the double point crossover works properly.
        """
        np.random.seed(5)
        parent_1 = np.array([1, 2, 1, 4])
        parent_2 = np.array([3, 10, 20, 5])
        expected_child = np.array([1, 10, 1, 4])
        real_child = double_point_crossover(parent_1, parent_2)
        assert_array_equal(
            real_child,
            expected_child,
            "Double point crossover did not perform " "as expected.",
        )


class TestMutationMethods(unittest.TestCase):
    """
    Tests that the mutation methods work properly.
    """

    def test_mutation_next_neighbor(self):
        """
        Tests that the mutation next neighbor work as expected.
        """
        np.random.seed(10)
        chromosome = np.array([5, 8, 3, 4])
        ranges = np.array([np.arange(10), np.arange(10), np.arange(10), np.arange(10)])
        mutated_chromosome = mutate_chromosome_to_neighbor(chromosome, ranges)
        expected_chromosome = np.array([4, 7, 4, 5])
        assert_array_equal(
            mutated_chromosome,
            expected_chromosome,
            "Mutation did not behave as " "expected.",
        )


class TestGeneticAlgorithms(unittest.TestCase):
    """
    Tests that the Genetic Algorithm behaves as expected.
    """

    def test_class_initialization(self):
        """
        Tests that the GeneticAlgorithm class initializes properly.
        """
        GeneticAlgorithm(
            selection_method=tournament_pick,
            pool_size=2,
            crossover_method=single_point_crossover,
            mutation_method=mutate_chromosome_to_neighbor,
            mutation_rate=0.5,
        )

    def test_next_neighbor_no_mutation(self):
        """
        Tests that the next neighbor method returns properly the next child, when there is a
        mutation rate set to 0.
        """
        np.random.seed(10)
        ranges = np.array([np.arange(20), np.arange(20)])
        genetic_algorithm = GeneticAlgorithm(
            selection_method=tournament_pick,
            crossover_method=single_point_crossover,
            mutation_method=mutate_chromosome_to_neighbor,
            mutation_rate=0,
            pool_size=5,
        )
        next_parameter = genetic_algorithm.choose_next_parameter(FAKE_HISTORY, ranges)
        expected_next_parameter = np.array([4, 3])
        assert_array_equal(
            next_parameter,
            expected_next_parameter,
            "Selection of next parameter "
            "using genetic algorithm did "
            "not behave as expected.",
        )

    def test_next_neighbor_mutation(self):
        """
        Tests that the next neighbor method returns properly the next child, when there is a
        mutation rate set to 1.
        """
        np.random.seed(10)
        ranges = np.array([np.arange(20), np.arange(20)])
        genetic_algorithm = GeneticAlgorithm(
            selection_method=tournament_pick,
            crossover_method=single_point_crossover,
            mutation_method=mutate_chromosome_to_neighbor,
            mutation_rate=1,
            pool_size=5,
        )
        next_parameter = genetic_algorithm.choose_next_parameter(FAKE_HISTORY, ranges)
        expected_next_parameter = np.array([3, 3])
        assert_array_equal(
            next_parameter,
            expected_next_parameter,
            "Selection of next parameter "
            "using genetic algorithm did "
            "not behave as expected.",
        )


if __name__ == "__main__":
    unittest.main()
