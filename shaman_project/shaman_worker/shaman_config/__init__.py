# Copyright 2020 BULL SAS All rights reserved
from pathlib import Path
from .shaman_config import SHAManConfigBuilder

SHAMAN_CONFIG_TEMPLATE = Path(__file__).parent / "shaman_config_template.yaml"

__all__ = ["SHAMAN_CONFIG_TEMPLATE", "SHAManConfigBuilder"]
