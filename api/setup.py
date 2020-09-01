"""
Installation file for the SHAMan API.
"""

#!/usr/bin/env python

__copyright__ = """
Copyright (C) 2020 Bull S. A. S. - All rights reserved
Bull, Rue Jean Jaures, B.P.68, 78340, Les Clayes-sous-Bois, France
This is not Free or Open Source software.
Please contact Bull S. A. S. for details about its license.
"""

import os
import glob

from setuptools import setup, find_packages

WHEEL_VERSION = '1.0'
VERSION = os.environ['RPM_VERSION'] if 'RPM_VERSION' in os.environ else WHEEL_VERSION


def readme():
    """
    Return content of README file as string
    """
    if glob.glob("README.md"):
        with open('README.md') as readmefile:
            return readmefile.read()
    else:
        return ""


def requirements():
    """
    List requirements from requirements.txt file
    """
    if glob.glob("requirements.txt"):
        with open('requirements.txt') as requirements_file:
            return [req.strip() for req in requirements_file.readlines()]
    else:
        return []


setup(name='shaman_api',
      version=VERSION,
      url='',
      license='',
      description='REST API for SHAMan Web application',
      long_description=readme(),
      author='BDS Data Management',
      author_email='bds-datamanagement@atos.net',
      packages=find_packages(exclude=["tests", "integration_tests"]),
      install_requires=requirements(),
      entry_points={
        'console_scripts': [
            'shaman-api=shaman_api.cli:cli',
        ],
    }
      )
