"""
This class inherits from the mother class Accelerator in order to provide ways to manipulate
and launch jobs with the Smart Burst Buffer developed by Atos Data Management via the workload
manager slurm.
"""

__copyright__ = """
Copyright (C) 2019-2020 Bull S. A. S. - All rights reserved
Bull, Rue Jean Jaures, B.P.68, 78340, Les Clayes-sous-Bois, France
This is not Free or Open Source software.
Please contact Bull S. A. S. for details about its license.
"""

import logging

from iomodules_handler.io_modules import __DEFAULT_CONFIGURATION__
from .accelerator import Accelerator


class SBBSlurmAccelerator(Accelerator):
    """
    This class inherits from the Accelerator class. It provides a way to run a sbatch with the Smart
    Burst Buffer via its slurm plugin.
    """

    def __init__(self, parameters=None, module_configuration=__DEFAULT_CONFIGURATION__):
        """
        Creates an handler that allows the set up of the SBB accelerator.

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
        # Inherits from the mother metaclass Accelerator

        self.header = self.build_header()
        # Builds the header

    def build_header(self):
        """Builds the header to add to the top of the sbatch in order to run an sbatch with the SBB.
        """
        # Set up environment variables
        super().setup()
        header = "#SBB "
        for parameter, value in self.parameters.items():
            # Except for environment variables
            if parameter not in self.var_env.keys():
                header += f"{parameter.lower()}={value} "
        return header.strip()

    @property
    def accelerator_name(self):
        """Returns the name of the accelerator"""
        return "sbb_slurm_accelerator"

    def setup(self):
        """
        Sets up the SBB accelerator with Slurm.
        As nothing is required but adding the header at the top of the file (which is done by the
        IOModule), this method does nothing but log the action of setting up the SBB.
        """
        logging.info("Setup SBB with parameters %s", self.parameters)
        super().setup()

    def kill(self):
        """
        Implements the kill method of the parent class.
        Does nothing in the case of SBB as it only depends on Slurm.
        """
