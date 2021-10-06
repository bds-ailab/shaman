# Copyright 2020 BULL SAS All rights reserved
"""Pydantic model for parsing the SHAMan configuration."""
import dataclasses
from pathlib import Path
from pydantic import BaseModel, validator, root_validator
from pydantic.dataclasses import dataclass

from typing import Dict, Optional, List, Any, Union
from enum import Enum
import importlib
import ast

import numpy as np
from loguru import logger
import yaml


class BaseConfiguration:
    """Base class to load YAML."""

    @classmethod
    def from_yaml(cls, path, component_name):
        """Loads the yaml file located at the path path."""
        return cls(
            **yaml.load(Path(path).read_text(), Loader=yaml.SafeLoader),
            component_name=component_name,
        )


class ExperimentParameters(BaseModel):
    """Contains the experiment parameters."""

    default_first: bool = True


class PruningParameters(BaseModel):
    """Contains the pruning parameters."""

    max_step_duration: Any

    @validator("max_step_duration")
    def check_max_step(cls, v):
        """Checks that the max step duration is either:

        - default
        - a numpy function
        - an int
        """
        if isinstance(v, int):
            return v
        else:
            try:
                module_name = v.split(".")
                module = importlib.import_module(".".join(module_name[:-1]))
                return getattr(module, module_name[-1])
            except BaseException:
                if v == "default":
                    return v
                else:
                    raise ValueError(
                        "Unknown input for max_step_duration \
                    variable."
                    )


class StepTypeEnum(str, Enum):
    """Defines an enumeration for the type of parameter in the
    parameter range. Possible values are:
    - additive
    - multiplicative
    """
    additive = "additive"
    multiplicative = "multiplicative"


class ParameterRange(BaseModel):
    """Contains the possible tested range of the parameters."""

    min: int
    max: int
    step: int
    step_type: StepTypeEnum = StepTypeEnum.additive

    @root_validator
    def check_range(cls, values):
        """Check that the range has the proper format."""
        if values["max"] < values["min"]:
            raise ValueError(
                "Specified min value in parameter range is \
                superior to max value."
            )
        return values

    @property
    def parameter_range(self) -> List:
        """Creates a parameter range given the grid information."""
        if self.step_type == "additive":
            return np.arange(self.min, self.max + 1, self.step)
        elif self.step_type == "multiplicative":
            range_ = list()
            val_ = self.min
            while val_ <= self.max:
                range_.append(val_)
                val_ = val_ * self.step
            return np.array(range_)


class ParameterList(BaseModel):
    """Contains the possible values of the parameters when"""


@dataclass
class SHAManConfig(BaseConfiguration):
    """Contains the configuration of the SHAMan application."""

    experiment: ExperimentParameters
    bbo: Dict
    components: Dict[str, Dict[str, Union[ParameterRange, List]]]
    component_name: str
    pruning: Optional[PruningParameters] = None
    noise_reduction: Optional[Dict] = None
    component_parameters: Dict[str,
                               Union[ParameterRange, List]] = dataclasses.field(init=False)

    def __post_init__(self) -> None:
        """Initialize an object of class SHAManConfig."""
        try:
            self.component_parameters = self.components[self.component_name]
        except KeyError:
            raise KeyError(f"Invalid component name {self.component_name}")

    @property
    def bbo_parameters(self) -> Dict:
        """Parses the bbo parameters to make them suitable to pass as argument
        of the BBOptimizer."""
        bbo_kwargs = dict()
        bbo_parameters = self.bbo
        if self.noise_reduction:
            bbo_parameters.update(self.noise_reduction)
        for param, value in bbo_parameters.items():
            if isinstance(value, str) and (
                ("bbo." in value) or
                ("sklearn." in value) or
                ("numpy." in value)
            ):
                module_name = value.split(".")
                module = importlib.import_module(".".join(module_name[:-1]))
                bbo_kwargs[param] = getattr(module, module_name[-1])
            else:
                try:
                    bbo_kwargs[param] = ast.literal_eval(value)
                except ValueError:
                    bbo_kwargs[param] = value
        return bbo_kwargs

    @property
    def component_parameter_names(self) -> List:
        """Returns the name of the parameters."""
        return list(self.component_parameters.keys())

    @property
    def component_parameter_space(self) -> np.ndarray:
        """Returns the range of the parameters, and takes into account
        whether the specified component range is a list or a parameter
        range."""
        array_parameters = list()
        for parameter_range in self.component_parameters.values():
            # Check if the parameter_range has been specified as a
            # ParameterRange (min, max step)
            if isinstance(parameter_range, ParameterRange):
                array_parameters.append(
                    np.array(parameter_range.parameter_range))
            else:
                array_parameters.append(np.sort(np.array(parameter_range)))
        logger.debug(f"Parameter space: {array_parameters}")
        return np.array(array_parameters, dtype=object)
