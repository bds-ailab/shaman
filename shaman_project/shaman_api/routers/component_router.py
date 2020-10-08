from typing import Any, Callable, get_type_hints
from fastapi import APIRouter
from ..databases.shaman import ExperimentDatabase
from ..logger import get_logger


logger = get_logger("component_router")


class ComponentRouter(APIRouter):
    """Router that will contain the endpoints relative to the components."""

    def __init__(self, *args, **kwargs):
        db = ExperimentDatabase()
        self.db = db
        on_startup = set(kwargs.get("on_startup", []))
        on_startup.add(db.connect)
        on_shutdown = set(kwargs.get("on_shutdown", []))
        on_shutdown.add(db.close)
        kwargs["on_startup"] = list(on_startup)
        kwargs["on_shutdown"] = list(on_shutdown)
        super().__init__(*args, **kwargs)

    def add_api_route(
        self, path: str, endpoint: Callable[..., Any], **kwargs: Any
    ) -> None:
        """
        Overrides the route decorator logic to use the annotated return type as the `response_model` if unspecified.
        """
        if kwargs.get("response_model") is None:
            kwargs["response_model"] = get_type_hints(endpoint).get("return")
        return super().add_api_route(path, endpoint, **kwargs)
