"""
The goal of the IOModule class is to provide an abstract interface for IOModules,
which is defined as a software developed by the Data Management team and which
can be enabled when running a sbatch.
Because of the many differences between accelerators, this class has been designed to
be flexible and to take account all the different possibilities for io modules.
"""

__copyright__ = """
Copyright (C) 2019-2020 Bull S. A. S. - All rights reserved
Bull, Rue Jean Jaures, B.P.68, 78340, Les Clayes-sous-Bois, France
This is not Free or Open Source software.
Please contact Bull S. A. S. for details about its license.
"""
# pylint: disable=no-member

import os
import logging
import sys
import subprocess
from threading import Thread
import pty

from time import sleep
from shlex import split
import yaml

ENV = os.environ.copy()


class IOModule:
    """
    An abstract class which represents a IOModule, which is any software
    developed by the Data Management team.
    It is defined by (optionally):
        - Its configuration as a YAML file
        - Its slurm plugin
        - Its LD_PRELOAD
        - Its environment variables to work properly
        - Its header to add to the sbatch file.

    In terms of method, an IOModule must implement a setup() method which performs
    the steps required to get the module ready for usage.

    The main functionality of this module is to provide a submit_sbatch method,
    which runs a sbatch with the IOModule enabled.
    """

    def __init__(self, module_configuration):
        """
        Creates an IO Module object given its configuration file.

        Args:
            module_configuration (String): The configuration of the IO module.

        Returns:
            An object of class IOModule
        """
        # Check if the configuration file exists
        if not os.path.exists(module_configuration):
            print(module_configuration)
            raise FileNotFoundError(
                "Module configuration can't be found. Please make sure this file exist, else use the default.")
        self.module_configuration = self.get_configuration(
            module_configuration)
        # Where the parameter description is stored

        self.plugin = ""
        # The name of the plugin to use

        self.ld_preload = ""
        # Libraries that should be preloaded to run the accelerator

        self.var_env = ENV
        # The dictionary containing the environment variables

        self.header = ""
        # The header to add to the sbatch file

        self.submitted_jobids = list()
        # List of the jobs that have been submitted using the accelerator

    @staticmethod
    def get_configuration(configuration_file):
        """
        Loads the file containing the description of the parameters as a YAML and stores it in the
        attribute configuration.

        Args:
            configuration_file (str): The path to the configuration file.

        Returns:
            The description of the parameters as a dictionary
        """
        # Load the description file
        with open(configuration_file, "rb") as file:
            configuration = yaml.load(file, Loader=yaml.SafeLoader)
        return configuration

    def add_header_sbatch(self, sbatch_file):
        """Adds the header corresponding to the IOModule to the sbatch file.
        The header is added to the first line which doesn't start by #SBATCH.

        Args:
            sbatch_file (str): The path to the sbatch where the header should be added.

        Returns:
            The path to the newly created sbatch.
        """
        written = False
        header = self.header
        copy_sbatch = open(
            f"{os.path.splitext(sbatch_file)[0]}_header.sbatch", "w")
        with open(sbatch_file, "r") as read_file:
            # For each line in the original sbatch
            lines = read_file.readlines()
            for enum, line in enumerate(lines):
                # Write the current line and break
                copy_sbatch.write(line)
                # If the line starts with # and not at the end of file
                if line.startswith('#') and enum < len(line) - 2 and not written:
                    following_line = lines[enum + 1]
                    # And not the following one
                    if not following_line.startswith("#"):
                        # Add the header at the beginning of the script and break
                        copy_sbatch.write(header + "\n")
                        written = True
        copy_sbatch.close()
        return f"{os.path.splitext(sbatch_file)[0]}_header.sbatch"

    def _build_cmd_line(self, sbatch_file, wait, instrumented):
        """Builds the command line to submit an sbatch_file using the IO module.
        This command line can be used in wait mode (hangs until the sbatch is finished).
        The ioi plugin can also be added to it in order to collect the IO traces made by the
        sbatch.

        Args:
            sbatch_file (str): The path to the sbatch file to run.
            wait (bool, optional): Whether or not the process is blocking. Defaults to True.
            instrumented (bool, optional): Whether or not the process should be instrumented.
                Defaults to False.

        Returns:
            The command line to use as a string.
        """
        # If the wait option is enabled, use the --wait flag
        wait_flag = ""
        if wait:
            wait_flag = " --wait "

        # If the instrumentation is enabled, instrument the run
        instrument_flag = ""
        if instrumented:
            instrument_flag = " --ioinstrumentation=yes "

        # If there is a plugin, add -- to the plugin
        plugin = ""
        if self.plugin:
            plugin = f" --{self.plugin} "

        # Build the cmd line and strip double white spaces
        cmd_line = " ".join(
            f'sbatch{wait_flag}{instrument_flag}{plugin} {sbatch_file}'.split())
        return cmd_line

    def setup(self):
        """
        Sets up the IOModule using the parameter passed as __init__ arguments.
        Once this method is run, the accelerator should be enabled and any sbatch run with the
        right environment variables should be using the accelerator.
        """

    def submit_sbatch(self, sbatch_file, wait=True, instrumented=False, verbose=False):
        """Submits the sbatch file contained at the path sbatch_file with the accelerator,
        by calling the setup method and then submitting the sbatch to the queue.
        If the accelerator has a header, a new sbatch with the header included is created as a
        copy.

        Args:
            sbatch_file (str): The path to the sbatch file to run.
            wait (bool, optional): Whether or not the process is blocking. Defaults to True.
            instrumented (bool, optional): Whether or not the process should be instrumented.
                Defaults to False.
            verbose (bool, optional): Whether or not the output of the submission should be
                returned by the function. Defaults to False.                

        Returns:
            The ID of the submitted slurm job.
        """
        self.setup()
        # Setup the module upon initialization

        # If the accelerator has a header, add it to the file
        if self.header:
            sbatch_file = self.add_header_sbatch(sbatch_file)
        cmd_line = self._build_cmd_line(sbatch_file, wait, instrumented)
        logging.info("Submitting %s to shell", sbatch_file)
        # Run the script using subprocess
        master, slave = pty.openpty()
        sub_ps = subprocess.Popen(split(cmd_line),
                                  stdout=slave,
                                  stderr=slave,
                                  env=self.var_env)

        with os.fdopen(master) as stdout:
            # Skip first empty line
            _ = stdout.readline()
            try:
                # Get job id in second line if the submission has been a success
                job_id = int(stdout.readline().split()[-1])
                self.submitted_jobids.append(job_id)
            except ValueError:
                # Try again because Slurm acts weird with its output and skipping two lines
                # can do the trick
                job_id = int(stdout.readline().split()[-1])
                self.submitted_jobids.append(job_id)
            # Else, raise an error
            except (IndexError, ValueError) as err_msg:
                logging.error("Could not submit job. Aborting.")
                raise Exception("Could not submit job.")

        # Wait until the process is over to get entire stdout and stderr
        sub_ps.wait()
        output_stdout, output_stderr = sub_ps.communicate()

        if sub_ps.returncode == 0:
            if verbose:
                return output_stderr, output_stdout
            # If the slurm submission step is blocking (i.e. wait is enabled)
            # The sub_ps retuning a succes code means that the job was successfully run
            if wait:
                logging.info("Successfully ran jobid %s", job_id)
            return job_id
        logging.error("Job didn't run properly. Aborting.")
        raise Exception(
            f"Could not run job {job_id}: \n stderr: {output_stderr}")
