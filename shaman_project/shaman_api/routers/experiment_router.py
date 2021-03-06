# Copyright 2020 BULL SAS All rights reserved
from typing import Any, Callable, get_type_hints, Optional
from fastapi import APIRouter
from loguru import logger
from arq import create_pool
from arq.connections import RedisSettings, ArqRedis
from ..databases.shaman import ExperimentDatabase

from shaman_core.config import RedisConfig


class ExperimentRouter(APIRouter):
    def __init__(self, *args, **kwargs):
        db = ExperimentDatabase()
        self.db = db
        self.redis: Optional[ArqRedis] = None
        on_startup = set(kwargs.get("on_startup", []))
        on_startup.add(db.connect)
        on_startup.add(self.connect_redis)
        on_shutdown = set(kwargs.get("on_shutdown", []))
        on_shutdown.add(db.close)
        on_shutdown.add(self.close_redis)
        kwargs["on_startup"] = list(on_startup)
        kwargs["on_shutdown"] = list(on_shutdown)
        super().__init__(*args, **kwargs)

    def add_api_route(
        self, path: str, endpoint: Callable[..., Any], **kwargs: Any
    ) -> None:
        """Overrides the route decorator logic to use the annotated return type
        as the `response_model` if unspecified."""
        if kwargs.get("response_model") is None:
            kwargs["response_model"] = get_type_hints(endpoint).get("return")
        return super().add_api_route(path, endpoint, **kwargs)

    async def connect_redis(self):
        logger.info(
            "Connecting to redis on host"
            f"{RedisConfig().redis_host}:{RedisConfig().redis_host}"
        )
        settings = RedisSettings(
            host=RedisConfig().redis_host, port=RedisConfig().redis_port
        )
        self.redis = await create_pool(settings)
        logger.info(f"Connected to redis server with settings {settings}.")

    async def close_redis(self):
        self.redis.close()
        logger.info("Closed connection to redis server.")
