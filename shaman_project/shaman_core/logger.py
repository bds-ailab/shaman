"""Logging module for the SHAMan package."""
import sys
from enum import Enum
from pathlib import Path
from typing import Optional, Tuple

from pydantic import BaseSettings
from loguru import logger


class LoggingLevel(str, Enum):
    """Allowed log levels for the application."""

    CRITICAL: str = "CRITICAL"
    ERROR: str = "ERROR"
    WARNING: str = "WARNING"
    INFO: str = "INFO"
    DEBUG: str = "DEBUG"


class LoggingSettings(BaseSettings):
    """Configure your application logging using a LoggingSettings instance.

    All arguments are optional.

    Arguments:
        level (str): the minimum log-level to log. (default: "DEBUG")
        format (str): the logformat to use.
            (default: "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green>
            | <level>{level: <8}</level>
            | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan>
            | <level>{message}</level>")
        filepath (Path): the path where to store the logfiles. (default: None)
        rotation (str): when to rotate the logfile. (default: "1 days")
        retention (str): when to remove logfiles. (default: "1 months")
    """

    level: LoggingLevel = LoggingLevel.DEBUG
    format: str = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )
    filepath: Optional[Path] = None
    rotation: str = "1 days"
    retention: str = "1 months"

    class Config:
        env_prefix = "logging_"


def setup_logger(
    level: str,
    format: str,
    filepath: Optional[Path] = None,
    rotation: Optional[str] = None,
    retention: Optional[str] = None,
) -> Tuple[int, ...]:
    """Define the global logger to be used by your entire application.

    Arguments:
        level: the minimum log-level to log.
        format: the logformat to use.
        filepath: the path where to store the logfiles.
        rotation: when to rotate the logfile.
        retention: when to remove logfiles.

    Returns:
        the logger to be used by the service.
    """
    # Add stdout logger
    stdout_handler_id = logger.add(
        sys.stdout,
        enqueue=True,
        colorize=True,
        backtrace=True,
        level=level.upper(),
        format=format,
    )
    # Optionally add filepath logger
    file_handler_id = 0
    if filepath:
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        file_handler_id = logger.add(
            str(filepath),
            rotation=rotation,
            retention=retention,
            enqueue=True,
            colorize=False,
            backtrace=True,
            level=level.upper(),
            format=format,
        )
        return (
            stdout_handler_id,
            file_handler_id,
        )

    return (stdout_handler_id,)


def setup_logger_from_settings(settings: LoggingSettings) -> Tuple[int, ...]:
    """Define the global logger to be used by your entire application.

    Arguments:
        settings: the logging settings to apply.

    Returns:
        the logger instance.
    """
    return setup_logger(
        settings.level,
        settings.format,
        settings.filepath,
        settings.rotation,
        settings.retention,
    )


def setup_logger_from_env() -> Tuple[int, ...]:
    """Override all standard library logging handlers to be intercepted and
    forwarded to loguru."""
    settings = LoggingSettings()
    return setup_logger_from_settings(settings)
