"""
This module contains the abstraction of a tunable HPC component. It must be implemented in order
to tune a component using the optimization engine. It provides three methods most common to setup HPC components:
- Submit a sbatch using set environment variables
- Edit a sbatch to add the wanted library and its parameters as a header
- Submit the sbatch along with a specified slurm plugin to activate the module

The name of the components and its parametrization must be indicated in a YAML file, befor instanciating the class.

Of course, a child class can add any wanted new methods specific to the tunable component.
"""
import os
# import pty
import subprocess
from shlex import split
from pathlib import Path
from collections import OrderedDict


from .component_model import TunableComponentsModel

# Save current environment as variable
ENV = os.environ.copy()

# TODO: Add custom components support


class TunableComponent:
    """
    Abstract class representing a tunable component.
    """

    def __init__(self, name: str, module_configuration: str, parameters: dict = dict()) -> None:
        """Creates a TunableComponent object, given its configuration file.

        Args:
            name (str): The name of the module to load from the configuration
            module_configuration (str): The path to the configuration file of the component,
                either as a YAML file or an URL.
            parameters (dict): The parameters to setup the component.
        """
        # Check if the configuration file is an URL and try loading
        if ("http://" or "https://") in str(module_configuration):
            possible_components = TunableComponentsModel.from_api(
                module_configuration).components
        # Else, check if it's a file
        else:
            # If it's a YAML
            if Path(module_configuration).suffix == ".yaml":
                # If it exists
                if Path(module_configuration).is_file():
                    possible_components = TunableComponentsModel.from_yaml(
                        module_configuration).components
                # If the file can't be found, raise an error
                else:
                    raise FileNotFoundError(
                        "Module configuration can't be found. Please make sure this file exist.")
            # If it's not a YAML, raise an error
            else:
                raise ValueError("File must have a YAML format.")

        try:
            self.description = possible_components[name]
        except KeyError:
            raise KeyError(f"There is no component with the name {name}. If you want to use it, \
                  add it to the configuration file. Current possible components are: \
                      {possible_components.keys()}")
        # Load the configuration of the component

        self.parameters_description = self.description.parameters
        # Extract the description of the parameters for the component
        self.parameters = self.sanitize_parameters(parameters)
        # Sanitize parameters, by checking their type and replacing them with their default value
        # if unspecified

        self.var_env = ENV
        # The dictionary containing the environment variables

        self.submitted_jobids = list()
        # List of the jobs that have been submitted using the accelerator

    @ property
    def cmd_line(self) -> str:
        """Collects all the parameters with a flag and a value and arrange them in order
        to build a command line that can be used to launch the component. If there is no
        command, returns an empty.

        Returns:
            str: the corresponding command line.
        """
        if not self.description.command:
            return ""
        else:
            cmd_line = ""
            # Iterate over each parameter
            for param, param_value in self.parameters_description.items():
                if param_value.cmd_var and self.parameters.get(param):
                    # If the string for the flag is bigger than 1, use --
                    if len(param_value.flag) > 1:
                        cmd_line += f" --{param_value.flag} {self.parameters.get(param)} "
                    else:
                        cmd_line += f" -{param_value.flag} {self.parameters.get(param)} "
            return self.description.command + " " + " ".join(cmd_line.split())

    def add_header_sbatch(self, sbatch_file: str) -> str:
        """Adds the header, the LD_PRELOAD and the command line corresponding to the component to the sbatch file.
        The header is added to the first line which doesn't start by #SBATCH.

        Args:
            sbatch_file (str): The path to the sbatch where the header should be added.

        Returns:
            str: the path to the newly created sbatch.
        """
        written = False
        copy_sbatch_path = f"{Path(sbatch_file).stem}_header.sbatch"
        copy_sbatch = open(copy_sbatch_path, "w")
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
                        # Add the header at the beginning of the script if exists
                        if self.description.header:
                            copy_sbatch.write(self.description.header + "\n")
                        # Add the ld preload at the beginning of the script if exists
                        if self.description.ld_preload:
                            copy_sbatch.write(
                                "LD_PRELOAD=" + self.description.ld_preload + "\n")
                        # Add the command line if exists
                        if self.cmd_line:
                            copy_sbatch.write(
                                self.cmd_line + "\n")
                        written = True
        copy_sbatch.close()
        return copy_sbatch_path

    def _build_sbatch_cmd_line(self, sbatch_file: str, wait: bool) -> str:
        """Builds the command line to submit an sbatch_file using the HPC component.
        This command line can be used in wait mode (hangs until the sbatch is finished).

        Args:
            sbatch_file (str): The path to the sbatch file to run.
            wait (bool, optional): Whether or not the process is blocking. Defaults to True.

        Returns:
            str: The command line to use as a string.
        """
        # If the wait option is enabled, use the --wait flag
        wait_flag = ""
        if wait:
            wait_flag = " --wait "

        # If there is a plugin, add -- to the plugin
        plugin = ""
        if self.description.plugin:
            plugin = f" --{self.description.plugin} "

        # Build the cmd line and strip double white spaces
        cmd_line = " ".join(
            f'sbatch{wait_flag}{plugin} {sbatch_file}'.split())
        return cmd_line

    def submit_sbatch(self, sbatch_file: str, wait: bool = True) -> int:
        """Submits the sbatch file contained at the path sbatch_file with the accelerator,
        by calling the setup method and then submitting the sbatch to the queue.
        If the accelerator has a header, a new sbatch with the header included is created as a
        copy.

        Args:
            sbatch_file (str): The path to the sbatch file to run.
            wait (bool, optional): Whether or not the process is blocking. Defaults to True.

        Returns:
            int: the ID of the submitted slurm job.
        """
        # Check that the file exists, else raise a file not found error
        if not Path(sbatch_file).exists():
            raise FileNotFoundError("Could not find sbatch")
        # Setup the component upon initialization
        self.setup_var_env()
        # Transform the sbatch file
        sbatch_file = self.add_header_sbatch(sbatch_file)
        # Build the command line for sbatch submission
        cmd_line = self._build_sbatch_cmd_line(sbatch_file, wait)
        # Run the script using subprocess
        master, slave = pty.openpty()
        sub_ps = subprocess.Popen(split(cmd_line),
                                  stdout=slave,
                                  stderr=slave,
                                  env=self.var_env)
        with os.fdopen(master, 'r') as stdout:
            try:
                # Get job id in second line if the submission has been a success
                job_id = int(stdout.readline().split()[-1])
                self.submitted_jobids.append(job_id)
            except ValueError:
                # Try again because Slurm acts weird with its output and skipping two lines
                # can do the trick
                job_id = int(stdout.readline().split()[-1])
                self.submitted_jobids.append(job_id)
            except ValueError:
                job_id = int(stdout.readline().split()[-1])
                self.submitted_jobids.append(job_id)
            # Else, raise an error
            except (IndexError, ValueError) as err_msg:
                raise Exception("Could not submit job.")

        # Wait until the process is over to get entire stdout and stderr
        sub_ps.wait()
        output_stdout, output_stderr = sub_ps.communicate()

        if sub_ps.returncode == 0:
            # If the slurm submission step is blocking (i.e. wait is enabled)
            # The sub_ps retuning a succes code means that the job was successfully run
            if wait:
                print("Successfully ran jobid %s", job_id)
            return job_id
        raise Exception(
            f"Could not run job {job_id}: \n stderr: {output_stderr}")

    def sanitize_parameters(self, parameters: dict) -> dict:
        """
        Get the parameter key argument in uppercase. Checks beforehand that the type of the
        parameter argument is correct (dictionary or ordered dictionary).
        Get the default values from the description file.

        Args:
             parameters (dict or OrderedDict): The raw parameters.

        Returns:
            dict: the dictionary of the parameters, the keys as uppercase.
        """
        # Check that the given parameters are a dict or an OrderedDict.
        if (not isinstance(parameters, dict)) \
                and (not isinstance(parameters, OrderedDict)):
            raise TypeError("Parameters must be dicts or ordered dicts")
        # From the description file, loads the parameter description associated with the
        # iomodules' name
        # Iterate over the description of the parameters
        for param, param_value in self.parameters_description.items():
            # Get the description of this parameter
            # Check if the parameter exist in the parameter argument
            if not parameters.get(param) and not param_value.optional:
                # If the parameter is not optional
                if param_value.default:
                    # Check if there is a default value for this parameter
                    # If the parameter is optional, do not take its value
                    parameters[param] = param_value.default
                else:
                    # If the parameter is not in the parameters, there is no value,
                    # and the parameter is not optional
                    # raise a ValueError
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
            if param_value.env_var and self.parameters.get(param):
                self.var_env[param] = self.parameters[param]
        # Make sure the environment variables are all strings:
        self.var_env = {k: str(v) for k, v in self.var_env.items()}
