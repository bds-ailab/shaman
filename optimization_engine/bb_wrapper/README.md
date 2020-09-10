# The little-shaman tool

The <code>little-shaman</code> is command line interface tool to find the optimal parametrization of a sbatch for either the FIOL or the SB IO accelerator developed by the BDS R&D Data Management Team at Atos. It relies on black-box optimization fo perform the accelerator tuning, by parsing at each iteration the slurm execution time corresponding to the parametrization and using this history to suggest the next parametrization to test.

## Install

### Installation of little shaman 

> <b>WARNING</b>: <br>
> Little-shaman relies on two IOanalytics internal libraries: <br>
> - iomodules_handler
> - BBO <br>
>
> While BBO does not require any special configuration, iomodules_handler **needs** to be configured by launching the <code>iomodules-handler-configure</code> command. <br>
> Please refer to the documentation of the package for further explanation.

In order to install little-shaman, you need to run in the package repository:

```
pip install .
```

or

```
python setup.py install
```

You then need to configure the different IOModules installed on your node by running:

```
iomodules-handler-configure
```
and then configure your system accordingly.

Obviously, you'll only be able to use <code>little-shaman</code> with the accelerators available on your system.

### Setting up the mongo database

The results of a <code>little-shaman</code> optimization are stored in a mongo database once the optimization is over. A mongo instance must thus be started *via* <code>docker</code>. An example of starting script is provided in the <code>run_mongo.example.sh</code>. The proper values for the volume and the UID of the user must be specified. You can then check that the database is properly running by running:
 
```
docker ps
```

And checking that a container called <code>mongo-shaman</code> is running.

We'll see in the configuration section that this database can also be configured.

## Running little-shaman

### Quickstart

Once the installation procedure is over, you'll be able to run the command line. You'll need at the minimum:
- The accelerator you want to optimize 
- The *sbatch* containing the application you want to optimize
- The number of iterations you want to run the application for

You can then call:

```
little-shaman 
--accelerator [fiol|sbb] 
--sbatch my_sbatch.sbatch 
--budget my_budget
```

### Other parameters

Other than the three mandatory arguments, two optional arguments can be specified:
- Whether or not the slurm outputs should be stored in a separate folder (by default, the slurm outputs are deleted): flag <code>--slurm_outputs name_of_folder</code>
- Whether or not a (by default, such a file is not created and the result goes straight to the database): flag <code>--result_file name_of_file</code>
- The configuration file to use (by default, corresponds to the <code>config.cfg</code> file in the <code>little_shaman</code> folder): flag <code>--configuration-file</code>.
- The name to give the experiment in the database (by default, it is set to <code>experiment_{timestamp}</code>)

## In depth description

### Technical description

Technically speaking, <code>little-shaman</code> is a simple wrapper built upon the modules <code>iomodules_handler</code> and  <code>BBO</code>. 

The <code>BBOptimizer</code> class shipped with <code>BBO</code> takes as input an object (which is treated as a black-box) with a method <code>compute</code>. In the case of <code>little-shaman</code>, this object is of a class <code>AccBlackBox</code> which is built upon <code>iomodules_handler</code>. It initializes an object of class <code>iomodules_handlers.Accelerator</code> with a parametrization. The compute method of this class calls the <code>submit_sbatch</code> and returns the slurm times associated with the sbatch and the parametrization. If it is not already the case, the <code>time</code> command is added to the sbatch in order to time the duration of the command.

The <code>BBOptimizer</code> then optimizes this object relatively to the parametrization of the accelerator.

At the end of the experiment, the summary is sent to a mongo-database called <code>shaman_db</code> (this name is configurable):
- <code>experiment_start</code>: the date the experiment was started
- <code>parameters</code>: the evaluated parameters, as a list
- <code>execution_time</code>: the execution time corresponding to the parametrization, as a list
- <code>accelerator</code>: the name of the accelerator used for the experiment
- <code>elapsed_time</code>: the total elapsed time of the experiment
- <code>experiment_name</code>: the name of the experiment
- <code>jobids</code>: the list of the jobids that have been submitted during the experiment

### Configuring little-shaman

While <code>little-shaman</code> is shipped with a default configuration file (<code>config.cfg</code>), finer tuning of the tool is possible to tailor particular users' needs. You can either modify the default configuration file directly in the package or provide a custom configuration file.

The configuration is separated in 5 parts and we'll detail each of them in the following sections:

#### EXPERIMENT

The EXPERIMENT section of the configuration describes several characteristics of the experiment. For now, the only option is whether or not the runs are instrumented using the IOI monitoring system, by setting the with_ioi variable to a boolean. By default, the runs are not monitored.

#### BBO

The BBO section of the configuration describes the heuristic used to perform the tuning. **It simply consists in listing out the different arguments that will be given to the <code>BBOptimizer</code>**.

> To learn more about the in-depth workings of BBO, please refer to the extensive documentation of this package.

#### FIOL

The goal of this section is to specify the possible parameter value that will be explored by the optimizer. It is used to specify both a range and a granularity for the evaluation of the parameters.

#### SBB

Similarly to the <code>FIOL</code> section, this section gives the range of the parameters, this time for the SBB, that will be used and the resolution of the grid to explore.

#### MONGODB

This section configures the access to the mongo database, by giving:
- The name of the host
- The value for the port
- The name of the database to connect to

## Further work

On-going work include:
- Fixing some of the TO-DOs included in the code
- Better handling of slurm failures
- Support for string parameters
- Logging