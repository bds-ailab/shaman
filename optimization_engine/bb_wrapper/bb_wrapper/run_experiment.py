"""This script is the entrypoint for little-shaman, by defining a main function which launches the
exploration process.
It ties together all the components required by the application.

It defines two functions:
- parse_args: this function relies on the argparse library to parse the user's imput
- main: this function uses the arguments parsed from the user's input in order to initialize an
    object of class ShamanExperiment and run the experiment.
"""

__copyright__ = """
Copyright (C) 2019-2020 Bull S. A. S. - All rights reserved
Bull, Rue Jean Jaures, B.P.68, 78340, Les Clayes-sous-Bois, France
This is not Free or Open Source software.
Please contact Bull S. A. S. for details about its license.
"""
import os
import time
import argparse

from little_shaman import __DEFAULT_CONFIGURATION__
from little_shaman import __CURRENT_DIR__
from little_shaman.shaman_experiment import ShamanExperiment


# Parse the user input:
def parse_args(args_in=None):
    """This function relies on the argparse module to collect the user's input.

    Returns:
        An object which contains as attributes the argument values.
    """
    parser = argparse.ArgumentParser(description='Little SHAMan')
    parser.add_argument('--accelerator_name', type=str, choices=["fiol", "sbb_slurm"],
                        help='The name of the accelerator to use.')
    parser.add_argument('--nbr_iteration', type=int,
                        help='The max number of iterations for optimization.')
    parser.add_argument('--sbatch_file', type=str,
                        help='The name of the sbatch file to run.')
    # Experiment name, defaults to experiment_timestamp
    parser.add_argument('--experiment_name', type=str, default=f"experiment_{round(time.time())}",
                        help="The name of the experiment as saved in the database")
    parser.add_argument('--sbatch_dir', type=str, default=None,
                        help="The folder where the sbatch will be written to.")
    parser.add_argument('--slurm_dir', type=str, default=None,
                        help="The folder that will contain the slurm outputs.")
    parser.add_argument('--result_file', type=str, default=None,
                        help="The file that will contain the results.")
    parser.add_argument('--configuration_file', type=str, default=None,
                        help="The file that will be used as configuration.")

    args = parser.parse_args(args_in)

    # Build absolute path for the result / slurm output files
    if args.result_file:
        args.result_file = os.path.join(__CURRENT_DIR__, args.result_file)
    if args.slurm_dir:
        args.slurm_dir = os.path.join(__CURRENT_DIR__, args.slurm_dir)
    if args.sbatch_dir:
        args.sbatch_dir = os.path.join(__CURRENT_DIR__, args.sbatch_dir)
    if args.configuration_file:
        args.configuration_file = os.path.join(
            __CURRENT_DIR__, args.configuration_file)
    else:
        args.configuration_file = __DEFAULT_CONFIGURATION__
    return args


def run(accelerator_name,
        nbr_iteration,
        sbatch_file,
        experiment_name,
        configuration_file,
        sbatch_dir=None,
        slurm_dir=None,
        result_file=None):
    """Run a SHAMan experiment given this input.

    Args:
        accelerator_name (str): The name of the accelerator to use.
        nbr_iteration (int): The maximal number of iterations to run the experiment for.
        sbatch_file (str): The path to the sbatch file.
        experiment_name (str): The name to give the experiment.
        sbatch_dir (str): The directory to store the sbatch.
        slurm_dir (str): The directory to write the slurm outputs.
        result_file (str): The result file.
        configuration_file (str): The configuration file.
    """
    # Create an experiment by initializing an object of class ShamanExperiment
    experiment = ShamanExperiment(accelerator_name,
                                  nbr_iteration,
                                  sbatch_file,
                                  experiment_name,
                                  sbatch_dir,
                                  slurm_dir,
                                  result_file,
                                  configuration_file=configuration_file)
    # Log the beginning of the experiment
    print(f"Lauching experiment {experiment_name}")
    # Catch possible keyyboard interrupt
    try:
        # Launch the experiment
        experiment.launch()
        # Save the experiment
        experiment.end()
        # Clean up the experiment
        experiment.clean()
    except KeyboardInterrupt:
        experiment.stop()
    except Exception as e:
        print(e)
        experiment.fail()


def main(args_in=None):
    """Runs the experiment

    Args:
        args_in (list): the input arguments with their option.
    """
    args = parse_args(args_in)

    run(args.accelerator_name,
        args.nbr_iteration,
        args.sbatch_file,
        args.experiment_name,
        args.configuration_file,
        args.sbatch_dir,
        args.slurm_dir,
        args.result_file)


if __name__ == "__main__":
    main()
