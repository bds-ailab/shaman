# Copyright 2020 BULL SAS All rights reserved
"""
Tests that the various methods associated with surrogate modeling:
    - Creation of the heuristic
    - Acquisition functions
"""


# Disable the could be a function for unit testing
# pylint: disable=no-self-use
# Disable name too longs (necessary for clarity in testing)
# pylint: disable=invalid-name

import unittest
import os
import shutil
import numpy as np

# Example of regression function
from sklearn.neighbors import KNeighborsRegressor
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.preprocessing import StandardScaler
from bbo.heuristics.surrogate_models.regression_models import (
    DecisionTreeSTDRegressor,
    CensoredGaussianProcesses,
)

# Example of minimization function
from bbo.heuristics.surrogate_models.surrogate_models import SurrogateModel
from bbo.heuristics.surrogate_models.next_parameter_strategies import (
    l_bfgs_b_minimizer,
    cma_optimizer,
    compute_maximum_probability_improvement,
    maximum_probability_improvement,
    expected_improvement,
    compute_expected_improvement,
)

# fake history that will be used for testing the correct behavior of the
# heuristic
fake_history = {
    "fitness": np.array([10, 5, 4, 2, 15, 20]),
    "parameters": np.array([[1, 2], [2, 3], [1, 3], [4, 3], [2, 1], [1, 5]]),
    "truncated": np.array([True, True, False, False, False, True]),
}
# fake parameter range to use for testing
ranges = np.array([np.arange(20), np.arange(21)])


class TestAcquisitionFunctions(unittest.TestCase):
    """
    Tests that the acquisition functions from the "next_parameter_strategies" module work properly.
    """

    def setUp(self):
        """
        Sets up the test by regressing two functions, one using the nearest neighbor regressor
        and one using gaussian process by using the _build_prediction_function of the
        SurrogateModel class.
        """
        # k nearest neighbor regressor
        knn = KNeighborsRegressor()
        scaler = StandardScaler()
        scaler.fit(fake_history["parameters"])
        knn.fit(X=fake_history["parameters"], y=fake_history["fitness"])
        self.knn_fun = SurrogateModel._build_prediction_function(knn, scaler)
        # gaussian processes
        gaussian_process = GaussianProcessRegressor()
        gaussian_process.fit(
            X=fake_history["parameters"],
            y=fake_history["fitness"])
        self.gp_fun = SurrogateModel._build_prediction_function(
            gaussian_process, scaler
        )

    # def test_lbfgs_b(self):
    #     """
    #     Tests that the L_BFGS_B minimizer works properly.
    #     """
    #     np.random.seed(10)
    #     expected_min = np.array([9., 4.])
    #     real_min = l_bfgs_b_minimizer(self.knn_fun, ranges)
    #     np.testing.assert_array_equal(expected_min, real_min, "L-BFGS minimizer do not work as "
    #                                                           "expected.")

    # def test_cma(self):
    #     """
    #     Tests that the CMA minimizer works properly. Sadly, I have not figured out how to set the
    #     internal seed of the CMA package so I can't compare its value to a set value.
    #     """
    #     np.random.seed(10)
    #     cma_optimizer(self.knn_fun, ranges)
    #     self._remove_dat()

    @staticmethod
    def _remove_dat():
        """
        Removes the .dat file in the test folder that are created by the CMA optimizer.
        """
        test_dir = os.getcwd()
        for file in os.listdir(test_dir):
            if file.endswith(".dat"):
                os.remove(os.path.join(test_dir, file))
            if "outcmaes" == file:
                shutil.rmtree(os.path.join(test_dir, file))

    def test_compute_mpi(self):
        """
        Tests that the Maximum Probability Improvement function is computed properly, given the
        proper arguments.
        """
        means = np.array([3, 13, 15])
        stds = np.array([0.05, 0.5, 0.5])
        current_optimum = 5
        max_prob_imp = compute_maximum_probability_improvement(
            current_optimum, means, stds
        )
        expected_mpi = np.array([1, 0, 0])
        np.testing.assert_array_almost_equal(expected_mpi, max_prob_imp)

    def test_mpi(self):
        """
        Tests that the Maximum Probability Improvement function works properly when using
        regression as gp.
        """
        np.random.seed(10)
        expected_min = np.array([0, 19])
        real_min = maximum_probability_improvement(
            self.gp_fun, ranges, fake_history["fitness"]
        )
        np.testing.assert_array_equal(real_min, expected_min)

    def test_mpi_no_sd_option(self):
        """
        Tests that the MPI function raises an error when given a function that do not support the
        return_std option.
        """
        with self.assertRaises(TypeError):
            maximum_probability_improvement(
                self.knn_fun, ranges, fake_history["fitness"]
            )

    def test_compute_ei(self):
        """
        Tests that the Maximum Probability Improvement function is computed properly, given the
        proper arguments.
        """
        means = np.array([3, 13, 15])
        stds = np.array([0.05, 0.5, 0.5])
        current_optimum = 5
        expected_imp = compute_expected_improvement(
            current_optimum, means, stds)
        expected_ei = np.array([2, 0, 0])
        np.testing.assert_array_almost_equal(expected_ei, expected_imp)

    def test_ei(self):
        """
        Tests that the Expected Improvement function works properly.
        """
        np.random.seed(10)
        expected_min = np.array([0, 20])
        real_min = expected_improvement(
            self.gp_fun, ranges, fake_history["fitness"])
        np.testing.assert_array_equal(real_min, expected_min)

    def test_ei_no_sd_option(self):
        """
        Tests that the EI function works properly.
        """
        with self.assertRaises(TypeError):
            expected_improvement(self.knn_fun, ranges, fake_history["fitness"])


class TestSurrogateModels(unittest.TestCase):
    """
    Tests that the implementation of the surrogate models work properly.
    """

    def test_regression_model_no_fit(self):
        """
        Tests that when the regression model does not have a fit method, an AttributeError error is
        raised.
        """
        # class without fit
        class AintGotNoFit:
            """
            Fake class that doesn't have a fit method.
            """

            def predict(self):
                """
                Only a predict method.
                """
                print("I don't have no fit !")

        with self.assertRaises(AttributeError):
            SurrogateModel(
                regression_model=AintGotNoFit,
                next_parameter_strategy=expected_improvement,
            )

    def test_regression_model_no_predict(self):
        """
        Tests that when the regression model does not have a predict method, an error is raised.
        """
        # class without predict
        class AintGotNoPredict:
            """
            Fake class that doesn't have a predict method.
            """

            def fit(self):
                """
                Only a fit method.
                """
                print("I don't have no predict !")

        with self.assertRaises(AttributeError):
            SurrogateModel(
                regression_model=AintGotNoPredict,
                next_parameter_strategy=expected_improvement,
            )

    def test_fit_return_prediction_function(self):
        """
        Tests that there is no error when computing the regression function.
        """
        surrogate_model = SurrogateModel(
            regression_model=GaussianProcessRegressor,
            next_parameter_strategy=expected_improvement,
        )
        surrogate_model.regression_function(fake_history)

    def test_choose_next_parameter_mpi(self):
        """
        Checks that the selection of the next parameter works properly when using MPI.
        """
        expected_new_parameter = [4, 3]
        surrogate_model = SurrogateModel(
            regression_model=GaussianProcessRegressor,
            next_parameter_strategy=maximum_probability_improvement,
        )
        real_new_parameter = surrogate_model.choose_next_parameter(
            fake_history, ranges)
        np.testing.assert_array_equal(
            real_new_parameter, expected_new_parameter)

    def test_choose_next_parameter_ei(self):
        """
        Checks that the selection of the next parameter works properly when using EI.
        """
        expected_new_parameter = [4, 4]
        surrogate_model = SurrogateModel(
            regression_model=GaussianProcessRegressor,
            next_parameter_strategy=expected_improvement,
        )
        real_new_parameter = surrogate_model.choose_next_parameter(
            fake_history, ranges)
        np.testing.assert_array_equal(
            real_new_parameter, expected_new_parameter)

    # def test_choose_next_parameter_lbfgsb(self):
    #     """
    #     Checks that the selection of the next parameter works properly when using L-BFGS-B.
    #     """
    #     np.random.seed(10)
    #     expected_new_parameter = np.array([3.974002, 3.046726])
    #     surrogate_model = SurrogateModel(regression_model=GaussianProcessRegressor,
    #                                      next_parameter_strategy=l_bfgs_b_minimizer)
    #     real_new_parameter = surrogate_model.choose_next_parameter(
    #         fake_history, ranges)
    #     np.testing.assert_array_almost_equal(
    #         real_new_parameter, expected_new_parameter)

    def test_evaluate_quality(self):
        """
        Tests that the RMSE is properly returned.
        """
        expected_score = -2.184857
        surrogate_model = SurrogateModel(
            regression_model=GaussianProcessRegressor,
            next_parameter_strategy=expected_improvement,
        )
        surrogate_model.choose_next_parameter(fake_history, ranges)
        real_score = surrogate_model.evaluate_quality(fake_history)
        np.testing.assert_array_almost_equal(expected_score, real_score)


class TestCensoredBayesian(unittest.TestCase):
    """Tests that censored bayesian models work as expected.
    """

    def test_censored_bayesian(self):
        """
        Tests that censored bayesian + EI work properly
        """
        expected_new_parameter = [4, 4]
        surrogate_model = SurrogateModel(
            regression_model=CensoredGaussianProcesses,
            next_parameter_strategy=expected_improvement,
        )
        real_new_parameter = surrogate_model.choose_next_parameter(
            fake_history, ranges)
        np.testing.assert_array_equal(
            real_new_parameter, expected_new_parameter)


class TestDecisionTreeSTD(unittest.TestCase):
    """
    Tests that surrogate modeling using DecisionTreeRegressor work as expected.
    """

    def test_tree_ei(self):
        """
        Tests that using EI with DecisionTree works properly, by decomposing the process into each of its step.
        """
        # Define a tree and fit it on the historical data
        dtstdr = DecisionTreeSTDRegressor()
        dtstdr.fit(fake_history["parameters"], fake_history["fitness"])
        # Predict the regression values over the whole grid
        combination_ranges = np.array(
            np.meshgrid(*ranges)).T.reshape(-1, len(ranges))
        predictions_means, predictions_std = dtstdr.predict(
            combination_ranges, return_std=True
        )
        # Compute the EI and save the max
        current_optimum = np.min(fake_history["fitness"])
        computed_ei = compute_expected_improvement(
            current_optimum, predictions_means, predictions_std
        )
        max_ei_index = np.argmax(computed_ei)
        expected_next_parameter = combination_ranges[max_ei_index]
        # Compare it to the normal process
        surrogate_model = SurrogateModel(
            regression_model=DecisionTreeSTDRegressor,
            next_parameter_strategy=expected_improvement,
        )
        next_parameter = surrogate_model.choose_next_parameter(
            fake_history, ranges)
        np.testing.assert_array_equal(next_parameter, expected_next_parameter)


if __name__ == "__main__":
    unittest.main()
