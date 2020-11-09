# Copyright 2020 BULL SAS All rights reserved
"""The class SHAManExperiment is a tool to launch, monitor and save
optimization experiments."""

import datetime
import sys
from pathlib import Path

import numpy as np
from httpx import Client
from typing import Dict, List
from loguru import logger

from bbo.optimizer import BBOptimizer
from shaman_core.models.shaman_config_model import SHAManConfig
from shaman_core.models.experiment_models import (
    FinalResult,
    InitExperiment,
    IntermediateResult,
)
from shaman_core.config import APIConfig

from .bb_wrapper import BBWrapper


__CURRENT_DIR__ = Path.cwd()
api_settings = APIConfig()


class SHAManExperiment:
    """This class represents an optimization experiment.

    It allows to plan, launch and store the information corresponding to
    an experiment.
    """

    def __init__(
        self,
        component_name: str,
        nbr_iteration: int,
        sbatch_file: str,
        experiment_name: str,
        configuration_file: str,
        sbatch_dir: str = None,
        slurm_dir: str = None,
        result_file: str = None,
    ) -> None:
        """Builds an object of class SHAManExperiment. This experiment is
        defined by giving:

            - The name of the component to tune.
            - The number of allowed iterations for the optimization process.
            - The name of the sbatch file to run.
            - The name of the experiment.
            - A configuration file to setup the experiment.
            - Where the slurm outputs should be stored
                (optional, if not specified, the outputs are deleted)
            - The path to the result file (optional, if not specified,
                no file is created).

        Args:
            component_name (str): The name of the component to use.
            nbr_iteration (int): The number of iterations.
            sbatch_file (str): The path to the sbatch file.
            experiment_name (str): The name of the experiment.
            sbatch_dir (str or Path): The working directory,
                where the shaman sbatch will be stored.
                If not specified, the directory where the command is called.
            slurm_dir (str or Path): The directory where the slurm outputs
                will be stored.
                If set to None, all the slurm outputs are removed after the
                end of the experiment.
            result_file (str): The path to the result file.
                If set to None, no such file is created and the results are
                debuged to the screen.
            configuration_file (str): The path to the configuration file.
                Defaults to the configuration file present in the package
                and called config.cfg.
        """
        # The name of the component that will be tuned through the experiment
        self.component_name = component_name
        # The maximum number of iterations
        self.nbr_iteration = nbr_iteration
        # The name of the sbatch to use, after ensuring its existence
        if Path(sbatch_file).exists():
            self.sbatch_file = sbatch_file
        else:
            raise FileNotFoundError(f"Could not find sbatch {sbatch_file}.")
        # Store information about the experiment
        self.experiment_name = experiment_name
        # Store the sbatch directory and convert to Path if not already
        if sbatch_dir:
            if isinstance(sbatch_dir, Path):
                self.sbatch_dir = sbatch_dir
            else:
                self.sbatch_dir = Path(sbatch_dir)
        else:
            self.sbatch_dir = Path.cwd()
        # Store the slurm directory and convert to Path if not already
        if slurm_dir:
            if isinstance(slurm_dir, Path):
                self.slurm_dir = slurm_dir
            else:
                self.slurm_dir = Path(slurm_dir)
        else:
            self.slurm_dir = None
        self.result_file = result_file
        self.experiment_id = ""

        # Parse the configuration
        self.configuration = SHAManConfig.from_yaml(
            configuration_file, self.component_name
        )
        # Create API client using the configuration information
        self.api_client = Client(base_url=self.api_url, proxies={})
        # Create the black box object using the informations
        self.bb_wrapper = BBWrapper(
            self.component_name,
            self.configuration.component_parameter_names,
            self.sbatch_file,
            sbatch_dir=self.sbatch_dir,
            component_configuration=self.api_url
            + "/"
            + api_settings.component_endpoint,
        )
        logger.debug(self.api_url + "/" + api_settings.component_endpoint)

        # Setup black box optimizer using configuration information
        self.bb_optimizer = self.setup_bb_optimizer()
        # Compute the start of the experiment
        self.experiment_start = \
            datetime.datetime.utcnow().strftime("%y/%m/%d %H:%M:%S")

    def setup_bb_optimizer(self) -> BBOptimizer:
        """Setups the black-box from the configuration."""
        # Create the BBOptimizer object using the different options in the
        # configuration
        # If pruning is enabled, parse corresponding fields
        if self.configuration.pruning:
            pruning = True
            max_step_cost = (
                self.bb_wrapper.default_execution_time
                if self.configuration.pruning.max_step_duration == "default"
                else self.configuration.pruning.max_step_duration
            )
        else:
            max_step_cost = None
            pruning = False

        self.bb_optimizer = BBOptimizer(
            black_box=self.bb_wrapper,
            parameter_space=self.configuration.component_parameter_space,
            max_iteration=self.nbr_iteration,
            async_optim=pruning,
            max_step_cost=max_step_cost,
            **self.configuration.bbo_parameters,
        )
        return self.bb_optimizer

    def launch(self) -> None:
        """Launches the tuning experiment."""
        logger.debug("Creating experiment.")
        # Create the experiment through API request
        self.create_experiment()
        if self.configuration.experiment.default_first:
            # Launch a run using default parameterization of the component
            logger.info("Running application with default parametrization.")
            self.bb_wrapper.run_default()
        # Setup the optimizer
        logger.debug("Initializing black box optimizer.")
        self.setup_bb_optimizer()
        # Launch the optimization
        logger.debug("Launching optimization.")
        self.bb_optimizer.optimize(callbacks=[self.update_history])
        # Summarize the optimization
        # If there is a result file, write the output in it
        if self.result_file:
            orig_stdout = sys.stdout
            file_ = open(self.result_file, "w")
            sys.stdout = file_
            self.summarize()
            sys.stdout = orig_stdout
            file_.close()
        logger.debug(f"Summary of experiment: {self.summarize()}")

    def clean(self) -> None:
        """Cleans the experiment by removing the sbatch generated by Shaman.

        If there is no value specified for the slurm outputs folder,
        removes them.
        """
        for file_ in Path(__CURRENT_DIR__).glob("slurm*.out"):
            if self.slurm_dir:
                # Create if it doesn't already exist the folder
                self.slurm_dir.mkdir(exist_ok=True)
                # Move the output
                file_.rename(self.slurm_dir / file_.name)
            else:
                # Remove the output
                file_.unlink()
        # Clean up the sbatch file in the current dir where the experiment runs
        # Else keep it
        for file_ in Path(__CURRENT_DIR__).glob("*_shaman*.sbatch"):
            (Path(__CURRENT_DIR__) / file_).unlink()

    @property
    def api_url(self) -> str:
        """Returns as a string the URL to the API using the data in the
        configuration file."""
        return f"http://{api_settings.api_host}:{api_settings.api_port}"

    @property
    def start_experiment_dict(self) -> Dict:
        """Creates a dictionnary describing the experiment from its start."""
        return InitExperiment(
            **{
                "experiment_name": self.experiment_name,
                "experiment_start": self.experiment_start,
                "experiment_budget": self.nbr_iteration,
                "component": self.component_name,
                "experiment_parameters": dict(self.configuration.bbo),
                "noise_reduction_strategy":
                dict(self.configuration.noise_reduction)
                if self.configuration.noise_reduction
                else dict(),
                "pruning_strategy": {
                    "pruning_strategy": str(
                        self.configuration.pruning.max_step_duration
                    )
                    if self.configuration.pruning
                    else self.configuration.pruning
                },
                "sbatch": open(self.sbatch_file, "r").read(),
            }
        ).dict()

    def create_experiment(self) -> None:
        """Create the experiment upon initialization."""
        request = self.api_client.post(
            "experiments", json=self.start_experiment_dict)
        if not 200 <= request.status_code < 400:
            raise Exception(
                "Could not create experiment with status code"
                f"{request.status_code}"
            )
        self.experiment_id = request.json()["id"]

    @property
    def best_performance(self) -> float:
        """Returns the current best noise.

        Returns:
            float: The best time.
        """
        return self.bb_optimizer._get_best_performance()

    @property
    def improvement_default(self) -> float:
        """Computes the improvement compared to the default parametrization.

        Returns:
            float: The improvement compared to the default parametrization.
        """
        _, best_time = self.best_performance
        return float(
            round(
                (self.bb_wrapper.default_execution_time - best_time)
                / self.bb_wrapper.default_execution_time,
                2,
            )
            * 100
        )

    @property
    def average_noise(self) -> float:
        """Computes the average noise within the tested parametrization.

        Returns:
            float: The average measured noise.
        """
        return float(np.mean(self.bb_optimizer.measured_noise))

    def _updated_dict(self, history: Dict) -> Dict:
        """Builds the updated dictionary that will be sent at each iteration to
        the API.

        Args:
            history (Dict): The BBO history from the optimizer

        Returns:
            Dict: The updated dict to add to the POST request.
        """
        logger.debug(f"Current optimization history: {history}")
        best_parameters, best_fitness = self.best_performance
        logger.debug(f"Best parameters so far: {best_parameters}")
        logger.debug(f"Best performance so far: {best_fitness}")
        return IntermediateResult(
            **{
                "jobids": self.bb_wrapper.component.submitted_jobids[-1],
                "execution_time": list(history["fitness"])[-1],
                "parameters": self.build_parameter_dict(
                    self.configuration.component_parameter_names,
                    history["parameters"].tolist(),
                )[-1],
                "truncated": bool(list(history["truncated"])[-1]),
                "resampled": bool(list(history["resampled"])[-1]),
                "initialization": bool(list(history["initialization"])[-1]),
                "improvement_default": self.improvement_default,
                "average_noise": self.average_noise,
                "explored_space":
                float(self.bb_optimizer.size_explored_space[0]),
                "best_parameters": self.build_parameter_dict(
                    self.configuration.component_parameter_names,
                    best_parameters.tolist(),
                ),
                "best_fitness": best_fitness,
            }
        ).dict()

    def update_history(self, history: Dict) -> None:
        """Update the optimization history at each BBO step and force
        conversion from numpy types.

        Args:
            history (dict): The BBO history
        """
        logger.debug(
            f"Writing update dictionary {self._updated_dict(history)}")
        request = self.api_client.put(
            f"experiments/{self.experiment_id}/update",
            json=self._updated_dict(history)
        )
        if not 200 <= request.status_code < 400:
            self.fail()
            raise Exception(
                "Could not finish experiment with status code"
                f"{request.status_code}"
            )

    @property
    def end_dict(self) -> Dict:
        """Comptues the dictionary sent to the API at the end of the
        experiment.

        Returns:
            Dict: The dictionary to send to the API.
        """
        best_parameters, best_fitness = self.best_performance
        return FinalResult(
            **{
                "averaged_execution_time": self.bb_optimizer.averaged_fitness,
                "min_execution_time": self.bb_optimizer.min_fitness,
                "max_execution_time": self.bb_optimizer.max_fitness,
                "std_execution_time": self.bb_optimizer.measured_noise,
                "resampled_nbr": self.bb_optimizer.resampled_nbr,
                "improvement_default": self.improvement_default,
                "elapsed_time": self.bb_optimizer.elapsed_time,
                "default_run": {
                    "execution_time": self.bb_wrapper.default_execution_time,
                    "job_id": self.bb_wrapper.default_jobid,
                    "parameters": self.bb_wrapper.default_parameters,
                },
                "average_noise": self.average_noise,
                "explored_space":
                float(self.bb_optimizer.size_explored_space[0]),
                "best_fitness": best_fitness,
                "best_parameters": self.build_parameter_dict(
                    self.configuration.component_parameter_names,
                    best_parameters.tolist(),
                ),
            }
        ).dict()

    def end(self):
        """End the experiment once it is over."""
        request = self.api_client.put(
            f"experiments/{self.experiment_id}/finish", json=self.end_dict
        )
        if not 200 <= request.status_code < 400:
            self.fail()
            raise Exception(
                "Could not finish experiment with status code"
                f"{request.status_code}"
            )

    def fail(self):
        """Fail the experiment.

        If there is an experiment id, sends a request at the endpoint
        /fail. Else, does not do anything (could be a good idea to
        perform some logging).
        """
        if self.experiment_id:
            request = self.api_client.put(
                f"experiments/{self.experiment_id}/fail")
            if not 200 <= request.status_code < 400:
                raise Exception(
                    "Could not fail experiment with status code"
                    f"{request.status_code}"
                )

    def stop(self):
        """Stop the experiment."""
        request = self.api_client.put(f"experiments/{self.experiment_id}/stop")
        if not 200 <= request.status_code < 400:
            raise Exception(
                "Could not fail experiment with status code"
                f"{request.status_code}"
            )

    def summarize(self):
        """Summarize the experiment by printing out the best parametrization,
        the associated fitness, and the BBO summary."""
        # Compute the optimal parametrization from the bb optimizer object
        optimal_param = self.build_parameter_dict(
            self.configuration.component_parameter_names,
            [self.bb_optimizer.best_parameters_in_grid],
        )
        print(f"Optimal time: {self.bb_optimizer.best_fitness}")
        print(
            f"Improvement compared to default:" f"{self.improvement_default}%")
        print(f"Optimal parametrization: {optimal_param}")
        print(
            "Number of early stops:"
            f"{sum(self.bb_optimizer.history['truncated'])}")
        print(
            "Average noise within each parametrization:"
            f"{self.bb_optimizer.measured_noise}"
        )
        self.bb_optimizer.summarize()

    @staticmethod
    def build_parameter_dict(
        parameter_names: List[str], parameter_values: List[List[float]]
    ) -> List[Dict]:
        """Static method to build the dictionary associated with the name of
        the parameters and their associated values.

        Args:
            parameter_names (list of str): The name of the parameters to use.
            parameter_values (list of lists of float):
                The values of the parameters

        Returns:
            list of dict: the dicts of the parameters with
                corresponding values.
        """
        # The list that will contain the dictionaries
        list_dict = []
        # Check if there is at least two nested elements in the dictionary
        if not isinstance(parameter_values[0], list):
            parameter_values = [parameter_values]
        for value in parameter_values:
            list_dict.append(dict(zip(parameter_names, value)))
        return list_dict
