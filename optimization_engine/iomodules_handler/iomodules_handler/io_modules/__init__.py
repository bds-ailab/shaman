"""Setup important constants for the module"""

__copyright__ = """
Copyright (C) 2020 Bull S. A. S. - All rights reserved
Bull, Rue Jean Jaures, B.P.68, 78340, Les Clayes-sous-Bois, France
This is not Free or Open Source software.
Please contact Bull S. A. S. for details about its license.
"""

import os

__PACKAGE_PATH__ = os.path.dirname(os.path.realpath(__file__))
__DEFAULT_CONFIGURATION__ = os.path.join(__PACKAGE_PATH__, "config/iomodules_config.yaml")

from .accelerators import SROAccelerator
from .accelerators import SBBSlurmAccelerator
