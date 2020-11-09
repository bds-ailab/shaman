# Auto-tuning of I/O accelerators

In this cookbook, we optimize a pure software I/O acceleration library, called `FIOL` developed by [Atos](http://atos.net), for an I/O benchmark. This accelerator relies on a dynamic data preload strategy to prefetch in memory chunks of files that are regularly accessed, in order to speed-up pseudo-random file accesses. The FIOL accelerator is **highly sensitive to its parametrization**, as a poorly set parametrization can trigger too many prefetches, slowing down the application, or too little, which limits the speed-up potential of the accelerator. It is important to find the right balance, in order to prefetch only zones of the file that will be accessed again.

## Configuration file

The following configuration file can be used to register the `FIOL` component.
``` yaml
components:
  small_read_optimizer:
    cli_command: fastio=yes
    parameters:
      sequence_length:
        env_var: True
        type: int
        default: 100
      binsize:
        env_var: True
        type: int
        default: 1048576
      cluster_threshold:
        env_var: True
        type: int
        default: 2
      prefetch_size:
        env_var: True
        type: int
        default: 20971520
```

It is launched through the slurm plugin `fastio=yes` and has four variables that can be passed as environment variables.

## Experiment example

We use the Web interface to launch an experiment with the `FIOL` experiment. Based on previous works, we use genetic algorithms.

TODO screenshot