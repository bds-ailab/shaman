"""
Given data sent by the user from the Web Interface, builds the corresponding experiment
configuration.
"""
from typing import Dict
import yaml
from pathlib import Path
import os
from pydantic import BaseSettings, validator

from devtools import debug


class SHAManSettings(BaseSettings):
    """Class to get settings of shaman engine."""

    directory: Path = "/slurm_fs"

    def chdir(self) -> None:
        self.directory.mkdir(exist_ok=True, parents=True)
        os.chdir(self.directory)

    def join_path(self, other: str) -> Path:
        p = self.directory / other
        return p.resolve()

    class Config:
        env_prefix = "shaman_"
        case_sensitive = False


class SHAManConfigBuilder:
    """Class to build a shaman configuration file from the data sent by the user.
    """

    CONFIGURATION_KEYS = {
        "experiment": ["default_first"],
        "pruning": ["max_step_duration"],
        "noise_reduction": [
            "resampling_policy",
            "fitness_aggregation",
            "nbr_resamples",
            "percentage",
            "estimator",
        ],
        "bbo": [
            "heuristic",
            "initial_sample_size",
            "selection_method",
            "crossover_method",
            "mutation_method",
            "mutation_rate",
            "elitism",
            "regression_model",
            "next_parameter_strategy",
            "cooling_schedule",
            "restart",
        ],
    }

    def __init__(self, default_file: Path, output_file: Path) -> None:
        """Initialize an object of class SHAManConfig, by using a default file and creating an
        output file.

        Args:
            default_file (Path): The path to the default file.
            output_file (Path): The path to the file to output.
        """
        # Open the default_file and store it as a config attribute
        with open(default_file, "r") as stream:
            self.config = yaml.safe_load(stream)
        # Save the path to the output file as attribute
        self.output_file = output_file

    @staticmethod
    def build_parametric_space(post_data: Dict) -> Dict:
        """
        Builds the part of the configuration file that will contain the parametric space description.
        {
            param_1: {min: 1, max: 2, step: 1},
            ...
        }}
        """
        # Dictionary that will contain the parametric space description
        parameters_dict = {}
        # Get the names of the parameter
        for key, value in post_data.items():
            if key.startswith("parameter_"):
                # Get parameter name
                parameter_name = "_".join(key.split("_")[2:])
                # Parse whether min, max or step
                status = key.split("_")[1]
                # Check if the entry already exists
                try:
                    parameters_dict[parameter_name].update({status: value})
                # If it does not exist, create the entry
                except KeyError:
                    parameters_dict[parameter_name] = {status: value}
        return parameters_dict

    def filter_post_data(self, post_data: Dict) -> Dict:
        """Separate the post_data into a nested with four top level keys:
            - experiment: parameters concerning the experiment
            - bbo_parameters: parameters concerning the BBO package
            - pruning_strategy: parameters concerning the pruning strategy.
            - noise_experiment: parameters concerning the noise reduction
            - components: the parameters and their range

        Args:
            post_data (dict): the data sent by the user containing the different configuration
                parameters.

        Returns:
            dict: a filtered dictionary.
        """
        filtered_data = {}
        # Iterate over configuration keys to properly separate the post_data
        for section, parameters in self.CONFIGURATION_KEYS.items():
            filtered_data[section] = {
                parameter: post_data[parameter]
                for parameter in parameters
                if post_data.get(parameter) is not None
            }
        # Add parametric description
        filtered_data["components"] = {
            post_data["component_name"]: self.build_parametric_space(post_data)
        }
        return filtered_data

    def update_section(self, section_name: str, update_dict: Dict) -> None:
        """Update the section 'section_name' with the data contained in update_dict.

        Args:
            section_name (str): The name of the section to update
            update_dict (dict): The data to use in the update.
        """
        config_current = self.config[section_name]
        # If there is some data to update
        if update_dict:
            # If there is already some data
            if config_current:
                config_current.update(update_dict)
            # If there is no data already
            else:
                config_current = update_dict
            self.config[section_name] = config_current
        # If there is no update data and no data in the default file
        else:
            if not config_current:
                self.config.pop(section_name)

    def build_configuration(self, post_data: Dict) -> None:
        """Build the configuration from a default file by filling out the different values using the
        data contained in the dictionary 'post_data'.

        Args:
            post_data (dict): Dictionary containing the parameters of the experiment
        """
        # Separate the data into the three possible sections of the CFG, filtering on the fields
        config_dicts = self.filter_post_data(post_data)
        # Update each section of the configuration
        self.update_section("bbo", config_dicts["bbo"])
        self.update_section("noise_reduction", config_dicts["noise_reduction"])
        self.update_section("experiment", config_dicts["experiment"])
        self.update_section("pruning", config_dicts["pruning"])
        self.update_section("components", config_dicts["components"])
        # Save the result in file
        self.save_configuration()

    def save_configuration(self) -> None:
        """Save the configuration file in the location indicated by the attribute output file.
        """
        with open(self.output_file, "w") as configfile:
            yaml.dump(self.config, configfile)
            print(f"Dumped configuration file at {self.output_file}")
