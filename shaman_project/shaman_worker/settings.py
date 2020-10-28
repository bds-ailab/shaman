"""Define the configuration of the Redis message broker."""

from .functions import FUNCTIONS
from .events import startup, shutdown
from shaman_core.config import RedisConfig


class WorkerSettings:
    """Settings for the ARQ worker."""

    # Specify function to run on startup
    on_startup = startup
    # Specifiy function to run on shutdown
    on_shutdown = shutdown
    # Get Redis settings from environment variables
    redis_settings = RedisConfig().settings()
    # Declare worker functions
    functions = FUNCTIONS
