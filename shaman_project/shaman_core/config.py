# Copyright 2020 BULL SAS All rights reserved
"""Module contaning the configuration data for the SHAMan project.
Configuration files deal with:

- The configuration of the bb_wrapper
- The configuration of the API
- The configuration of the worker
"""
import os
from pathlib import Path
from arq.connections import RedisSettings
from pydantic import BaseSettings


class SHAManConfig(BaseSettings):
    """Parent class for configuration files."""

    class Config:
        case_sensitive = False
        env_prefix = "SHAMAN_"


class DatabaseConfig(SHAManConfig):
    """This class sets values for different variables describing the database.

    Configuration can be set using:
        - Keyword arguments at instantation
        - Using environment variables
    """

    # Host of the mongo db
    mongodb_host: str = "mongo"
    # Port of the mongo db
    mongodb_port: int = 27017
    # Name of the mongo database
    mongodb_database: str = "shaman_db"


class APIConfig(SHAManConfig):
    """This class sets values for different variables describing the API."""

    # Host of API
    api_host: str = "api"
    # Port of the API
    api_port: int = 5000
    # Endpoint to call to post the document describing the components
    component_endpoint: str = "components"


class RedisConfig(SHAManConfig):
    """This class sets values for different variables describing the Redis
    service."""

    redis_host: str = "redis"
    redis_port: int = 6379

    def settings(self):
        return RedisSettings(host=self.redis_host, port=self.redis_port)


class EngineConfig(SHAManConfig):
    """This class sets values for different variables describing the behavior
    of the engine."""

    directory: Path = "/slurm_fs"

    def chdir(self) -> None:
        self.directory.mkdir(exist_ok=True, parents=True)
        os.chdir(self.directory)

    def join_path(self, other: str) -> Path:
        p = self.directory / other
        return p.resolve()
