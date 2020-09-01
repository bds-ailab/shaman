"""
routers subpackage of shaman_api package.
This subpackage implement the endpoints of the REST API.
"""
from .experiments import router as experiment_router
from .io_durations import router as ioi_router


__all__ = ["experiment_router", "ioi_router"]
