"""
This class inherits from the mother class Accelerator in order to provide ways to manipulate
and launch jobs with the SRO accelerator provided in the Fast IO Libraries.
"""

__copyright__ = """
Copyright (C) 2019-2020 Bull S. A. S. - All rights reserved
Bull, Rue Jean Jaures, B.P.68, 78340, Les Clayes-sous-Bois, France
This is not Free or Open Source software.
Please contact Bull S. A. S. for details about its license.
"""

import logging

# from iomodules_handler.io_modules import __DEFAULT_CONFIGURATION__
from .accelerator import Accelerator
# TODO: deal with iomodules configuration
__DEFAULT_CONFIGURATION__ = ""


class SROAccelerator(Accelerator):
    """
    This class inherits from the Accelerator class. It provides a way to run a sbatch with the
    Fast IO libraries enabled.
    """

    def __init__(self, parameters=None, module_configuration=__DEFAULT_CONFIGURATION__):
        """
        Creates an handler that allows the set up of the SRO accelerator.

        Args:
            parameters (dict, optional): A Python dictionary containing the values of the
                parameters.
            module_configuration (str, optional): The path to the parameter desciption.
                Must be a YAML file.
                Defaults to the configuration file provided in the config/ folder and generated for
                the user upon the package install.

        Returns:
            An object of class Accelerator
        """
        super().__init__(parameters, module_configuration)
        # Inherits from the mother class Accelerator

        self.plugin = "fastio=yes"
        # The plugin value to use to run an sbatch using FIOL

        self.header = "clush -w $(hostname) -l root 'sync ; echo 3 > /proc/sys/vm/drop_caches'"
        # Cleans the cache of the compute nodes before execution

    @property
    def accelerator_name(self):
        """Returns the name of the accelerator"""
        return "fiol_accelerator"

    def setup(self):
        """
        Sets up the FIOL accelerator.
        As this accelerator only depends on the use of the plugins and the environment variables,
        setting it up is the same as setting up the environment.

        However, this method is necessary to respect the implementaiton rules
        of the accelerator interface and preserve clarity.
        """
        logging.info("Setup SRO with parameters %s", self.parameters)
        super().setup()

    def kill(self):
        """
        Implements the kill method of the parent class.
        Does nothing in the case of SRO as it only depends on environment variables.
        """
