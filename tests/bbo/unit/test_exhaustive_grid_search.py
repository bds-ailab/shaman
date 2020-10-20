"""Unit testing for exhaustive grid search.
"""
import unittest
import sys
from io import StringIO
import numpy as np
from numpy import testing
from bbo.heuristics.exhaustive_search.exhaustive_search import ExhaustiveSearch

PARAMETRIC_GRID = np.array([np.arange(-5, 5, 1), np.arange(-6, 6, 1),], dtype=object).T


class TestExhaustiveSearch(unittest.TestCase):
    """Unit testing for exhaustive search heuristic.
    """

    def test_next_parameter(self):
        """Tests that the next parameter is the right value, i.e.
        the next value has the right position in the grid.
        """
        history = {
            "fitness": np.array([1, 3, 4]),
            "parameters": np.array([[1, 2], [1, 2], [1, 2]]),
            "initialization": [False, False, False],
        }
        exhaustive_search = ExhaustiveSearch()
        next_parameter = exhaustive_search.choose_next_parameter(
            history, PARAMETRIC_GRID
        )
        testing.assert_array_equal(next_parameter, [-5, -3])

    def test_explore_all_grid(self):
        """Tests that with the right number of iterations, the whole grid is explored.
        """
        history = {"fitness": [], "parameters": [], "initialization": []}
        exhaustive_search = ExhaustiveSearch()
        tested_parameters = list()
        # Explore the whole parametric grid
        ix = 0
        while ix <= 119:
            tested_parameters.append(
                exhaustive_search.choose_next_parameter(history, PARAMETRIC_GRID)
            )
            # Append bogus fitness
            history["fitness"].append(1)
            ix += 1
        # Check that the whole parametric grid is the same as the tested parameters
        exhaustive_grid = np.array(np.meshgrid(*PARAMETRIC_GRID)).T.reshape(
            -1, len(PARAMETRIC_GRID)
        )
        testing.assert_array_equal(tested_parameters, exhaustive_grid)

    def test_number_tested(self):
        """Tests that the attribute which stores the number of tested parametrization.
        """
        history = {"fitness": [], "parameters": [], "initialization": []}
        exhaustive_search = ExhaustiveSearch()
        tested_parameters = list()
        # Explore the whole parametric grid
        ix = 0
        while ix <= 50:
            tested_parameters.append(
                exhaustive_search.choose_next_parameter(history, PARAMETRIC_GRID)
            )
            # Append bogus fitness
            history["fitness"].append(1)
            ix += 1
        self.assertEqual(ix, exhaustive_search.nbr_tested)

    def test_summary(self):
        """Tests that the summary printing the number of resampling is exact.
        """
        history = {"fitness": [], "parameters": [], "initialization": []}
        exhaustive_search = ExhaustiveSearch()
        tested_parameters = list()
        # Explore the whole parametric grid
        ix = 0
        while ix <= 50:
            tested_parameters.append(
                exhaustive_search.choose_next_parameter(history, PARAMETRIC_GRID)
            )
            # Append bogus fitness
            history["fitness"].append(1)
            ix += 1
        saved_stdout = sys.stdout
        try:
            out = StringIO()
            sys.stdout = out
            exhaustive_search.summary()
            output = out.getvalue().strip()
            assert output == "Number of tested parametrization: 51"
        finally:
            sys.stdout = saved_stdout


if __name__ == "__main__":
    unittest.main()
