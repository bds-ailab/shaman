"""
This module defines the logger of the application
"""
import logging

from .config import CONFIG


LOGGING_LEVELS_MAPPING = {
    "CRITICAL": logging.CRITICAL,
    "ERROR": logging.CRITICAL,
    "WARNING": logging.WARNING,
    "INFO": logging.INFO,
    "DEBUG": logging.DEBUG,
}


def get_logger(name: str):
    """
    Create a new logger with given name.
    Logging level is induced from configuration.
    """
    log_level = LOGGING_LEVELS_MAPPING[CONFIG.log_level]

    logger = logging.getLogger(name)

    logger.setLevel(log_level)
    logger.propagate = False

    formatter = logging.Formatter(
        "%(levelname)s::%(asctime)s::%(name)s::%(lineno)d:: %(message)s"
    )

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(log_level)

    logger.addHandler(stream_handler)

    return logger
