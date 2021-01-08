# Copyright 2020 BULL SAS All rights reserved
"""Defines a pydantic model that represents a tunable component."""
from pathlib import Path
import importlib
from typing import Dict, Optional, Any
import builtins
import httpx
from pydantic import BaseModel, root_validator
import yaml


class BaseConfiguration:
    """Base class to load YAML."""

    @classmethod
    def from_yaml(cls, path: str):
        """Loads the yaml file located at the path path.

        Args:
            path (str): The path to the YAML file.
        """
        return cls(**yaml.load(Path(path).read_text(), Loader=yaml.SafeLoader))

    @classmethod
    def from_api(cls, url: str):
        """Loads the JSON file located at the url resource.

        Args:
            url (str): The URL to reach the API resource.
        """
        request = httpx.get(url, proxies={})
        if 200 <= request.status_code < 400:
            return cls(**request.json())
        else:
            raise Exception("Could not read component configuration from API.")


class TunableParameter(BaseModel):
    """Creates a pydantic model for a tunable parameter."""

    type: str
    default: Optional[Any] = None
    optional: bool = False
    env_var: Optional[bool] = None
    description: Optional[str] = None
    cmd_var: Optional[str] = None
    cli_var: Optional[bool] = None
    flag: Optional[str] = None
    suffix: Optional[str] = None

    @root_validator(pre=True)
    def check_env_cmd(cls, values):
        """Checks that the parameter is either a command line variable or an
        environment one."""
        # Check that default value has correct type
        try:
            expected_type = getattr(builtins, values["type"])
        except AttributeError:
            raise AttributeError(
                "Specified parameter type was not \
            understood."
            )
        default = values.get("default", None)
        if default and not isinstance(default, expected_type):
            raise TypeError("Default does not match the parameter type")

        # Check that either cmd_var or env_var are defined
        if (
            ("cmd_var" not in values)
            and ("env_var" not in values)
            and ("cli_var" not in values)
        ):
            raise ValueError(
                "Variable must either be a command line variable, \
                an environment variable or a CLI variable."
            )
        return values


class TunableComponentModel(BaseModel):
    """Creates a pydantic model for a tunable component."""

    plugin: str = ""
    header: Optional[str]
    command: Optional[str]
    ld_preload: Optional[str]
    parameters: Dict[str, TunableParameter]
    custom_target: Optional[str] = "parse_execution_time.parse_slurm_times"

    @property
    def get_target(self):
        """Import the function target.
        Defaults to the parse slurm times in the plugins package.
        """
        plugin_path = "bb_wrapper.tunable_component.plugins."
        split_target_name = self.custom_target.split(".")
        module_path = plugin_path + split_target_name[0]
        module = importlib.import_module(module_path)
        return getattr(module, split_target_name[1])


class TunableComponentsModel(BaseConfiguration, BaseModel):
    """Creates a pydantic model for a list of tunable components."""

    components: Dict[str, TunableComponentModel]
