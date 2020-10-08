"""Setsup the settings of the SHAMan module:
- The host of the API
- The port of the API
- The endpoint of the components
"""
from pydantic import BaseSettings


class SHAManSettings(BaseSettings):
    api_host: str = "api"
    api_port: int = 5000
    component_endpoint: str = "components"
