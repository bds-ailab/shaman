"""Module for unit testing of bbo's test criteria.
"""
import unittest
import numpy as np
from bbo.stop_criteria import ImprovementCriterion, \
    CountMovementCriterion, DistanceMovementCriterion


class TestStopCriteria(unittest.TestCase):
    """Class to test the stop criteria included with BBO.
    """

    def test_best_improvement_not_enough_iterations(self):
        """Tests that when there are not enough iterations, the
        the improvement stop criterion with min automatically evaluates
        to True.
        """
        test_history = {"fitness": [1, 2, 3]}
        stop_process = ImprovementCriterion(
            stop_window=4, improvement_threshold=0.5, improvement_estimator=min)
        self.assertTrue(stop_process.stop_rule(test_history))

    def test_best_improvement_improvement(self):
        """Tests that when there is some improvement,
        the improvement stop criterion with min evaluates to True.
        """
        test_history = {"fitness": [5, 6, 3, 4, 1, 2, 3]}
        stop_process = ImprovementCriterion(
            stop_window=4, improvement_threshold=0.2, improvement_estimator=min
        )
        self.assertTrue(stop_process.stop_rule(test_history))

    def test_best_improvement_no_improvement(self):
        """Tests that when there is no improvement,
        the improvement stop criterion with min evaluates to False.
        """
        test_history = {"fitness": [1, 6, 3, 4, 1, 2, 3]}
        stop_process = ImprovementCriterion(
            stop_window=4, improvement_threshold=0.2, improvement_estimator=min
        )
        self.assertFalse(stop_process.stop_rule(test_history))

    def test_average_improvement_improvement(self):
        """Tests that when there is some improvement,
        the improvement stop criterion evaluates to True when used
        with the average estimator.
        """
        test_history = {"fitness": [5, 6, 3, 4, 1, 2, 3]}
        stop_process = ImprovementCriterion(
            stop_window=4, improvement_threshold=0.2, improvement_estimator=np.mean
        )
        self.assertTrue(stop_process.stop_rule(test_history))

    def test_average_improvement_no_improvement(self):
        """Tests that when there is no improvement,
        the improvement stop criterion evaluates to False when used
        with the average estimator.
        """
        test_history = {"fitness": [1, 1, 3, 4, 1, 4, 8]}
        stop_process = ImprovementCriterion(
            stop_window=4, improvement_threshold=0.2, improvement_estimator=np.mean
        )
        self.assertFalse(stop_process.stop_rule(test_history))

    def test_count_movement_not_enough_iterations(self):
        """Tests that when there are not enough iterations, the
        best_improvement stop criterion automatically evaluates
        to False.
        """
        test_history = {"parameters": [np.array([1, 2]),
                                       np.array([2, 3]),
                                       np.array([1, 2])]
                        }
        stop_process = CountMovementCriterion(
            nbr_parametrizations=2, stop_window=4)
        self.assertTrue(stop_process.stop_rule(test_history))

    def test_count_movement_stop(self):
        """Tests that the optimization process stops if there is no
        unique newly tested parametrization.
        """
        test_history = {"parameters": np.array([np.array([1, 2]),
                                                np.array([2, 3]),
                                                np.array([1, 2]),
                                                np.array([1, 2]),
                                                np.array([1, 2]),
                                                np.array([2, 3]),
                                                np.array([1, 2]),
                                                ])
                        }
        stop_process = CountMovementCriterion(
            nbr_parametrizations=2, stop_window=4)
        self.assertFalse(stop_process.stop_rule(test_history))

    def test_count_movement_no_stop(self):
        """Tests that the optimization process stops if there is enough
        unique newly tested parametrization.
        """
        test_history = {"parameters": np.array([np.array([1, 2]),
                                                np.array([2, 3]),
                                                np.array([1, 2]),
                                                np.array([1, 2]),
                                                np.array([1, 2]),
                                                np.array([2, 3]),
                                                np.array([4, 5]),
                                                ])
                        }
        stop_process = CountMovementCriterion(
            nbr_parametrizations=2, stop_window=4)
        self.assertTrue(stop_process.stop_rule(test_history))

    def test_distance_movement_not_enough_iterations(self):
        """Tests that when there are not enough iterations, the
        best_improvement stop criterion automatically evaluates
        to False.
        """
        test_history = {"parameters": [np.array([1, 2]),
                                       np.array([2, 3]),
                                       np.array([1, 2])]
                        }
        stop_process = DistanceMovementCriterion(
            stop_window=4, distance=2)
        self.assertTrue(stop_process.stop_rule(test_history))

    def test_distance_movement_no_stop(self):
        """Tests that the optimization process stops if there is enough
        unique newly tested parametrization.
        """
        test_history = {"parameters": np.array([np.array([1, 2]),
                                                np.array([2, 3]),
                                                np.array([1, 2]),
                                                np.array([1, 2]),
                                                np.array([1, 2]),
                                                np.array([2, 3]),
                                                np.array([4, 5]),
                                                ])
                        }
        stop_process = DistanceMovementCriterion(
            stop_window=4, distance=2)
        self.assertTrue(stop_process.stop_rule(test_history))

    def test_distance_movement_stop(self):
        """Tests that the optimization process stops if there is enough
        unique newly tested parametrization.
        """
        test_history = {"parameters": np.array([np.array([1, 2]),
                                                np.array([2, 3]),
                                                np.array([1, 2]),
                                                np.array([1, 2]),
                                                np.array([1, 2]),
                                                np.array([2, 3]),
                                                np.array([1, 2]),
                                                ])
                        }
        stop_process = DistanceMovementCriterion(
            stop_window=4, distance=1)
        self.assertFalse(stop_process.stop_rule(test_history))


if __name__ == "__main__":
    unittest.main()
