# Copyright 2020 BULL SAS All rights reserved
"""Databases subpackage of shaman_api package.

This subpackages defines connections to mongodb databases and functions
to interact with databases
"""
from .shaman import ExperimentDatabase

__all__ = ["ExperimentDatabase"]
