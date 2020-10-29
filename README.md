# The SHAMan project

![Tests](https://github.com/SphRbtHyk/shaman_project/workflows/unittests/badge.svg)
![flake-8](https://github.com/SphRbtHyk/shaman_project/workflows/flake8/badge.svg)
![Docker builds](https://github.com/SphRbtHyk/shaman_project/workflows/Docker%20builds/badge.svg)

The SHAMan project is the result of my research works during my PhD on the auto-tuning of I/O accelerators.
Its an optimization framework to find the optimum parametrization of an I/O accelerator for HPC applications.

It is composed of three modules: - **bbo**: Contains the black-box optimization. - **iomodules_handler**: A Python interface for manipulating I/O accelerators. - **little_shaman**: The Python module which performs the optimization of I/O accelerators.

## Installing the different modules

Each module comes with a <code>setup.py</code> file, and can be installed running <code>python setup.py install</code> in the corresponding folder.
An easier way to proceed is to rely on the Makefile. You can call the command <code>make install-{packagename}</code>, which creates a virtualenv where the package is installed. All you have to do to source the environment: <code>source .venv/bin/activate</code>

## Continuous integration

For now, there is no continuous integration pipeline associated with the project and the projects different stats are not available on a dashboard.
To mitigate this problem and to make reviewing easy, the package comes with a Makefile and a <code>ci</code> target. All you have to do is clone the repository, then call <code>make ci</code> in the main folder. This will run the unit tests, compute their coverages and return the Pylint scores of the project.
