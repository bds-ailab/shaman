# The SHAMan application

<img src="https://github.com/SphRbtHyk/shaman_project/blob/next/frontend/assets/little_shaman.png" width="130">

![Tests](https://github.com/SphRbtHyk/shaman_project/workflows/Unittests/badge.svg)
![flake-8](https://github.com/SphRbtHyk/shaman_project/workflows/Flake8/badge.svg)
![Docker builds](https://github.com/SphRbtHyk/shaman_project/workflows/Docker%20builds/badge.svg)

SHAMan is an out-of-the-box Web application to perform black-box auto-tuning of custom computer components running on a distributed system, for an application submitted by a user. It relies on black-box auto-tuning to find the components' parametrization that are the most efficient in terms of execution time.

# Main goal and features

This framework integrates three state-of-art heuristics, as well as noise reduction strategies to deal with the possible interference of shared resources for large scale HPC systems, and pruning strategies to limit the time spent by the optimization process.

Compared to already existing softwares, it provides these main advantages:

:rocket: **Accessibility**: the optimization engine is accessible either through a Web Interface or a CLI

:rocket: **Easy to extend**: the optimization engine uses a plug-in architecture and the development of the heuristic is thus the only development cost

:rocket: **Integrated within the HPC ecosystem**: the framework relies on the Slurmworkload manager to run HPC applications. The microservice architectureenables it to have no concurrent interactions with the cluster and the appli-cation itself.

:rocket: **Flexible for a wide range of use-cases**: new components can be registeredthrough a generalist configuration file.

:rocket: **Integrates noise reduction strategies**: because of their highly dynamic natureand the complexity of applications and software stacks, HPC systems aresubject to many interference when running in production, which results in a different performance measure for each run even with the same system’sparametrization. Noise reduction strategies are included in the framework toperform well even in the case of strong interference.

:rocket: **Integrates pruning strategies**: runs with unsuited parametrization are aborted,to speed-up the convergence process

# Basic architecture

# Installation

SHAMan can be installed in a containerized environment, as several docker containers run with `docker-compose`. However, this type of install is only suitable for demo purpose: it is not possible to infer proper performance metrics from hardwares or softwares running in a containerized environment. To deal with production installs, we provide a ansible playbook to deploy the services of the application that require the system's full performance.

In both cases, the latest version of SHAMan pust be pulled by cloning this repository. The user must then move to the cloned repository.

## Demo deployment

:warning: This version requires a working install of docker and docker compose.

The demo version of the application can be run by calling:

```
docker-compose -f demo-compose.yml up
```

## Production deployment

:warning: This version requires a working install of docker, the possibility to install Python libraries on a node that has access to the Slurm cluster (login node or compute node).

An ansible playbook is available for deployment in production.

# Registering a new component

# Creating an experiment

# Documentation

More details about the available heuristics, the architecture and how it works is available in the documentation.

# Maintainers

# Contributing
