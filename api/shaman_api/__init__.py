"""
Shaman API package.

Rest API written in Python using FastAPI framework
"""
from .app import app
from .cli import cli

__all__ = ["app", "cli"]
