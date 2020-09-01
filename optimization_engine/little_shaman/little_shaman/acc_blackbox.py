"""
The goal of this class is to provide an object which returns the execution time associated with each
parametrization and is compatible with the BBO standards by having a compute method.
"""

__copyright__ = """
Copyright (C) 2019-2020 Bull S. A. S. - All rights reserved
Bull, Rue Jean Jaures, B.P.68, 78340, Les Clayes-sous-Bois, France
This is not Free or Open Source software.
Please contact Bull S. A. S. for details about its license.
"""

import os
import re
from shutil import copyfile
import subprocess
from shlex import split
from iomodules_handler.io_modules import SBBSlurmAccelerator, SROAccelerator,\
    __DEFAULT_CONFIGURATION__ as IOMODULES_CONFIGURATION


# TODO: add manual SBB support
__ACCELERATORS__ = {"fiol": SROAccelerator,
                    "sbb_slurm": SBBSlurmAccelerator}


class AccBlackBox:
    """
    Given an instance of a class Accelerator (from the iomodules_handler library) and
    a sbatch file, builds a "black-box" which is suitable for use with BBO.
    """

    def __init__(self, accelerator_name, parameter_names, sbatch_file,
                 instrumented=False,
                 acc_configuration_file=IOMODULES_CONFIGURATION,
                 sbatch_dir=os.getcwd()):
        """Creates an object of class AccBlackBox, with the accelerator accelerator_name
        and the file sbatch_file.

        Args:
            accelerator_name (str): The name of the accelerator.
            parameter_names (list of str): The name of the parameters that will be tested.
            acc_configuration_file (str): The path to the configuration of the accelerators
                (in the sense of iomodules-handler).
            sbatch_file (str): The path to the sbatch file to launch.
            instrumented (bool): Whether or not the experiment should be monitored using the
                IO Instrumentation monitoring tool.
            sbatch_dir (str): The path to the directory where the sbatch file is generated.
        """
        self.accelerator_name = accelerator_name
        self.parameter_names = parameter_names
        self.acc_configuration_file = acc_configuration_file
        self.sbatch_dir = sbatch_dir
        self.accelerator = __ACCELERATORS__[self.accelerator_name.lower()]
        self.sbatch_file = self.copy_sbatch(sbatch_file)
        self.instrumented = instrumented
        # The list of jobids that have been run through the blackbox
        self.jobids = list()
        # Attributes concerning the default run
        # The jobid of the run using default parameters
        self.default_jobid = None
        # The execution time of the run using default parameters
        self.default_execution_time = None
        # The default paremeters
        self.default_parameters = None
        # The accelerator setup with the current parameters
        # Is initialized to be setup with the default parameters
        self.acc_setup = self.accelerator(
            module_configuration=self.acc_configuration_file)

    def copy_sbatch(self, sbatch_file):
        """This method copies the sbatch in order to transform it into a timed
        sbatch which can be used by little-shaman.
        This sbatch file will be stored in the same folder as the sbatch
        submitted to the command line.

        Args:
            sbatch_file (str): The path to the sbatch file.

        Returns:
            The path to the newly created sbatch.
        """
        # Flag indicating if a time command has been written
        timed_written = False
        direct_copy = False
        os.makedirs(self.sbatch_dir, exist_ok=True)
        sbatch_file_name = os.path.basename(sbatch_file)
        new_path = os.path.join(self.sbatch_dir,
                                f"{os.path.splitext(sbatch_file_name)[0]}_shaman.sbatch")
        copy_sbatch = open(new_path, "w")
        # Check if file is already timed
        with open(sbatch_file, "r") as read_file:
            lines = read_file.readlines()
            print("Writing new file")
            # For each line in the original sbatch
            for enum, line in enumerate(lines):
                # If the line is timed already, break by copying the file
                if line.startswith("time"):
                    print("File is already timed, escaping")
                    direct_copy = True
                    break
                # Write the current line and break
                copy_sbatch.write(line)
                # If the line starts with # and not at the end of file
                if line.startswith('#') and enum < len(lines) - 1:
                    following_line = lines[enum + 1]
                    # And not the following one and the time command has not
                    # yet been written
                    if not following_line.startswith("#") and not timed_written:
                        copy_sbatch.write("time (" + "\n")
                        # Set time written to true
                        timed_written = True
                        print("Wrote time in file")
            if direct_copy:
                # Leave the started file and directly copy the original timed file
                copy_sbatch.close()
                copyfile(sbatch_file, new_path)
            else:
                # Close parenthesis and file
                copy_sbatch.write(")")
                copy_sbatch.close()
            return new_path

    def compute(self, parameters):
        """Given a set of accelerators parameter, submits the sbatch using
        these parameters.

        Args:
            parameters (np.array): The parameters to use the accelerator with.

        Returns:
            The time spent to run the sbatch.
        """
        # Build the dictionary that will contain the parameters
        parameter_dict = dict(zip(self.parameter_names, parameters))
        # Log the output
        print(
            f"Launching {self.accelerator_name} black-box with parametrization {parameter_dict}")
        # Setup the accelerator with the parameters
        self.acc_setup = self.accelerator(
            parameter_dict, module_configuration=self.acc_configuration_file)
        # Submit the sbatch using the accelerator
        job_id = self.acc_setup.submit_sbatch(
            self.sbatch_file, wait=True, instrumented=self.instrumented)
        # Add the ran jobid to the list of jobids
        self.jobids.append(job_id)
        execution_time = float(self._parse_slurm_times(os.path.join(os.getcwd(),
                                                                    f"slurm-{job_id}.out")))
        print(f"Application elapsed time: {execution_time}")
        return execution_time

    def run_default(self):
        """Launch the black-box with the default parameters, as specified in the IOModules
        configuration file.
        """
        # Log the output
        print(
            f"Launching {self.accelerator_name} black-box with default parametrization")
        # Submit the sbatch using the accelerator
        job_id = self.acc_setup.submit_sbatch(
            self.sbatch_file, wait=True, instrumented=self.instrumented)
        # Store the id of the default job
        self.default_jobid = job_id
        # Store the default parameters
        self.default_parameters = self.acc_setup.parameters
        execution_time = float(self._parse_slurm_times(os.path.join(os.getcwd(),
                                                                    f"slurm-{job_id}.out")))
        print(f"Default application elapsed time: {execution_time}")
        self.default_execution_time = execution_time
        return execution_time

    @property
    def slurm_config(self):
        """
        Returns the path to the file to use for the Slurm configuration.
        """
        acc = self.accelerator(
            module_configuration=self.acc_configuration_file)
        return acc.var_env["SLURM_CONF"]

    def step_cost_function(self):
        """
        Defines a custom cost function in order to be able to use BBO asynchronously. It computes
        the slurm running time of the currently running job (i.e. the last element of
        the currently running jobid).
        """
        return self.parse_job_elapsed_time(self.acc_setup.submitted_jobids[-1], self.slurm_config)

    def on_interrupt(self):
        """
        If the .compute method of the black-box is called, scancel the last job.
        """
        self.scancel_job(
            self.acc_setup.submitted_jobids[-1], self.slurm_config)

    def _parse_slurm_times(self, out_file):
        """Parses the slurm times associated with the file slurm-job_id.out

        Args:
            out_file (str): The job slurm output file path to parse.

        Returns:
            The time real value
        """
        real_time = None
        try:
            with open(out_file, "r") as file:
                lines = file.readlines()
                for line in lines:
                    if line.startswith("real"):
                        time = re.split('\t', line)[-1].strip()
                        real_time = self.parse_milliseconds(time)
            if real_time:
                return real_time
            raise ValueError(f"Slurm command was not timed !")
        except FileNotFoundError:
            raise FileNotFoundError("Slurm output was not generated.")

    @staticmethod
    def parse_milliseconds(string_time):
        """
        Given a string date with the format MMmSS.MSs (as returned by the linux time command),
        parses it to seconds.

        Args:
            string_time (str): The date to parse

        Returns:
            The number of elapsed seconds
        """
        minutes = int(string_time.split("m")[0])
        string_time = string_time.replace(str(minutes)+"m", "")
        seconds = int(string_time.split(".")[0])
        milliseconds_string = string_time.split(".")[1]
        milliseconds_string = milliseconds_string.replace("s", "")
        milliseconds = int(milliseconds_string)
        return minutes * 60 + seconds + milliseconds / 1000

    @staticmethod
    def parse_job_elapsed_time(job_id, slurm_conf):
        """
        Given a Slurm jobid, parses the output of the squeue command for this job in order to
        return the running time.

        Args:
            job_id (int): The slurm ID of the job.

        Returns:
            float: The time the job has been running.
        """
        sub_ps = subprocess.run(split(f"squeue -j {job_id}"),
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                env=dict(os.environ, SLURM_CONF=slurm_conf))
        output_stdout = sub_ps.stdout.decode()
        if output_stdout:
            try:
                # Try to parse the output of the squeue command
                # If it returns a ValueError, it means that the job is already over
                # Set the resulting time to 0
                raw_time = sub_ps.stdout.decode().split(" ")[-8].split(":")
                time_in_second = int(raw_time[0]) * 60 + int(raw_time[1])
                return time_in_second
            except ValueError:
                return 0
        return 0

    @staticmethod
    def scancel_job(job_id, slurm_conf):
        """Call scancel on the job job_id.

        Args:
            job_id ([type]): [description]
        """
        sub_ps = subprocess.run(split(f"scancel {job_id}"),
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                env=dict(os.environ, SLURM_CONF=slurm_conf))
        if sub_ps.returncode == 0:
            print(f"Successfully cancelled {job_id}")
        else:
            print(f"Could not stop {job_id}")
