"""
Databases subpackage of shaman_api package.
This subpackages defines connections to mongodb databases
and functions to interact with databases
"""
from .shaman import (
    connect_shaman_db,
    close_shaman_db,
    create_experiment,
    get_experiments,
    get_experiment,
    update_experiment,
    close_experiment,
    watch_experiments,
    fail_experiment,
    stop_experiment,
    watch_experiment,
    get_experiment_status,
    launch_experiment
)

__all__ = [
    "connect_shaman_db",
    "close_shaman_db",
    "create_experiment",
    "get_experiments",
    "get_experiment",
    "update_experiment",
    "close_experiment"
]
