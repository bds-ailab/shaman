# Copyright 2020 BULL SAS All rights reserved
"""This module implements surrogate modeling techniques for black-box
optimization of a function."""

# Ignore unused argument kwargs
import numpy as np
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from bbo.heuristics.heuristics import Heuristic


class SurrogateModel(Heuristic):
    """Object that will perform the surrogate modeling.

    Inherits from the mother class Heuristic.
    """

    def __init__(self, regression_model,
                 next_parameter_strategy, *args, **kwargs):
        """Initializes a Surrogate Model object, which needs two information:
        the regression or interpolation model for modeling the function and the
        acquisition strategy which samples the next point on the regressed
        function.

        Args:
            regression_model (class): the regression model to use.
                Compatible with any model that implements methods called
                .fit or .predict (typically anything included in the
                sklearn library).

            function: the strategy to use when selecting new parameters.
        """
        super(
            SurrogateModel,
            self).__init__(
            regression_model,
            next_parameter_strategy)
        # Save regression model argument
        # Checks for the fit + predict method of regression function

        self.regression_model = regression_model()
        if not hasattr(self.regression_model, "predict"):
            raise AttributeError(
                "Regression model argument must have a method named `predict`"
                "defined."
            )
        if not hasattr(self.regression_model, "fit"):
            raise AttributeError(
                "Regression model argument must have a method named `fit`"
                "defined."
            )

        # Save next parameter strategy
        self.next_parameter_strategy = next_parameter_strategy
        # Save parameter, fitness scaler
        self.parameter_scaler = StandardScaler()
        self.fitness_scaler = StandardScaler()
        # save hot encoder as attributes and index of categorical variables
        # TODO: not very efficient to create it at each round
        self.computed_ranges = False
        self.hot_encoder = None
        self.categorical_variables = None
        self.categorical_ranges = None

    def _build_prediction_function(self):
        """Given a fitted regression model, returns a function that predicts
        the value at data point x for this model.

        Args:
            fitted_regression_model (object of class regression_model):
                A fitted object of class regression_model

        Returns:
            function: The function that can be used to predict the value of x.
        """
        # define the function
        def prediction_function(data_point, *args, **kwargs):
            x_arr = self.hot_encode(data_point)
            try:
                scaled_arr = self.parameter_scaler.transform(x_arr)
                return self.regression_model.predict(
                    scaled_arr, *args, **kwargs)
            except ValueError:
                scaled_arr = self.parameter_scaler.transform(
                    x_arr.reshape(1, -1))
                return self.regression_model.predict(
                    scaled_arr, *args, **kwargs)

        # return it
        return prediction_function

    def get_categorical_ranges(self, ranges):
        """Compute the categorical ranges of an array.

        Args:
            ranges (numpy arrays of numpy array): the possible values of each
                parameter dimension.

        Returns:
            None, but save the hot encoder and the categorical range
                information into an attribute
        """
        # Check in the ranges if there are any categorical variable
        # And store them in the list categorical_ranges
        # As well as their indexes
        self.categorical_ranges = []
        self.categorical_index = []
        for range in ranges:
            # Check if the first value of the range is a string
            # If it is, the whole range is considered to be a categorical
            # variable
            # Because it is re-used for decoding, the categorical index is
            # saved
            if isinstance(range[0], str):
                self.categorical_ranges.append(range)
                self.categorical_index.append(True)
            else:
                self.categorical_index.append(False)
        self.computed_ranges = True

    def hot_encode(self, parameters_array):
        """
        Given a parameter array, returns an hot encoded value of it
        if it encounters any string value, treated as a categorical variable.

        Args:
            parameters_array (np.array): an array containing the tested
                parameters.

        Returns:
            np.array: the parameters array with the hot encoding when
                relevant.
        """
        # If there are any categorical variables
        if self.categorical_ranges:
            # Create a hot encoder on this array if it does not yet exist
            self.hot_encoder = OneHotEncoder(
                categories=self.categorical_ranges, sparse=False)
            # Transform parameter array using the hot encoder
            hot_encoded = self.hot_encoder.fit_transform(
                parameters_array[:, self.categorical_index])
            # Return a vstack concatenation of the data
            return np.hstack([parameters_array[:,
                                               np.invert(
                                                   self.categorical_index)],
                              hot_encoded])
        return parameters_array

    def regression_function(self, history, ranges):
        """Fits the regression or interpolation method on the history of the
        previous evaluations and returns the associated prediction function.

        Args:
            history (dict): the history of the optimization, i.e. the tested
                parameters and the associated value.
            ranges (numpy arrays of numpy array): the possible values of each
                parameter dimension.

        Returns:
           function: the function to use for regression.
        """
        # Check if the hot encoding has already been called
        if not self.computed_ranges:
            # Compute the ranges if not already done
            self.get_categorical_ranges(ranges)
        # take parameter array and transform it using the hot encoder
        parameters_array = self.hot_encode(history["parameters"])
        # take history and normalize it using standard scaler
        scaled_parameters = self.parameter_scaler.fit_transform(
            parameters_array)
        scaled_fitness = self.fitness_scaler.fit_transform(
            history["fitness"].reshape(-1, 1)
        )
        truncated = np.copy(history["truncated"])
        # perform regression and save resulting function as attribute
        # try to pass the truncated argument in order to deal with censored
        # data
        try:
            self.regression_model.fit(
                X=scaled_parameters, y=scaled_fitness, truncated=truncated
            )
        # if not, fit the model without this parameter
        except TypeError:
            self.regression_model.fit(X=scaled_parameters, y=scaled_fitness)
        return self._build_prediction_function()

    def choose_next_parameter(self, history, ranges, *args, **kwargs):
        """Choose the next parameter by using the function passed as argument
        for next_parameter_strategy and use it for acquisition.

        Args:
            history (dict): the history of the optimization, i.e. the tested
                parameters and the associated value.
            ranges (numpy arrays of numpy array): the possible values of each
                parameter dimension.

        Returns:
            numpy array: The next parameter, i.e. the child born from the
                reproduction of the two parents.
        """
        # Build prediction function
        prediction_function = self.regression_function(history, ranges)
        # choose next parameter for this function using the strategy given as
        # input
        new_parameter = self.next_parameter_strategy(
            prediction_function,
            ranges=ranges,
            previous_evaluations=self.fitness_scaler.transform(
                history["fitness"].reshape(-1, 1)
            ),
        )
        return new_parameter

    def evaluate_quality(self, history, *args, **kwargs):
        """Evaluates the quality of the regression model by returning the RMSE
        of the regression function on the already evaluated points. The model
        must have been already fitted in order to return a score.

        Args:
            history (dict): the history of the optimization, i.e. the tested
                parameters and the associated value.

        Returns:
            RMSE (float): The value of the RMSE on the evaluated data points.
        """
        return self.regression_model.score(
            X=history["parameters"], y=history["fitness"]
        )

    def summary(self, history):
        """Returns a summary of the optimization process of the surrogate
        model, by returning the final RMSE."""
        rmse = self.regression_model.score(
            X=history["parameters"], y=history["fitness"]
        )
        print(f"Final RMSE: {rmse}")

    def reset(self):
        """Resets the algorithm."""
