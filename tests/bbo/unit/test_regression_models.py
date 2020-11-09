# Copyright 2020 BULL SAS All rights reserved
"""
Tests the regression models in the regression_models module.
"""
import unittest
import numpy as np
import pandas as pd
from bbo.heuristics.surrogate_models.regression_models import (
    DecisionTreeSTDRegressor,
    CensoredGaussianProcesses,
)
from sklearn.tree import DecisionTreeRegressor

# Fake data to fit the models on
np.random.seed(1)
X = np.random.rand(100, 10)
y = np.random.rand(100, 1)
truncated = np.random.choice(a=[False, True], size=100)


class TestRegressionTree(unittest.TestCase):
    """
    Unit-testing for the regression models.
    """

    def test_decision_tree_no_std(self):
        """
        Tests the class RandomForestSRDRegressor when not returning the STD, by checking that the
        returned prediction is the same than when using the basic sklearn regressor.
        """
        dtstd = DecisionTreeSTDRegressor()
        dtstd.fit(X, y)
        y_mean = dtstd.predict(X, return_std=False)
        dtr = DecisionTreeRegressor(min_samples_leaf=2)
        dtr.fit(X, y)
        y_pred = dtr.predict(X)
        np.testing.assert_array_almost_equal(y_pred, y_mean)

    def test_decision_tree_std(self):
        """
        Tests the class RandomForestSTDRegressor when returning the STD.
        """
        dtstd = DecisionTreeSTDRegressor()
        dtstd.fit(X, y)
        _, y_std = dtstd.predict(X, return_std=True)
        expected_mean_y_std = 0.047695347215556606
        # self.assertAlmostEqual(expected_mean_y_std, np.mean(y_std))


class TestCensoredGaussian(unittest.TestCase):
    """
    Tests the behavior of the censored gaussian process class.
    """

    def setUp(self):
        """Sets up the unit tests by creating an attribute CensoredGaussianProcesses
        that will be tested.
        """
        self.cgp = CensoredGaussianProcesses()

    def test_fit_non_truncated(self):
        """
        Tests that the model is properly fitted on non-truncated data.
        """
        self.cgp._fit_non_truncated(X, y, truncated)

    def test_estimate_censored_data(self):
        """
        Tests that the estimation of the censored data happens properly.
        """
        model = self.cgp._fit_non_truncated(X, y, truncated)
        print(self.cgp._estimate_censored_data(X, truncated, model))

    def test_truncated_gaussian_distribution(self):
        """
        Tests that sampling from the truncated gaussian distribution behaves as expected.
        """
        lower_bound = 3
        mu = 2
        sigma = 1
        sample = self.cgp._truncated_gaussian_sample(mu, sigma, lower_bound)
        print(sample)

    def test_fit(self):
        """Tests that the censored bayesian model can be properly fit on the data.
        """
        self.cgp.fit(X, y, truncated)


if __name__ == "__main__":
    unittest.main()
