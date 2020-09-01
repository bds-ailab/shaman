"""
Setup file for the IOModules handler.
"""

__copyright__ = """
Copyright (C) 2019 Bull S. A. S. - All rights reserved
Bull, Rue Jean Jaures, B.P.68, 78340, Les Clayes-sous-Bois, France
This is not Free or Open Source software.
Please contact Bull S. A. S. for details about its license.
"""

import os
import glob
from setuptools import setup, find_packages

WHEEL_VERSION = '2.0'
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


setup(
    name="iomodules_handler",
    version=VERSION,
    description="Python package to manipulate the IO accelerators developed by Atos"
                "BDS R&D Data Management",
    long_description=readme(),
    author='BDS Data Management',
    author_email='bds-datamanagement@atos.net',
    packages=find_packages(exclude=["tests"]),
    install_requires=requirements(),
    python_requires=">=3.6",
    include_package_data=True,
    extras_require={"dev": ["pytest", "pytest-coverage", "black", "pylint"]},
    entry_points={
        'console_scripts': [
            'iomodules-handler-configure = iomodules_handler.tools.configuration_builder:main',
        ],
    },
)

# Ask the user to call the configuration command
print("\n")
print("\033[1;31;40m ----- WARNING: You need to configure the module by calling iomodules-handler-configure command ----- \033[1;31;40m")
print("\n")