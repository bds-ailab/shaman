"""
Define the configuration of the Redis message broker.
"""
from pydantic import BaseSettings
from arq.connections import RedisSettings
from .functions import FUNCTIONS
from .events import startup, shutdown


class RedisConfig(BaseSettings):
    """
    Defines the configuration of Redis.
    """

    host: str = "redis"
    port: int = 6379

    def settings(self):
        return RedisSettings(host=self.host, port=self.port)

    class Config:
        env_prefix = "REDIS_"
        case_sensitive = False


class WorkerSettings:
    """
    Settings for the ARQ worker
    """

    # Specify function to run on startup
    on_startup = startup
    # Specifiy function to run on shutdown
    on_shutdown = shutdown
    # Get Redis settings from environment variables
    redis_settings = RedisConfig().settings()
    # Declare worker functions
    functions = FUNCTIONS
