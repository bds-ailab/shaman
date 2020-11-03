# Registering a component

To use SHAMan, you must first **register a component** to be optimized, by specifying how it is used conjointely with an application, its different parameters and their possible values.

!!! warning
    There is no component registered by default with SHAMan, and **the application cannot run without a registered component**. An error message will be displayed in the Web UI if there is no registered component.

## What is a component ?

A component is defined in SHAMan as **an entity**, that **can be launched through a sbatch**,  with **parameters that can be optimized**. Examples of such components are I/O accelerators (see the cookbook on [auto-tuning of I/O accelerators](../cookbooks/ioaccelerators.md)) and Message Passing Interface.

## Configuration file

To register a component, you must write a YAML file describing the component and its different characterstics. This YAML file must describe how the component is launched and declares its different parameters and how they must be used to parametrize the component. After the installation process, the components are available in the launch menu of the Web interface and can be used through the command line interface.

The basic structure of the YAML file is a series of dictionaries describing the different available components. There is no limit on the possible number of components.

``` yaml
components:
  component_1:
    ...
  component_2:
    ...
```

Within the description of each component, the configuration file is separated into two distinct parts.

### Specifying how to launch the component

``` yaml hl_lines="3 4 5 6"
components:
  component_1:
    plugin: example_1
    command: example_cmd
    ld_preload: example_lib
    header: example_header
    parameters:
      ...

  component_2:
  ...
```

Several ways can be (non-exclusively) used by SHAMan to launch the component:

* `plugin`: added as an argument of the submission command line.
In the example above, the following command is used ```sbatch --example_1 my_sbatch```

* `command`: added on top of the sbatch file.
In the example above, the top of the program is appended by adding `example_cmd` as well as the `cmd_var` argument (see next section).

* `ld_preload`: positions the variable as value for `LD_PRELOAD`.
In the example above, the top of the program is appended by adding `LD_PRELOAD=ld_preload` on top of the sbatch file. 

An additional parameter is the `header`, which specifies a command to be run between each optimization run. An example can be a system call to clean the cache, to ensure independence between runs.

### Description of the component's parameters

The second part of the component configuration file deals with the description of the parameters of the components. The parameters can either be passed as:

- Environment variables (`env_var=True`)
- A variable appended to the command line variable (`cmd_var=True`) with an optional flag and suffix
- A variable passed on the job's command line (`cli_var=True`) with an optional flag and suffix

Each parameter must have a `default` value, as well as a `type` (:warning: for now, only integer values are supported).

``` yaml hl_lines="7 8 9 10 11 12 13 14 15 16 17 18 19 20"
components:
  component_1:
    cli_command: example_1
    header: example_header
    command: example_cmd
    ld_preload: example_lib
    parameters:
      param_1:
        env_var: True
        type: int
        default: 1
      param_2:
        cmd_var: True
        type: int
        default: 100
        flag: test
      param_3:
        cli_var: True
        type: int
        default: 1

  component_2:
  ...
```

### Dummy example

If we consider the configuration file describing `component_1`:

``` yaml
components:
  component_1:
    cli_command: example_1
    header: example_header
    command: example_cmd
    ld_preload: example_lib
    parameters:
      param_1:
        env_var: True
        type: int
        default: 1
      param_2:
        cmd_var: True
        type: int
        default: 100
        flag: test
        suffix: M
      param_3:
        cli_var: True
        type: int
        default: 1
```

and the application described by the sbatch file `my_sbatch.sbatch`

``` shell
#!/bin/bash
#SBATCH --job-name=TestJob
#SBATCH --ntasks=3
hostname
```

SHAMan will optimize the application by calling repeatedly the script (here with default parameters):

``` shell
#!/bin/bash
#SBATCH --job-name=TestJob
#SBATCH --ntasks=3
example_cmd --test=100M
LD_PRELOAD=ld_preload
header
hostname
```

through the launch command line `sbatch --component_1 param_3=1 my_sbatch.sbatch` and with the environment variable `param_1=1`.


For a concrete example of a configuration file, refer to the examples presented in the [cookbook](../cookbooks/ioaccelerators.md)

## Install command

!!! tip
    If you are running the application entirely containerized, the install command must be run either in the API docker container. Else, the command must be run either in the API docker or directly on the login node where the Python library is installed.


The component can be registered once the configuration file has been written, by calling the command:
``` shell
shaman-install configuration.yaml
```

!!! Warning
    Running the command **erases** the current data.

## Example

Examples can be found in the [cookbook example](../cookbooks/ioaccelerators.md).
