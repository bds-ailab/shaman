"""This script is the entrypoint for little-shaman, by defining a main function which launches the
exploration process.
It ties together all the components required by the application.

It defines a single function main which runs the experiment.
"""

import os
import time
from typer import Typer, Option

from .shaman_experiment import SHAManExperiment

cli = Typer(add_completion=False)


def run(component_name: str = Option(..., help="The name of the component to tune"),
        nbr_iteration: int = Option(...,
                                    help="The maximal number of iterations to run the experiment for."),
        sbatch_file: str = Option(..., help="The path to the sbatch file"),
        experiment_name: str = Option(...,
                                      help="The name to give the experiment"),
        configuration_file: str = Option(...,
                                         help="The path to the configuration file"),
        sbatch_dir: str = Option(
        None, help="The directory to store the sbatch"),
        slurm_dir: str = Option(
        None, help="The directory to write the slurm outputs"),
        result_file: str = Option(None, help="The path to the result file.")) -> None:
    """Run an optimization experiment.
    """
    # Create an experiment by initializing an object of class ShamanExperiment
    experiment = SHAManExperiment(component_name=component_name,
                                  nbr_iteration=nbr_iteration,
                                  sbatch_file=sbatch_file,
                                  experiment_name=experiment_name,
                                  sbatch_dir=sbatch_dir,
                                  slurm_dir=slurm_dir,
                                  result_file=result_file,
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


cli.command()(run)


if __name__ == "__main__":
    cli()
