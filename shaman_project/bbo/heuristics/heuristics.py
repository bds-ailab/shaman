"""
This module contains the Heuristic class is the mother class from which all of the heuristics will
inherit.
This helps ensure that all heuristics will respect the same properties.
The following methods are mandatory when adding a new heuristic, else a NotImplementedError will
be raised:
* choose_next_parameter: given the previous history, this method should return the next parameter
selected as most relevant for the heuristic.
* evaluate_quality: this method should return a or some values that can be used in order to judge
the quality of the algorithm.
* summary: this method should print a summary that is specific to the heuristic. This is useful when
printing the summary of the optimizer.
* draw: this method should graphically represent the behavior of the heuristic.
* reset: this method should "reset" the heuristic, by setting some of its attribute to zero,
so that the algorithm can be easily restarted.

In terms of attributes, this class only possess the stop attribute, which indicates whether or
not the heuristic should stop. This value can be switched during the algorithm flow in order to
stop it when a certain heuristic-specific stop criterion is matched.
"""

__copyright__ = """
Copyright (C) 2020 Bull S. A. S. - All rights reserved
Bull, Rue Jean Jaures, B.P.68, 78340, Les Clayes-sous-Bois, France
This is not Free or Open Source software.
Please contact Bull S. A. S. for details about its license.
"""
# Ignore unused argument kwargs
# pylint: disable=unused-argument


class Heuristic:
    """
    The Heuristic class is the mother class from which all of the heuristics will inherit.
    This helps ensure that all heuristics will respect the same properties.

    The following methods are mandatory when adding a new heuristic, else a NotImplementedError will
    be raised:
    * choose_next_parameter: given the previous history, this method should return the next
    parameter selected as most relevant for the heuristic.
    * evaluate_quality: this method should return a or some values that can be used in order to
    judge the quality of the algorithm.
    * summary: this method should print a summary that is specific to the heuristic. This is
    useful when printing the summary of the optimizer.
    * draw: this method should graphically represent the behavior of the heuristic.
    * reset: this method should "reset" the heuristic, by setting some of its attribute to zero,
    so that the algorithm can be easily restarted.

    In terms of attributes, this class only possess the stop attribute, which indicates whether or
    not the heuristic should stop. This value can be switched during the algorithm flow in order to
    stop it when a certain heuristic-specific stop criterion is matched.
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize an object of class Heuristic.

        Args:
            *args, **kwargs: Various arguments that are heuristic dependent.
        """
        # boolean in order to enforce an heuristic-specific stop criterion.
        self.stop = False

    def choose_next_parameter(self, history, *args, **kwargs):
        """
        Launches the heuristic that exploits the history of the already evaluated point in order
        to return the most relevant data points.

        Args:
            history (dict): A dictionary of the form {"fitness": [---], "parameters": [---]} that
                contains the previously sampled parameters and the associated fitness.
            ranges (numpy array of numpy arrays): the possible values of each parameter dimension.
            *args, **kwargs: Heuristic specific arguments.

        Returns:
            parameters (numpy array): the next parametrisation to evaluate.
        """
        raise NotImplementedError

    def summary(self, *args, **kwargs):
        """
        Prints a summary that is specific to the heuristic.
        This summary will be printed when the .summary method of the BBOptimizer is called in
        order to recapitulate the optimization process.

        Args:
            *args, **kwargs: Heuristic-specific arguments to compute the summary.

        Returns:
            None, prints out the result.
        """
        raise NotImplementedError

    def reset(self):
        """
        Resets the heuristic's attributes in order to be able to re-launch it with "clean"
        attributes.

        Returns:
            None, only modifies the attributes.
        """
        raise NotImplementedError
