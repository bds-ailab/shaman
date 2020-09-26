"""
configuration module of SHAMan API"""

from enum import Enum
from pydantic import BaseSettings
from pathlib import Path


class LoggingLevel(str, Enum):
    """
    Allowed log levels for the application
    """

    CRITICAL: str = "CRITICAL"
    ERROR: str = "ERROR"
    WARNING: str = "WARNING"
    INFO: str = "INFO"
    DEBUG: str = "DEBUG"


class AppConfig(BaseSettings):
    """
    Configuration can be set using:
        - Keyword arguments at instantation
        - Using environment variables
    """

    shaman_mongodb_host: str = "mimsy.farm"
    shaman_mongodb_port: int = 27017
    shaman_mongodb_database: str = "shaman_db"
    shaman_redis_host: str = "mimsy.farm"
    shaman_redis_port: int = 6379
    log_level: LoggingLevel = "DEBUG"

    class Config:
        case_sensitive = False


CONFIG = AppConfig()
