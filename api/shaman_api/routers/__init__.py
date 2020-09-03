"""
routers subpackage of shaman_api package.
This subpackage implement the endpoints of the REST API.
"""
from .experiments import router as experiment_router


__all__ = ["experiment_router"]
