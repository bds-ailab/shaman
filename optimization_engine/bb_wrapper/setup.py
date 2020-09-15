"""
Setup file for the little-shaman module.
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
    name="shaman",
    version=VERSION,
    description="Python package to automatically tune the accelerators"
                "developed by Atos BDS R&D Data Management for a given"
                "application",
    long_description=readme(),
    author='BDS Data Management',
    author_email='bds-datamanagement@atos.net',
    packages=find_packages(exclude=["tests"]),
    install_requires=requirements(),
    python_requires=">=3.6",
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'shaman = bb_wrapper.run_experiment:cli',
        ],
    },
)
