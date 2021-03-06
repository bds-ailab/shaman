# Copyright 2020 BULL SAS All rights reserved
"""routers subpackage of shaman_api package.

This subpackage implement the endpoints of the REST API.
"""
from .experiments import router as experiment_router
from .components import router as component_router

__all__ = ["experiment_router", "component_router"]
