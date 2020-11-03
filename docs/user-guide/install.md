# Installing SHAMan

SHAMan can be installed in a containerized environment, as several docker containers run with `docker-compose`. However, this type of install is only suitable for demo purpose: it is not possible to infer proper performance metrics from hardwares or softwares when the optimization engine is running in a containerized environment. To deal with production installs, we provide a ansible playbook to deploy the services of the application that require the system's full performance.

In both cases, the latest version of SHAMan pust be pulled by cloning this repository. The user must then move to the cloned repository.

## Deployment for demonstration purpose

!!! warning
    This deployment requires a working instance of **docker** and **docker-compose**.

The demo version of the application can be run by calling:

```
docker-compose -f demo-docker-compose.yml up
```

This command deploys every services according to the architecture described in the [architecture](../technical-guide/architecture.md) section.

!!! tip
    To enable data persistence, a volume must be declared in the docker-compose file for the mongo database entry.

Once the application is up and running, visit `localhost:3000` and check that you can access the web interface.

## Production deployment

!!! warning
    This version requires a working install of **docker** and the possibility to install **Python libraries** on a node that has access to a **Slurm cluster** (login node or compute node).

The suggested method to deploy the application in production is to use every services in a container except for the optimization engine (see [architecture]('../technical-guide/architecture) for a detailed description of the architecture). 

To setup the containerized services run:

```
docker-compose -f prod-docker-compose.yml up
```

Once the containers are running, go to any node of your cluster that **can use sbatch to submit Slurm jobs** and source a shell file containing the following information (an example is given at deploy/example.env):

``` shell
#!/bin/bash

# The node running the API, here the adress of the node running the containers
export SHAMAN_API_HOST=...
# The host running the redis service, here the adress of the node running the containers
export SHAMAN_REDIS_HOST=...
# SHAMan will run in this directory. Make sure that this directory exists beforehand !
export SHAMAN_DIRECTORY="where_you_want_shaman_to_run"
# Where the SHAMan code is located
export SHAMAN_FOLDER="where_the_code_is_located"
```

Then run a script to run the worker:

```
./deploy/start-worker.env
```

!!! tip
    It is advised to run this script as a detached process:
    ```nohup ./deploy/start-worker.env &```

!!! tip
    If you want to run SHAMan without the Web interface (see [here](user-guide/launching.md)), you **do not need to start the worker**. 