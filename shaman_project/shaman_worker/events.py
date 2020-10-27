"""Startup and shutdown worker events."""
from os import chdir
from shaman_core.config import EngineConfig


async def startup(context):
    """
    On startup of the optimization worker, go to the right directory to run the SHAMan optimization.
    """
    # Store working directory as string
    context["settings"] = settings = EngineConfig()
    # Go to working directory
    settings.chdir()
    # Print a message to stdout for the user
    print(f"Starting up the worker in directory '{settings.directory}'")


async def shutdown(context):
    """
    Do nothing on shutdown.
    """
    print("Stopping the worker")
