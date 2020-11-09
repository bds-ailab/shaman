# Copyright 2020 BULL SAS All rights reserved
"""
Tests the various methods associated with simulated annealing:
    - Creation of the heuristic
    - Cool-down schedule
    - Neighboring functions
    - Restart functions
"""

# Disable the could be a function for unit testing
# pylint: disable=no-self-use
# Disable name too longs (necessary for clarity in testing)
# pylint: disable=invalid-name

import unittest
import numpy as np

from bbo.heuristics.simulated_annealing.cooldown_functions import (
    exponential_schedule,
    logarithmic_schedule,
    multiplicative_schedule,
)
from bbo.heuristics.simulated_annealing.neighbor_functions import (
    hop_to_next_value,
    random_draw,
)
from bbo.heuristics.simulated_annealing.restart_functions import (
    random_restart,
    threshold_restart,
)
from bbo.heuristics.simulated_annealing.simulated_annealing import SimulatedAnnealing

fake_history = {
    "fitness": np.array([10, 5, 4, 2, 15, 20]),
    "parameters": np.array([[1, 2], [2, 3], [1, 3], [4, 3], [2, 1], [1, 5]]),
}


class TestCoolDownSchedules(unittest.TestCase):
    """
    Tests that the different methods available for describing the cool-down schedules behave as
    expected.
    """

    def test_exponential_schedule_wrong_factor(self):
        """
        Test exponential schedule with a factor that is superior to one. It should raise an
        Assertion error and abort the process.
        """
        cooling_factor = 10
        current_iteration = 1
        initial_temperature = 100
        with self.assertRaises(AssertionError):
            exponential_schedule(
                initial_temperature,
                current_iteration,
                cooling_factor)

    def test_exponential_schedule(self):
        """
        Tests that exponential schedule works as expected.
        """
        cooling_factor = 0.8
        current_iteration = 2
        initial_temperature = 100
        expected_temperature = 64.00000000000001
        actual_temperature = exponential_schedule(
            initial_temperature, current_iteration, cooling_factor
        )
        self.assertEqual(
            expected_temperature,
            actual_temperature,
            "Exponential schedule did not " "return expected results.",
        )

    def test_logarithmic_schedule_wrong_factor(self):
        """
        Test logarithmic schedule with a factor that is inferior to one. It should raise an
        Assertion error and abort the process.
        """
        cooling_factor = 0.01
        current_iteration = 1
        initial_temperature = 100
        with self.assertRaises(AssertionError):
            logarithmic_schedule(
                initial_temperature,
                current_iteration,
                cooling_factor)

    def test_logarithmic_schedule(self):
        """
        Tests that the logarithmic schedule works as expected.
        """
        cooling_factor = 2
        current_iteration = 2
        initial_temperature = 100
        expected_temperature = 31.2771272649591
        actual_temperature = logarithmic_schedule(
            initial_temperature, current_iteration, cooling_factor
        )
        self.assertEqual(
            expected_temperature,
            actual_temperature,
            "Logarithmic schedule did not " "return expected value.",
        )

    def test_multiplicative_schedule_wrong_factor(self):
        """
        Test multiplicative schedule with a factor that is inferior to one. It should raise an
        Assertion error and abort the process.
        """
        cooling_factor = 0.01
        current_iteration = 1
        initial_temperature = 100
        with self.assertRaises(AssertionError):
            multiplicative_schedule(
                initial_temperature, current_iteration, cooling_factor
            )

    def test_multiplicative_schedule(self):
        """
        Tests that the logarithmic schedule works as expected.
        """
        cooling_factor = 2
        current_iteration = 2
        initial_temperature = 100
        expected_temperature = 20
        actual_temperature = multiplicative_schedule(
            initial_temperature, current_iteration, cooling_factor
        )
        self.assertEqual(
            expected_temperature,
            actual_temperature,
            "Multiplicative schedule did " "not " "return expected value.",
        )


class TestNeighboringFunction(unittest.TestCase):
    """
    Tests that the function that compute the neighbors of the current point under evaluation
    behave as expected.
    """

    def test_random_draw_0(self):
        """
        Tests that the random_draw function behaves as expected when the draw is 0.
        """
        np.random.seed(0)
        cur_idx = random_draw(1, 4)
        self.assertEqual(cur_idx, 2)

        np.random.seed(0)
        cur_idx = random_draw(3, 4)
        self.assertEqual(cur_idx, 3)

        # !! The index can be greater than the index range !!
        np.random.seed(0)
        cur_idx = random_draw(10, 4)
        self.assertEqual(cur_idx, 10)

    def test_random_draw_1(self):
        """
        Tests that the random_draw function behaves as expected when the draw is 1.
        """
        np.random.seed(1)
        cur_idx = random_draw(1, 4)
        self.assertEqual(cur_idx, 0)

        np.random.seed(1)
        cur_idx = random_draw(0, 4)
        self.assertEqual(cur_idx, 0)

        # !! The index can be greater than the index range !!
        np.random.seed(1)
        cur_idx = random_draw(10, 4)
        self.assertEqual(cur_idx, 9)

    def test_random_draw_2(self):
        """
        Tests that the random_draw function behaves as expected when the draw is 2.
        """
        np.random.seed(3)
        cur_idx = random_draw(1, 4)
        self.assertEqual(cur_idx, 1)

    def test_hop_next_value_center_grid(self):
        """
        Tests that the hop_to_next_value function behaves as expected when the current parameter is
        located in the middle of the grid.
        """
        np.random.seed(10)
        fake_grid = np.array(
            [np.arange(-10, 10, 1), np.arange(-10, 10, 1),
             np.arange(-10, 11, 1)]
        )
        current_parameter = np.array([0, 0, 0])
        next_value = hop_to_next_value(current_parameter, fake_grid)
        expected_value = np.array([-1, -1, 1])
        np.testing.assert_array_equal(
            next_value,
            expected_value,
            "Neighboring parameter was not " "the expected one.",
        )

    def test_hop_next_value_out_of_grid(self):
        """
        Tests that the hop_to_next_value function behaves as expected when the current parameter
        is located on the outside of the grid, by returning an IndexError exception.
        """
        np.random.seed(10)
        fake_grid = np.array(
            [np.arange(-10, 10, 1), np.arange(-10, 10, 1),
             np.arange(-10, 11, 1)]
        )
        current_parameter = np.array([10, 8, 8])
        with self.assertRaises(IndexError):
            hop_to_next_value(current_parameter, fake_grid)

    def test_hop_next_value_lower_border_grid(self):
        """
        Tests that the hop_to_next_value function behaves as expected when the current parameter
        is located on the lower border of the grid, by returning a parameter that is on the grid.
        """
        np.random.seed(12)
        fake_grid = np.array(
            [np.arange(-10, 10, 1), np.arange(-10, 10, 1),
             np.arange(-10, 11, 1)]
        )
        current_parameter = np.array([-10, -9, -10])
        next_value = hop_to_next_value(current_parameter, fake_grid)
        expected_next_value = np.array([-10, -10, -10])
        np.testing.assert_array_equal(
            expected_next_value,
            next_value,
            "Expected and real value "
            "do not match when the "
            "current parameter is on "
            "the lower end of the grid.",
        )

    def test_hop_next_value_upper_border_grid(self):
        """
        Tests that the hop_to_next_value function behaves as expected when the current parameter
        is located on the upper border of the grid, by returning a parameter that is on the grid.
        """
        np.random.seed(13)
        fake_grid = np.array(
            [np.arange(-10, 10, 1), np.arange(-10, 10, 1),
             np.arange(-10, 11, 1)]
        )
        current_parameter = np.array([9, 9, 10])
        next_value = hop_to_next_value(current_parameter, fake_grid)
        expected_next_value = np.array([9, 8, 10])
        np.testing.assert_array_equal(
            expected_next_value,
            next_value,
            "Expected and real value "
            "do not match when the "
            "current parameter is on "
            "the lower end of the grid.",
        )


class TestRestartMethods(unittest.TestCase):
    """
    Tests the different methods that restart the system.
    """

    def test_random_restarts(self):
        """
        Tests that the random restart method works properly.
        """
        bernouilli_parameter = 1
        t_max = 10
        real_restart, real_t_max = random_restart(
            bernouilli_parameter=bernouilli_parameter, initial_temperature=t_max
        )
        self.assertTrue(real_restart)
        self.assertEqual(
            t_max, real_t_max, "Maximal temperature was not computed properly."
        )

    def test_threshold_restarts(self):
        """
        Tests that the threshold restart method works properly.
        """
        probability_threshold = 0.3
        current_probability = 0.2
        t_max = 10
        real_restart, real_t_max = threshold_restart(
            probability_threshold=probability_threshold,
            current_probability=current_probability,
            initial_temperature=t_max,
        )
        self.assertTrue(real_restart)
        self.assertEqual(
            t_max, real_t_max, "Maximal temperature was not computed properly."
        )


class TestSimulatedAnnealing(unittest.TestCase):
    """
    Tests that the simulated annealing heuristic behaves as expected.
    """

    def test_simulated_annealing_wrong_temp(self):
        """
        Tests that the simulated annealing class raises an error when the temperature is of the
        wrong type.
        """
        with self.assertRaises(TypeError):
            SimulatedAnnealing(
                initial_temperature="tutu",
                neighbor_function=hop_to_next_value,
                cooldown_function=multiplicative_schedule,
                cooling_factor=2,
                restart=False,
            )

    def test_simulated_annealing_neg_temp(self):
        """
        Tests that the simulated annealing raises an error when given a negative initial
        temperature.
        """
        with self.assertRaises(TypeError):
            SimulatedAnnealing(
                initial_temperature=-1,
                neighbor_function=hop_to_next_value,
                cooldown_function=multiplicative_schedule,
                cooling_factor=2,
                restart=False,
            )

    def test_simulated_annealing_no_restart(self):
        """
        Tests that the simulated annealing heuristic restarts properly when not using any restart
        for finding the next relevant parameter.
        """
        np.random.seed(10)
        ranges = np.array([np.arange(20), np.arange(20)])
        sa = SimulatedAnnealing(
            initial_temperature=50,
            neighbor_function=hop_to_next_value,
            cooldown_function=multiplicative_schedule,
            cooling_factor=2,
            restart=False,
        )
        next_parameter = sa.choose_next_parameter(fake_history, ranges)
        expected_next_parameter = np.array([2, 6])
        np.testing.assert_array_equal(
            next_parameter, expected_next_parameter, "tutu")

    def test_simulated_annealing_random_restart(self):
        """
        Tests that the simulated annealing heuristic restarts properly when using random restart
        for finding the next relevant parameter.
        """
        np.random.seed(10)
        ranges = np.array([np.arange(20), np.arange(20)])
        sa = SimulatedAnnealing(
            initial_temperature=50,
            neighbor_function=hop_to_next_value,
            cooldown_function=multiplicative_schedule,
            cooling_factor=3,
            restart=random_restart,
            bernouilli_parameter=0.3,
        )
        next_parameter = sa.choose_next_parameter(fake_history, ranges)
        expected_next_parameter = np.array([2, 6])
        np.testing.assert_array_equal(next_parameter, expected_next_parameter)

    def test_simulated_annealing_threshold_restart(self):
        """
        Tests that the simulated annealing heuristic restarts properly when using the threshold
        method for finding the next relevant parameter.
        """
        np.random.seed(10)
        ranges = np.array([np.arange(20), np.arange(20)])
        sa = SimulatedAnnealing(
            initial_temperature=50,
            neighbor_function=hop_to_next_value,
            cooldown_function=multiplicative_schedule,
            cooling_factor=3,
            restart=threshold_restart,
            probability_threshold=0.3,
        )
        next_parameter = sa.choose_next_parameter(fake_history, ranges)
        expected_next_parameter = np.array([2, 6])
        np.testing.assert_array_equal(next_parameter, expected_next_parameter)

    def test_simulated_annealing_temp_stop(self):
        """
        Tests that the simulated annealing heuristic stop properly when reaching a low temperature.
        """
        np.random.seed(10)
        ranges = np.array([np.arange(20), np.arange(20)])
        sa = SimulatedAnnealing(
            initial_temperature=0.1,
            neighbor_function=hop_to_next_value,
            cooldown_function=multiplicative_schedule,
            cooling_factor=10,
            restart=threshold_restart,
            probability_threshold=0.3,
        )
        sa.choose_next_parameter(fake_history, ranges)  # first computation
        next_parameter = sa.choose_next_parameter(fake_history, ranges)
        expected_next_parameter = np.array([4, 3])
        np.testing.assert_array_equal(next_parameter, expected_next_parameter)
        self.assertTrue(sa.stop)

    def test_reset(self):
        """
        Tests that the "reset" method reset the attributes.
        """
        np.random.seed(10)
        ranges = np.array([np.arange(20), np.arange(20)])
        sa = SimulatedAnnealing(
            initial_temperature=50,
            neighbor_function=hop_to_next_value,
            cooldown_function=multiplicative_schedule,
            cooling_factor=3,
            restart=threshold_restart,
            probability_threshold=0.3,
        )
        next_parameter = sa.choose_next_parameter(fake_history, ranges)
        expected_next_parameter = np.array([2, 6])
        np.testing.assert_array_equal(next_parameter, expected_next_parameter)
        sa.reset()
        self.assertEqual(sa.current_t, 50)
        self.assertEqual(sa.nbr_iteration, 0)
        self.assertEqual(sa.restart, 0)
        self.assertListEqual(sa.energy, list())


if __name__ == "__main__":
    unittest.main()
