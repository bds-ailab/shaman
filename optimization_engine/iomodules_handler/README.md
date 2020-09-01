# IO Module handlers 

This module contains different tools to handle the IO modules developped by the <code>Data Management</code> team using Python. The main feature of this package is the ability to run a sbatch file with the IO Module setup with a given set of parameters.

## Supported products

For now, two IO Modules are supported:
- The FIOL libraries
- The Smart Burst Buffer using the slurm plugins.


## Install and configure

The iomodules_handler can be installed using either:

```
python setup.py install
```

or

```
pip install .
```

#### Interactive install
Once the package is installed, the <code>iomodules-handler-configure</code> command **must be run** to finish the installation procedure. If not, **the package will not function**. 

When running the command:
```
iomodules-handler-configure
```
a prompt opens. For each accelerator available in the library, the user is asked whether he wants to configure the accelerator or whether he wants to skip it. Of course, if the accelerator is not installed or available, its configuration procedure must be skipped. Make sure to specify a value of the right type (in the sens of Python types) for each parametrization as the install will fail otherwise.

This configuration can be accessed at any time in the file <code>iomodules_handler/accelerators/config/iomodules_config.cfg</code>.

#### Non-interactive install
This step can be bypassed by directly adding a configuration file in <code>iomodules_handler/accelerators/config/iomodules_config.cfg</code>. There is **no checking on the configuration file**, so make sure that the format is respected, else the package will not function properly. Also, this bypasses the checking of the installation of the accelerators, so make sure that the correct rpm are installed.

## Running the tests

This package comes with two types of tests:
- Unit-tests (in the <code>tests</code> folder) which tests the features of the Python code
- Integration tests (in the <code>tests_integration</code> folder) which tests how the package behaves when interacting with the different IO modules. They require:
    - An install of the IO modules which are supported by the library
    - RHEL 7.0
    - Slurm

## Quickstart

For each of the supported accelerator, this module provides ways to run a sbatch file with the accelerator set-up with a given set of parameters.

For example, to run the file <code>test_sbatch.sbatch</code> with the <code>SRO</code> accelerator, with the default parameters, I use the following command:

```python
from iomodules_handler.io_module.accelerators.sro import SROAccelerator

fiol_acc = SROAccelerator()
fiol_acc.submit_sbatch("test_sbatch.sbatch")
```

This then runs the application with the FIOL accelerator enabled.

## Parametrization of the accelerators

The information about the parametrization of the accelerators is available in the file <code>iomodules_handler/config/iomodules_config.yaml</code>. When parametrizing your accelerator, you must respect the following rules:

### Optional variables
By default, all variables are mandatory when setting up the accelerator, except if the configuration indicates them to be **optional** or having a **default value**. If you want to add a default value to the accelerator, you can add a **default** flag to the parameter of your choice.

### Environment variables

Parameters which have a **var_env** flag sets to true indicates them to be environment variables. They will be passed to the environment at runtime when running the sbatch program.

### Flag variables

Parameters which have a **flag** variable will be used to build a command line property of the accelerator.

## The different IOModules

### The abstract classes: IOModules and Accelerator

The goal of these abstract classes is to provide a common interface and common methods for all available IO modules. The <code>IOModule</code> class is generic to any module that can be triggered when running an sbatch. The <code>Accelerator</code> class is specific to modules which require a parametrization. 

### Small Read Optimizer handler (SRO)

The <code>SROAccelerator</code> enables the use of the SRO accelerator as available in the Fast IO libraries. It functions by passing as environment variables for the execution the wanted parameters.

### SBB handlers

The <code>SBBSlurmAccelerator</code> class enables the use of a datanode using as a burst buffer *via* the flash-accelerators library. It writes as header of the sbatch file the value for the parameters of the Smart Burst Buffer, as <code>#SBB list_of_parameters</code>.


## Implementing a new Accelerators

In order to add a new accelerator to the library, it must implement:
- An <code>accelerator_name</code> property.
- A <code>setup</code> method to get the accelerator ready to run.
- A <code>kill</code> method to kill the accelerator.

## Suggestions and on-going work
Feel free to suggest new functionalities !