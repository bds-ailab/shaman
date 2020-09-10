"""
This module parses the configuration file in order to:
    - Get the name of the varying parameters of the accelerator
    - Parse the arguments of the BBOptimizer
"""

__copyright__ = """
Copyright (C) 2019-2020 Bull S. A. S. - All rights reserved
Bull, Rue Jean Jaures, B.P.68, 78340, Les Clayes-sous-Bois, France
This is not Free or Open Source software.
Please contact Bull S. A. S. for details about its license.
"""

from configparser import ConfigParser
import re
import ast
import importlib
import numpy as np


class ShamanConfig:
    """
    The ShamanConfig class parses the configuration file of little SHAMan
    in order to:
        - Set up the BBOptimizer
        - Set up the accelerator
    """

    def __init__(self, configuration_file, accelerator_name):
        """Parses the configuration file.

        Args:
            configuration_file (str): The path to the configuration file.
            accelerator_name (str): The name of the accelerator to select
                the configuration for.
        """
        # Save the accelerator name
        self.accelerator_name = accelerator_name.upper()
        # Loads the configuration file
        self.config = ConfigParser()
        self.config.read(configuration_file)
        # Parses the parameters of the experiment
        self._parse_experiment_parameters()
        # Parses the parameters of the pruning strategy
        self._parse_pruning_parameters()
        # Parses the parameters of the accelerators
        self._parse_acc_parameters()
        # Parses the parameters of BBO
        self._parse_bbo_parameters()
        # Parses the noise reduction parameters
        self._parse_noise_reduction()
        # Parses the parameters of the mongo database
        self._parse_api_parameters()

    def _parse_experiment_parameters(self):
        """Parses the parameters associated with the experiment"""
        self.experiment_parameters = self.config["EXPERIMENT"]

    @property
    def with_ioi(self):
        """Returns whether or not all the runs for an experiment should be
        instrumented"""
        return ast.literal_eval(self.experiment_parameters["with_ioi"])

    @property
    def default_first(self):
        """Whether or not the first run should be a run with default parameters."""
        return ast.literal_eval(self.experiment_parameters["default_first"])

    def _parse_pruning_parameters(self):
        """Parses the parameters associated with the pruning strategy of the experiment.
        """
        try:
            self.pruning_parameters = self.config["PRUNING_STRATEGY"]
        except KeyError:
            self.pruning_parameters = dict()

    @property
    def pruning(self):
        """Whether or not the computations should happen asynchronously, in order to
        cancel jobs that take too long to run.
        """
        if self.pruning_parameters:
            return True
        return False

    @property
    def max_step_duration(self):
        """Set up the maximal duration for a run, it can either be a string 'default' (which means
        that parametrization that performs worse than the default value) or a value in second.
        """
        if self.pruning:
            max_step_duration = self.pruning_parameters["max_step_duration"]
            if max_step_duration == "default":
                if not self.default_first:
                    raise ValueError("The 'max_step_duration' value can't be set to default if the"
                                     "parameter default_first is set to False")
                return max_step_duration
            elif 'numpy.' in max_step_duration:
                try:
                    module_name = max_step_duration.split(".")
                    module = importlib.import_module(
                        ".".join(module_name[:-1]))
                    return getattr(module, module_name[-1])
                except:
                    raise ValueError(
                        "Specified function must be a numpy function.")
            else:
                try:
                    return int(max_step_duration)
                except ValueError:
                    raise ValueError("Maximum step duration should either be an integer, a numpy."
                                     "function or 'default'")
                raise ValueError(
                    "Possible string values are 'default' or a numpy function.")
        else:
            return None

    def _parse_bbo_parameters(self):
        """Parses the parameters associated with BBO."""
        self.bbo_parameters = self.config["BBO"]

    def _parse_noise_reduction(self):
        """Parses the noise reduction parameters, if there are any"""
        try:
            self.noise_reduction_parameters = self.config["NOISE_REDUCTION"]
        except KeyError:
            self.noise_reduction_parameters = dict()

    @property
    def bbo_kwargs(self):
        """Parses the kwargs corresponding to the BBOptimizer and the noise reduction dictionary"""
        bbo_kwargs = dict()
        bbo_parameters = self.bbo_parameters
        bbo_parameters.update(self.noise_reduction_parameters)
        for param, value in bbo_parameters.items():
            if ('bbo.' in value) or ('sklearn.' in value) or ('numpy.' in value):
                module_name = value.split(".")
                module = importlib.import_module(".".join(module_name[:-1]))
                bbo_kwargs[param] = getattr(module, module_name[-1])
            else:
                try:
                    bbo_kwargs[param] = ast.literal_eval(value)
                except ValueError:
                    bbo_kwargs[param] = value
        return bbo_kwargs

    def _parse_acc_parameters(self):
        """Parses the parameters of the accelerator"""
        self.accelerator_parameters = self.config[self.accelerator_name]

    @property
    def acc_parameter_names(self):
        """Returns the name of the parameters."""
        return list(self.accelerator_parameters.keys())

    @property
    def acc_parameter_space(self):
        """Returns the range of the parameters."""
        array_parameters = list()
        for parameter_range in self.accelerator_parameters.values():
            parameter_list = self.create_range(parameter_range)
            array_parameters.append(np.array(parameter_list))
        return np.array(array_parameters)

    @staticmethod
    def check_range_format(range_string):
        """
        Given a string, returns true if its format matches the {start, stop, step} format,
        with start, stop and step being integers.

        Args:
            range_string (str): The string whose format must be checked

        Returns:
            format_match (bool): Equals to true if the format match, false otherwise
        """
        # Use regex to match the format
        rex = re.compile(r"^{\d+, \d+, \d+}$")
        return rex.match(range_string)

    @staticmethod
    def create_range(range_string):
        """
        Given a string of format {start, stop, step}, returns a list containing all the values
        of the parameters. If the format is as a list of value (around []), list them.

        For example, create_range("{1, 5, 2}") will return [1, 3, 5] as a list.

        Args:
            range_string (str): The string describing the range to use

        Returns:
            list_range (list): The values in the range as a Python list
        """
        # If we're in the case of a range format:
        if ShamanConfig.check_range_format(range_string):
            # Get the values as strings
            values = re.findall(r'\d+', range_string)

            # For each value found, assert that it is an integer.
            for idx, value in enumerate(values):
                values[idx] = int(value)

            # Create the range
            list_range = list(range(values[0], values[1] + 1, values[2]))

            # Check that the range is not empty (i.e. the input values make sense)
            if list_range:
                return list_range
        raise ValueError("Range was wrongly specified."
                         "Please refer to the documentation.")

    def _parse_api_parameters(self):
        """Parses the parameters of the IOI backend"""
        self.api_parameters = self.config["API"]
