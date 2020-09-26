import os
from .shaman_config import ShamanConfig


FILE_DIR = os.path.dirname(os.path.realpath(__file__))
SHAMAN_CONFIG_TEMPLATE = os.path.join(FILE_DIR, "shaman_config_template.cfg")
