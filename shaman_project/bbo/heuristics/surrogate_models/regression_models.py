"""
This module contains different regression models to use with the surrogate modeling heuristics.

For now, the following module is available:
    - Decision tree regressors
    - Censored data bayesian optimization
"""

from sklearn.tree import DecisionTreeRegressor
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import Matern
from scipy.stats import norm, truncnorm
import numpy as np


class DecisionTreeSTDRegressor(DecisionTreeRegressor):
    """
    This class extends the class DecisionTreeSTDRegressor available in the sklearn module, by adding
    the possibility to return the standard error of each predicted data point (i.e. the impurity
    of the node where the predicted data point is located). Adding this standard error makes it
    possible to use this model as a regression model with Expected Improvement and Maximum
    Probability Improvement as next parameter acquisition strategy.
    """

    def __init__(self, min_samples_leaf=2, *args, **kwargs):
        """
        Initialize an object of class DecisionTreeSTDRegressor, which inherits from the
        DecisionTreeRegressor of sklearn.

        Args:
            min_samples_leaf (int): The minimal number of parametrization per end-leaf.
            *args, **kwargs: Various arguments that will be passed to the sklearn parent class.
        """
        # Initalize the parent class
        super().__init__(min_samples_leaf=min_samples_leaf, *args, **kwargs)
        # Save the X model the data is trained on
        self.fitted_X = None
        # Save the y model the data is trained on
        self.fitted_y = None

    def fit(self, X, y, sample_weight=None, check_input=True, X_idx_sorted=None):
        """
        Build a decision tree classifier from the training set (X, y). This method overrides the
        original sklearn .fit method, by saving the original training y data.

        Args:
            X (array-like): Array of shape (n_samples, n_features) which contains the training
                input samples. Internally, it will be converted to ``dtype=np.float32`` and if a sparse
                matrix is provided to a sparse ``csc_matrix``.
            y (array-like): Array of shape (n_samples,) which contains the target values as float.
            sample_weight (array-like, optional): Sample weights. If None, then samples are equally weighted. Splits
                that would create child nodes with net zero or negative weight are
                ignored while searching for a split in each node. Splits are also
                ignored if they would result in any single class carrying a
                negative weight in either child node.
                Defaults to None.
            check_input (bool, optional): Allow to bypass several input checking.
                Don't use this parameter unless you know what you do.
                Defaults to True.
            X_idx_sorted (array-like, optional): The indexes of the sorted training input samples.
                If many tree are grown on the same dataset, this allows the ordering to be
                cached between trees. If None, the data will be sorted here.
                Don't use this parameter unless you know what to do.
                Defaults to None.

        Returns:
            The fitted object
        """
        self.fitted_y = y
        self.fitted_X = X
        return super().fit(
            X=X,
            y=y,
            sample_weight=sample_weight,
            check_input=check_input,
            X_idx_sorted=X_idx_sorted,
        )

    def compute_leaf_stats(self):
        """
        For each leave, compute its standard error and its mean.
        """
        leaf_ids = self.apply(self.fitted_X.astype(np.float32))
        leaves = list()
        leaves_mean = list()
        leaves_std = list()
        for leaf_id in np.unique(leaf_ids):
            leaf = self.fitted_y[leaf_ids == leaf_id]
            leaves_std.append(np.std(leaf))
            leaves_mean.append(np.mean(leaf))
            leaves.append(leaf_id)
        return np.array(leaves), np.array(leaves_mean), np.array(leaves_std)

    def predict(self, X, return_std=False):
        """
        Predict regression target for X.
        The predicted regression target of an input sample is computed as the
        mean predicted regression targets of the trees in the forest. If the return_std value is
        set to True, the standard error of the prediction (i.e. the impurity of the node) is also
        returned.

        Args:
        X (array-like): The input samples. Internally, its dtype will be converted to
            ``dtype=np.float32``. If a sparse matrix is provided, it will be
            converted into a sparse ``csr_matrix``.
        return_std (bool, optional): Whether or not the standard error should be returned. Defaults
            to False.

        Returns:
        y_mean (array-like):  Array of shape (n_samples, ) that corresponds to the mean of
            data point in the node.
        y_std (array-like): Array of shape (n_samples,) that corresponds to the standard
            deviation of predictive distribution in the node.
            Only returned when return_std is True.
       """
        predicted_leaves = self.apply(X.astype(np.float32))
        leaves, leaves_mean, leaves_std = self.compute_leaf_stats()
        y_mean = list()
        y_std = list()
        for leaf_id in predicted_leaves:
            y_mean.append(leaves_mean[leaves == leaf_id][0])
            y_std.append(leaves_std[leaves == leaf_id][0])
        if return_std:
            return np.array(y_mean), np.array(y_std)
        return np.array(y_mean)


class CensoredGaussianProcesses(GaussianProcessRegressor):
    """
    This class implements Gaussian Process Regression for censored data, as inspired by
    "J. Schmee and G. J. Hahn. A simple method for regression analysis with censored data".
    It inherits from the class GaussianProcessRegressor, and override its fits method
    to treat censored (truncated) data differently.
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize an object of class CensoredGaussianProcesses.
        """
        # Initalize the parent class
        super().__init__(*args, **kwargs)

    def _fit_non_truncated(self, X, y, truncated):
        """Fit the model on the uncensored data, and return it fitted.

        Args:
            X (array-like): Array of shape (n_samples, n_features) which contains the training
                input samples. Internally, it will be converted to ``dtype=np.float32`` and if a sparse
                matrix is provided to a sparse ``csc_matrix``.
            y (array-like): Array of shape (n_samples,) which contains the target values as float.
            truncated (array-like of bool): Wether or not the data has been truncated and we are only
                observing its higher bounds.
        """
        untruncated_X = X[np.invert(truncated), :]
        untruncated_y = y[np.invert(truncated)]
        return super().fit(X=untruncated_X, y=untruncated_y)

    def _estimate_censored_data(self, X, truncated, model):
        """Given a matrix X and a truncated vector, uses the model to predict the data point.

        Args:
            X (array-like): Array of shape (n_samples, n_features) which contains the training
                input samples. Internally, it will be converted to ``dtype=np.float32`` and if a sparse
                matrix is provided to a sparse ``csc_matrix``.
            truncated (array-like of bool): Wether or not the data has been truncated and we are only
                observing its higher bounds.
            model (sklearn model): The model to use to output the predictions.
        """
        return model.predict(X[truncated, :], return_std=True)

    def _draw_censored_data(self, censored_data_estimates, lower_bounds):
        """Given the estimation of the censored_data at some data point, generate a sample
        of randomly drawn.

        Args:
            censored_data_estimates (tuple): A tuple containing the estimated mean and standard
                error of the sample.

        Returns:
            samples (np.array): A sample of data drawn from this distribution.
        """
        samples = list()
        mus = censored_data_estimates[0]
        sigmas = censored_data_estimates[1]
        for mu, sigma, lower_bound in zip(mus, sigmas, lower_bounds):
            samples.append(self._truncated_gaussian_sample(mu, sigma, lower_bound)[0])
        return np.array(samples).reshape(-1, 1)

    @staticmethod
    def _truncated_gaussian_sample(mu, sigma, lower_bound):
        """Returns samples from a truncated gaussian sample as defined in Bayesian Optimization With
        Censored Response Data (Frank Hutter, Holger Hoos, and Kevin Leyton-Brown).

        Args:
            mu (float): The mean of the distribution.
            sigma (positive float): The scale of the distribution.
            lower_bound (float): The lower bound value.
            n_samples (int): The number of samples

        Returns:
            float: the value of the density function at point x.
        """
        normed_lower_bound = (lower_bound - mu) / sigma
        return truncnorm.rvs(
            a=normed_lower_bound, b=np.Inf, loc=mu, scale=sigma, size=1
        )

    def fit(self, X, y, truncated):
        """Given a matrix, a target value, and a boolean vector indicating which observation has
        been truncated, fits the model on the data.
        The model fitting is as follow:
            - Fit the model on uncensored data
            - Obtain the estimation on the uncensored data
            - Draw the samples from an estimated random distribution
            - Refit the model using this estimation
            - Return the fitted model

        Args:
            X (array-like): Array of shape (n_samples, n_features) which contains the training
                input samples. Internally, it will be converted to ``dtype=np.float32`` and if a sparse
                matrix is provided to a sparse ``csc_matrix``.
            y (array-like): Array of shape (n_samples,) which contains the target values as float.
            truncated (array-like): Wether or not the data has been truncated and we are only
                observing its higher bounds.

        Returns:
            The fitted object
        """
        # Check that there is some truncated data
        # If there isn't, fit the model normally
        if sum(truncated) == 0:
            return super().fit(X=X, y=y)
        # Else:
        # Isolate the truncated data
        y_truncated = y[truncated]
        # Fit the model on uncensored/untruncated data
        fit_on_non_truncated = self._fit_non_truncated(X, y, truncated)
        # Obtain the estimation for the censored data
        censored_data_estimates = self._estimate_censored_data(
            X, truncated, fit_on_non_truncated
        )
        # Draw the data from a random law
        sampled_y = self._draw_censored_data(censored_data_estimates, y_truncated)
        # Refit the model on non-truncated + the estimated data and return
        print(sampled_y)
        print(y[truncated])
        y[truncated] = sampled_y
        return super().fit(X=X, y=y)


class MaternGaussianProcess(GaussianProcessRegressor):
    """
    Implementation of GPRs using Matern kernel.
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize an object of class CensoredGaussianProcesses.
        """
        # Initialize a matern kernel
        # kernel = 1.0 * Matern(length_scale=1.0, nu=1.5)
        # Initalize the parent class
        super().__init__(*args, **kwargs, normalize_y=True)


class NoisyGaussianProcesses:
    """
    This class implements Noisy Gaussian Processes
    """
