"""
This module implements surrogate modeling techniques for black-box optimization of a function.
"""

__copyright__ = """
Copyright (C) 2020 Bull S. A. S. - All rights reserved
Bull, Rue Jean Jaures, B.P.68, 78340, Les Clayes-sous-Bois, France
This is not Free or Open Source software.
Please contact Bull S. A. S. for details about its license.
"""
# Ignore unused argument kwargs
# pylint: disable=unused-argument
import numpy as np
from sklearn.preprocessing import StandardScaler
from bbo.heuristics.heuristics import Heuristic


class SurrogateModel(Heuristic):
    """
    Object that will perform the surrogate modeling.
    Inherits from the mother class Heuristic.
    """

    def __init__(self, regression_model, next_parameter_strategy, *args, **kwargs):
        """
        Initializes a Surrogate Model object, which needs two information: the regression or
        interpolation model for modeling the function and the acquisition strategy which samples
        the next point on the regressed function.

        Args:
            regression_model (class): the regression model to use.
                Compatible with any model that implements methods called .fit or .predict (
                typically anything included in the sklearn package).

            function: the strategy to use when selecting new parameters.
        """
        super(SurrogateModel, self).__init__(
            regression_model, next_parameter_strategy)
        # Save regression model argument
        # Checks for the fit + predict method of regression function

        self.regression_model = regression_model()
        if not hasattr(self.regression_model, "predict"):
            raise AttributeError("Regression model argument must have a method named `predict` "
                                 "defined.")
        if not hasattr(self.regression_model, "fit"):
            raise AttributeError("Regression model argument must have a method named `fit` "
                                 "defined.")

        # Save next parameter strategy
        self.next_parameter_strategy = next_parameter_strategy
        # Save parameter and fitness scaler as attributes
        self.parameter_scaler = StandardScaler()
        self.fitness_scaler = StandardScaler()

    @staticmethod
    def _build_prediction_function(fitted_regression_model, parameter_scaler):
        """
        Given a fitted regression model, returns a function that predicts the value at data point x
        for this model.

        Args:
            fitted_regression_model (object of class regression_model): A fitted object of class
                regression_model
            parameter_scaler (object of class Scaler): A fitted scaler to transform the parameter
                space.

        Returns:
            function: The function that can be used to predict the value of x.
        """
        # define the function
        def prediction_function(data_point, *args, **kwargs):
            x_arr = np.array(data_point)
            try:
                scaled_arr = parameter_scaler.transform(x_arr)
                return fitted_regression_model.predict(scaled_arr, *args, **kwargs)
            except ValueError:
                scaled_arr = parameter_scaler.transform(x_arr.reshape(1, -1))
                return fitted_regression_model.predict(scaled_arr, *args, **kwargs)
        # return it
        return prediction_function

    def regression_function(self, history):
        """
        Fits the regression or interpolation method on the history of the previous evaluations
        and returns the associated prediction function.

        Args:
            history (dict): the history of the optimization, i.e. the tested parameters and the
                associated value. Must be a dictionary of the form {"fitness": [---],
                "parameters": [---]}:

        Returns:
           function: the function to use for regression.
        """
        # take history and normalize it using standard scaler
        scaled_parameters = self.parameter_scaler.fit_transform(
            history["parameters"])
        scaled_fitness = self.fitness_scaler.fit_transform(
            history["fitness"].reshape(-1, 1))
        truncated = np.copy(history["truncated"])
        # perform regression and save resulting function as attribute
        # try to pass the truncated argument in order to deal with censored data
        try:
            self.regression_model.fit(
                X=scaled_parameters, y=scaled_fitness, truncated=truncated)
        # if not, fit the model without this parameter
        except TypeError:
            self.regression_model.fit(X=scaled_parameters, y=scaled_fitness)
        return self._build_prediction_function(self.regression_model, self.parameter_scaler)

    def choose_next_parameter(self, history, ranges, *args, **kwargs):
        """
        Choose the next parameter by using the function passed as argument for
        next_parameter_strategy and use it for acquisition.

        Args:
            history (dict): the history of the optimization, i.e. the tested parameters and the
                associated value. Must be a dictionary of the form {"fitness": [---],
                "parameters": [---]}
            ranges (numpy arrays of numpy array): the possible values of each parameter dimension.

        Returns:
            numpy array: The next parameter, i.e. the child born from the
                reproduction of the two parents.
        """
        # Build prediction function
        prediction_function = self.regression_function(history)
        # choose next parameter for this function using the strategy given as input
        new_parameter = self.next_parameter_strategy(prediction_function,
                                                     ranges=ranges,
                                                     previous_evaluations=self.fitness_scaler.transform(history["fitness"].reshape(-1, 1)))
        return new_parameter

    def evaluate_quality(self, history, *args, **kwargs):
        """
        Evaluates the quality of the regression model by returning the RMSE of the regression
        function on the already evaluated points. The model must have been already fitted in
        order to return a score.

        Args:
            history (dict): the history of the optimization, i.e. the tested parameters and the
                associated value. Must be a dictionary of the form {"fitness": [---],
                "parameters": [---]}

        Returns:
            RMSE (float): The value of the RMSE on the evaluated data points.
        """
        return self.regression_model.score(X=history["parameters"], y=history["fitness"])

    def summary(self, history):
        """
        Returns a summary of the optimization process of the surrogate model, by returning the
        final RMSE.
        """
        rmse = self.regression_model.score(X=history["parameters"], y=history[
            "fitness"])
        print(f"Final RMSE: {rmse}")

    def reset(self):
        """
        Resets the algorithm.
        """
