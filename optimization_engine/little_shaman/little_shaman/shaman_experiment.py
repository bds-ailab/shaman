"""The class ShamanExperiment is a tool to launch, monitor and save optimization
experiments.
"""

__copyright__ = """
Copyright (C) 2019 Bull S. A. S. - All rights reserved
Bull, Rue Jean Jaures, B.P.68, 78340, Les Clayes-sous-Bois, France
This is not Free or Open Source software.
Please contact Bull S. A. S. for details about its license.
"""

import datetime
import sys
import os
import numpy as np
from httpx import Client
from bbo.optimizer import BBOptimizer

from little_shaman import __DEFAULT_CONFIGURATION__ as SHAMAN_CONFIGURATION
from little_shaman import __CURRENT_DIR__
from little_shaman.acc_blackbox import AccBlackBox
from little_shaman.configuration_parser import ShamanConfig


class ShamanExperiment:
    """This class represents an optimization experiment. It allows to
    plan, launch and store the information corresponding to an experiment."""

    def __init__(self,
                 accelerator_name,
                 nbr_iteration,
                 sbatch_file,
                 experiment_name,
                 sbatch_dir=None,
                 slurm_dir=None,
                 result_file=None,
                 configuration_file=SHAMAN_CONFIGURATION):
        """Builds an object of class ShamanExperiment.
        This experiment is defined by giving:
            - The name of the accelerator to use.
            - The number of iterations the optimization should happen.
            - The name of the sbatch file to run.
            - The name of the experiment.
            - Where the slurm outputs should be stored (optional, if not specified,
                the outputs are deleted)
            - The path to the result file (optional, if not specified, no file is created).
            - A configuration file to setup the experiment.

        Args:
            accelerator_name (str): The name of the accelerator to use.
            nbr_iteration (int): The number of iterations.
            sbatch_file (str): The path to the sbatch file.
            experiment_name (str): The name of the experiment.
            sbatch_dir (str): The working directory, where the shaman sbatch will be stored.
                If not specified, the directory where the command is called.
            slurm_dir (str): The directory where the slurm outptus will be stored.
                If set to None, all the slurm outputs are removed after the end of the experiment.
            result_file (str): The path to the result file.
                If set to None, no such file is created and the results are printed to the screen.
            configuration_file (str): The path to the configuration file.
                Defaults to the configuration file present in the package and called
                config.cfg.
        """
        # Assert that the accelerator is equal to FIOL or SBB_SLURM
        assert accelerator_name.upper() in [
            "FIOL", "SBB_SLURM"], "Unknown accelerator name."
        self.accelerator_name = accelerator_name
        self.nbr_iteration = nbr_iteration
        self.sbatch_file = sbatch_file
        # Assert that the file exist
        if not os.path.exists(self.sbatch_file):
            raise FileNotFoundError("Requested sbatch does not exist.")
        self.experiment_name = experiment_name
        self.sbatch_dir = sbatch_dir if sbatch_dir else __CURRENT_DIR__
        self.slurm_dir = slurm_dir if slurm_dir else __CURRENT_DIR__
        self.result_file = result_file
        self.configuration = ShamanConfig(
            configuration_file, self.accelerator_name)
        self.api_client = Client(base_url=self.api_url, proxies={})
        # Compute the start of the experiment
        self.experiment_start = datetime.datetime.utcnow().strftime("%y/%m/%d %H:%M:%S")
        # Create the black box object
        self.acc_black_box = AccBlackBox(self.accelerator_name,
                                         self.configuration.acc_parameter_names,
                                         self.sbatch_file,
                                         instrumented=self.configuration.with_ioi,
                                         sbatch_dir=self.sbatch_dir)
        self.bb_optimizer = self.setup_bb_optimizer()
        self.experiment_id = ""

    def setup_bb_optimizer(self):
        """
        Setups the black-box from the configuration.
        """
        # Create the BBOptimizer object using the different options in the
        # configuration
        max_step_cost = self.configuration.max_step_duration
        if self.configuration.max_step_duration == "default":
            max_step_cost = self.acc_black_box.default_execution_time
        self.bb_optimizer = BBOptimizer(black_box=self.acc_black_box,
                                        parameter_space=self.configuration.acc_parameter_space,
                                        max_iteration=self.nbr_iteration,
                                        async_optim=self.configuration.pruning,
                                        max_step_cost=max_step_cost,
                                        **self.configuration.bbo_kwargs)
        return self.bb_optimizer

    def launch(self):
        """Launches the accelerator experiment"""
        # Create the experiment through API request
        self.create_experiment()
        if self.configuration.default_first:
            # Launch a run using default parameterization of the accelerator
            self.acc_black_box.run_default()
        # Setup the optimizer
        self.setup_bb_optimizer()
        # Launch the optimization
        self.bb_optimizer.optimize(callbacks=[self.update_history])
        # Summarize the optimization
        # If there is a result file, write the output in it
        if self.result_file:
            print("Writing to result file")
            orig_stdout = sys.stdout
            file_ = open(self.result_file, 'w')
            sys.stdout = file_
            self.summarize()
            sys.stdout = orig_stdout
            file_.close()
        self.summarize()

    def clean(self):
        """Cleans the experiment by removing the sbatch generated by Shaman.
        If there is no value specified for the slurm outputs folder, removes them."""
        for file_ in os.listdir(__CURRENT_DIR__):
            if file_.startswith("slurm") and file_.endswith(".out"):
                file_path = os.path.join(__CURRENT_DIR__, file_)
                if self.slurm_dir != __CURRENT_DIR__:
                    # Create if it doesn't already exist the folder
                    os.makedirs(self.slurm_dir, exist_ok=True)
                    # Move the output
                    os.rename(file_path, os.path.join(self.slurm_dir, file_))
                else:
                    # Remove the output
                    os.remove(file_path)
        # Clean up the sbatch file in the current dir where the experiment runs
        # Else keep it
        if self.sbatch_dir == __CURRENT_DIR__:
            for file_ in os.listdir(self.sbatch_dir):
                if "_shaman" in file_ and file_.endswith("sbatch"):
                    # Remove the sbatch files created by shaman
                    os.remove(os.path.join(self.sbatch_dir, file_))

    @property
    def api_url(self):
        """Build the URL to the API using the data in the configuration file.
        """
        return f"http://{self.configuration.api_parameters['host']}:{self.configuration.api_parameters['port']}"

    def create_experiment(self):
        """Create the experiment upon initialization.
        """
        dict_ = {"experiment_name": self.experiment_name, "experiment_start": self.experiment_start, "experiment_budget": self.nbr_iteration, "accelerator": self.accelerator_name,
                 "experiment_parameters": dict(self.configuration.bbo_parameters), "noise_reduction_strategy": dict(self.configuration.noise_reduction_parameters), "pruning_strategy": {"pruning_strategy": self.configuration.pruning}, "sbatch": open(self.sbatch_file, "r").read()}
        request = self.api_client.post("experiments", json=dict_)
        if not 200 <= request.status_code < 400:
            raise Exception(
                f"Could not create experiment with status code {request.status_code}")
        self.experiment_id = request.json()["id"]

    def update_history(self, history):
        """Update the optimization history at each BBO step and force conversion from numpy types.
        """
        dict_ = {
            "jobids": self.acc_black_box.acc_setup.submitted_jobids[-1]}
        dict_.update({"execution_time": history["fitness"][-1], "parameters": self.build_parameter_dict(self.configuration.acc_parameter_names, history["parameters"].tolist(
        ))[-1], "truncated": bool(history["truncated"][-1]), "resampled": bool(history["resampled"][-1]), "initialization": bool(history["initialization"][-1])})
        request = self.api_client.put(
            f"experiments/{self.experiment_id}/update", json=dict_)
        if not 200 <= request.status_code < 400:
            self.fail()
            raise Exception(
                f"Could not finish experiment with status code {request.status_code}")

    def end(self):
        """End the experiment once it is over.
        """
        dict_ = {
            "averaged_execution_time": self.bb_optimizer.averaged_fitness,
            "min_execution_time": self.bb_optimizer.min_fitness,
            "max_execution_time": self.bb_optimizer.max_fitness,
            "std_execution_time": self.bb_optimizer.measured_noise,
            "resampled_nbr": self.bb_optimizer.resampled_nbr,
            "improvement_default": float(round((self.acc_black_box.default_execution_time -
                                                self.bb_optimizer.best_fitness) /
                                               self.acc_black_box.default_execution_time, 2)*100),
            "elapsed_time": self.bb_optimizer.elapsed_time,
            "default_run": {
                "execution_time": self.acc_black_box.default_execution_time,
                "job_id": self.acc_black_box.default_jobid,
                "parameters": self.acc_black_box.default_parameters
            },
            "average_noise": float(np.mean(self.bb_optimizer.measured_noise)),
            "explored_space": float(self.bb_optimizer.size_explored_space[0])}
        request = self.api_client.put(
            f"experiments/{self.experiment_id}/finish", json=dict_)
        if not 200 <= request.status_code < 400:
            self.fail()
            raise Exception(
                f"Could not finish experiment with status code {request.status_code}")

    def fail(self):
        """
        Fail the experiment. If there is an experiment id, sends a request at the endpoint /fail.
        Else, does not do anything (could be a good idea to perform some logging).
        """
        if self.experiment_id:
            request = self.api_client.put(
                f"experiments/{self.experiment_id}/fail")
            if not 200 <= request.status_code < 400:
                raise Exception(
                    f"Could not fail experiment with status code {request.status_code}")

    def stop(self):
        """
        Stop the experiment.
        """
        request = self.api_client.put(
            f"experiments/{self.experiment_id}/stop")
        if not 200 <= request.status_code < 400:
            raise Exception(
                f"Could not fail experiment with status code {request.status_code}")

    def summarize(self):
        """Summarize the experiment by printing out the best parametrization, the associated
        fitness, and the BBO summary.
        """
        # Compute the optimal parametrization from the bb optimizer object
        optimal_param = self.build_parameter_dict(self.configuration.acc_parameter_names,
                                                  [self.bb_optimizer.best_parameters_in_grid])
        print(f"Optimal time: {self.bb_optimizer.best_fitness}")
        print(f"Improvement compared to default:"
              f"{round((self.acc_black_box.default_execution_time - self.bb_optimizer.best_fitness)/self.acc_black_box.default_execution_time, 2)*100}%")
        print(
            f"Speedup: {self.bb_optimizer.best_fitness / self.acc_black_box.default_execution_time}")
        print(f"Optimal parametrization: {optimal_param}")
        print(
            f"Number of early stops: {sum(self.bb_optimizer.history['truncated'])}")
        print(
            f"Average noise within each parametrization: {self.bb_optimizer.measured_noise}")
        self.bb_optimizer.summarize()

    @staticmethod
    def build_parameter_dict(parameter_names, parameter_values):
        """Static method to build the dictionary associated with the name of the parameters
        and their associated values.

        Args:
            parameter_names (list of str): The name of the parameters to use.
            parameter_values (list of lists of int): The values of the parameters

        Returns:
            (list of dict): the dicts of the parameters with corresponding values.
        """
        # The list that will contain the dictionaries
        list_dict = []
        # Check if there is at least two nested elements in the dictionary
        if not isinstance(parameter_values[0], list):
            parameter_values = [parameter_values]
        for value in parameter_values:
            list_dict.append(dict(zip(parameter_names, value)))
        return list_dict
