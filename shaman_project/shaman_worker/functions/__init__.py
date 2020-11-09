# Copyright 2020 BULL SAS All rights reserved
"""This subpackage defines the functions that can be executed on ARQ worker."""
from .experiments import launch_experiment


FUNCTIONS = [launch_experiment]
