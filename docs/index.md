<img src="./assets/little_shaman.png" width="150">

# SHAMan: Smart HPC Application MANager

SHAMan is an out-of-the-box framework to perform **black-box auto-tuning of custom computer components** running on **a distributed system**, for a given application launched through the **Slurm workload manager**. It relies on state-of-the-art black-box algorithms to find the components' parametrization that are the most efficient in terms of execution time. It also integrates **noise reduction strategies** to deal with the possible interference of shared resources for large scale HPC systems, and **pruning strategies** to limit the time spent by the optimization process.

Compared to already existing softwares, it provides these main advantages:

:rocket: **Accessibility**: the optimization engine is accessible either through a Web Interface or a CLI

:rocket: **Easy to extend**: the optimization engine uses a plug-in architecture and the development of the heuristic is thus the only development cost

:rocket: **Integrated within the HPC ecosystem**: the framework relies on the Slurmworkload manager to run HPC applications. The microservice architectureenables it to have no concurrent interactions with the cluster and the appli-cation itself.

:rocket: **Flexible for a wide range of use-cases**: new components can be registeredthrough a generalist configuration file.

:rocket: **Integrates noise reduction strategies**: because of their highly dynamic natureand the complexity of applications and software stacks, HPC systems aresubject to many interference when running in production, which results in a different performance measure for each run even with the same system’sparametrization. Noise reduction strategies are included in the framework toperform well even in the case of strong interference.

:rocket: **Integrates pruning strategies**: runs with unsuited parametrization are aborted,to speed-up the convergence process
