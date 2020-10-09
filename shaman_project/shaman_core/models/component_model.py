"""
Defines a pydantic model that represents a tunable component.
"""
from pathlib import Path
from typing import Dict, Optional, Union, Type, Any
from enum import Enum
import ast
import builtins
import httpx
from httpx import ConnectError
from pydantic import BaseModel, validator, root_validator
import yaml


class BaseConfiguration:
    """Base class to load YAML.
    """

    @classmethod
    def from_yaml(cls, path: str):
        """
        Loads the yaml file located at the path path.

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
        request = httpx.get(url)
        if 200 <= request.status_code < 400:
            return cls(**request.json())
        else:
            raise Exception("Could not read component configuration from API.")


class TunableParameter(BaseModel):
    """
    Creates a pydantic model for a tunable parameter.
    """

    type: str
    default: Optional[Any] = None
    optional: bool = False
    env_var: Optional[bool] = None
    description: Optional[str] = None
    cmd_var: Optional[str] = None
    flag: Optional[str] = None

    @root_validator(pre=True)
    def check_env_cmd(cls, values):
        """Checks that the parameter is either a command line variable or an environment one.
        """
        # Check that default value has correct type
        try:
            expected_type = getattr(builtins, values["type"])
        except AttributeError:
            raise AttributeError("Specified parameter type was not understood.")
        default = values.get("default", None)
        if default and not isinstance(default, expected_type):
            raise TypeError("Default does not match the parameter type")

        # Check that either cmd_var or env_var are defined
        if (not "cmd_var" in values) and (not "env_var" in values):
            raise ValueError(
                "Variable must either be a command line variable or an environment variable."
            )

        # Check that flag is defined when cmd_var is defined
        if "cmd_var" in values:
            if not "flag" in values:
                raise ValueError(
                    "No specification of the flag for a command line parameter."
                )

        return values


class TunableComponentModel(BaseModel):
    """
    Creates a pydantic model for a tunable component.
    """

    plugin: str = ""
    header: Optional[str]
    command: Optional[str]
    ld_preload: Optional[str]
    parameters: Dict[str, TunableParameter]
    custom_component: Optional[str]


class TunableComponentsModel(BaseConfiguration, BaseModel):
    """Creates a pydantic model for a list of tunable components.
    """

    components: Dict[str, TunableComponentModel]
