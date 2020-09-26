from pathlib import Path
from .shaman_config import ShamanConfig, ShamanSettings


SHAMAN_CONFIG_TEMPLATE = Path(__file__).parent / "shaman_config_template.cfg"


__all__ = ["ShamanConfig", "ShamanSettings", "SHAMAN_CONFIG_TEMPLATE"]
