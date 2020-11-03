# Installing SHAMan

SHAMan can be installed in a containerized environment, as several docker containers run with `docker-compose`. However, this type of install is only suitable for demo purpose: it is not possible to infer proper performance metrics from hardwares or softwares when the optimization engine is running in a containerized environment. To deal with production installs, we provide a ansible playbook to deploy the services of the application that require the system's full performance.

In both cases, the latest version of SHAMan pust be pulled by cloning this repository. The user must then move to the cloned repository.

## Deployment for demonstration purpose

!!! warning
    This deployment requires a working instance of **docker** and **docker-compose**.

The demo version of the application can be run by calling:

```
docker-compose -f demo-compose.yml up
```

This command deploys every services according to the architecture described in the [architecture](../technical-guide/architecture.md) section.

!!! tip
    To enable data persistence, a volume must be declared in the docker-compose file for the mongo database entry.

Once the application is up and running, visit `localhost:3000` and check that you can access the web interface.

## Production deployment

!!! warning
    This version requires a working install of **docker** and the possibility to install **Python libraries** on a node that has access to the Slurm cluster (login node or compute node).

An ansible playbook is available to deploy the application in a production ready mode, where every services but the optimization engine and the slurm nodes are dockerized. A configuration file, indicating the different names of the cluster nodes, must be filled out beforehand.
