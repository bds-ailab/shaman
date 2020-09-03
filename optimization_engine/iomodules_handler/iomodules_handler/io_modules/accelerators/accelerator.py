"""
The goal of the Accelerator class is to provide an abstraction of accelerator handlers
and thus provides the methods that must be implemented when coding a new Python
accelerator handler.

It inherits from the abstract class IOModule.
"""

__copyright__ = """
Copyright (C) 2019-2020 Bull S. A. S. - All rights reserved
Bull, Rue Jean Jaures, B.P.68, 78340, Les Clayes-sous-Bois, France
This is not Free or Open Source software.
Please contact Bull S. A. S. for details about its license.
"""

from collections import OrderedDict
import logging
from iomodules_handler.io_modules.iomodule import IOModule
# from iomodules_handler import __DEFAULT_CONFIGURATION__
# TODO: deal with iomodules configuration
__DEFAULT_CONFIGURATION__ = ""


class Accelerator(IOModule):
    """
    Represents an accelerator (defined as an abstract interface) that
    inherits from the abstract class IOModule.

    This class provides methods to:
        - Read the configuration file of a given accelerator (load_parameter_description)

        - Sanitize the parameters by replacing by their default when required (sanitize_parameters)

        - Set up the environement variables by getting the values with a env_var flag in the
        configuration (setup_var_env)

        - Build a command line associated with the values in the configuration with a flag option
    """

    def __init__(self, parameters=None, module_configuration=__DEFAULT_CONFIGURATION__):
        """
        Creates an accelerator object.

        Args:
            parameters (dict): A Python dictionary containing the values of the parameters.
                The default value is an empty dictionary, which corresponds to using all
                the defaults of the accelerator.
            module_configuration (str, optional): The path to the configuration of the IOModule.
                It defaults to the file iomodules_config.yaml.

        Returns:
            An object of class Accelerator
        """
        super().__init__(module_configuration)
        # Inherit from the IOModule class
        self.parameters_description = self.load_parameter_description()
        # Load the description of the parameters for the accelerator

        # If set to None, set the parameters to be an empty dictionary
        if not parameters:
            parameters = dict()
        self.parameters = self.sanitize_parameters(parameters)
        # The value of the parameters, passed as uppercase

    @property
    def accelerator_name(self):
        """Returns the name of the accelerator"""
        return "abstract_accelerator"

    def load_parameter_description(self):
        """Loads the description of the parameters that corresponds to the accelerator_name."""
        return self.module_configuration[self.accelerator_name.upper()]

    def sanitize_parameters(self, parameters):
        """
        Get the parameter key argument in uppercase. Checks beforehand that the type of the
        parameter argument is correct (dictionary or ordered dictionary).
        Get the default values from the description file.

        Args:
             parameters (dict or OrderedDict): The raw parameters.

        Returns:
            parameters (dict): the dictionary of the parameters, the keys as uppercase.
        """
        # Check that the given parameters are a dict or an OrderedDict.
        if (not isinstance(parameters, dict)) \
                and (not isinstance(parameters, OrderedDict)):
            raise TypeError("Parameters must be dicts or ordered dicts")
        parameters = {key.upper(): value for key, value in parameters.items()}
        # From the description file, loads the parameter description associated with the
        # iomodules' name
        # Iterate over the description of the parameters
        for param, param_value in self.parameters_description.items():
            # Get the description of this parameter
            # Check if the parameter exist in the parameter argument
            if not parameters.get(param) and not param_value.get("optional"):
                # If the parameter is not optional
                if param_value.get("value"):
                    # Check if there is a default value for this parameter
                    # If the parameter is optional, do not take its value
                    logging.info("No value specified for param %s. "
                                 "Setting it to its value defined in the configuration"
                                 "%s", param, param_value.get("value"))
                    parameters[param] = param_value.get("value")
                else:
                    # If the parameter is not in the parameters, there is no value,
                    # and the parameter is not optional
                    # raise a ValueError
                    logging.info(
                        "No value for parameter %s. Aborting process.", param)
                    raise ValueError(f"No value for parameter {param}")
        return parameters

    def setup_var_env(self):
        """
        Sets up the environment variables needed for the execution of the accelerator.
        For each of the variable in the configuration file with a flag env_var set to True,
        matches the environment variable with the corresponding parameter.
        """
        # Iterate over each parameter
        for param, param_value in self.parameters_description.items():
            if param_value.get("env_var") and param_value.get("value"):
                self.var_env[param] = self.parameters[param]
        # Make sure the environment variables are all strings:
        self.var_env = {k: str(v) for k, v in self.var_env.items()}

    @property
    def cmdline(self):
        """Collects all the parameters with a flag and a value and arrange them in order
        to build a command line that can be used to launch the accelerator.

        Returns:
            The corresponding command line.
        """
        cmdline = ""
        # Iterate over each parameter
        for param, param_value in self.parameters_description.items():
            if param_value.get("flag") and self.parameters.get(param):
                # If the string for the flag is bigger than 1, use --
                if len(param_value["flag"]) > 1:
                    cmdline += f" --{param_value['flag']} {self.parameters.get(param)}"
                else:
                    cmdline += f" -{param_value['flag']} {self.parameters.get(param)}"
        return " ".join(cmdline.split())

    def kill(self):
        """
        Provides a way to kill the accelerator.
        By default, does nothing.
        """

    def setup(self):
        """
        Provides a way to setup the accelerator to run the sbatch.
        By default, only sets up the environment variables.
        """
        self.setup_var_env()
