# Copyright 2020 BULL SAS All rights reserved
"""This script is the entrypoint for little-shaman, by defining a main function
which launches the exploration process. It ties together all the components
required by the application.

It defines a single function main which runs the experiment.
"""


from typer import Typer, Option
from loguru import logger

from .shaman_experiment import SHAManExperiment

cli = Typer(add_completion=False)


def run(
    component_name: str = Option(...,
                                 help="The name of the component to tune"),
    nbr_iteration: int = Option(
        ..., help="The maximal number of iterations to run the experiment for."
    ),
    sbatch_file: str = Option(..., help="The path to the sbatch file"),
    experiment_name: str = Option(..., help="The name to give the experiment"),
    configuration_file: str = Option(
        ..., help="The path to the configuration file"),
    sbatch_dir: str = Option(None, help="The directory to store the sbatch"),
    slurm_dir: str = Option(
        None, help="The directory to write the slurm outputs"),
    result_file: str = Option(None, help="The path to the result file."),
) -> None:
    """Run an optimization experiment."""
    # Create an experiment by initializing an object of class ShamanExperiment
    logger.debug(
        f"Experiment parametrization: Component name {component_name} | \
        Nbr iteration {nbr_iteration} | \
        Sbatch file {sbatch_file} | \
        Sbatch dir {sbatch_dir} | \
        Slurm dir {slurm_dir} | \
        Result file {result_file} | \
        Configuration file {configuration_file}"
    )
    experiment = SHAManExperiment(
        component_name=component_name,
        nbr_iteration=nbr_iteration,
        sbatch_file=sbatch_file,
        experiment_name=experiment_name,
        sbatch_dir=sbatch_dir,
        slurm_dir=slurm_dir,
        result_file=result_file,
        configuration_file=configuration_file,
    )
    # Log the beginning of the experiment
    logger.info(f"Running experiment {experiment_name}")

    # Catch possible keyyboard interrupt
    try:
        logger.info(f"Launching experiment {experiment_name}")
        # Launch the experiment
        experiment.launch()
        logger.debug(f"Successful ending for experiment {experiment_name}")
        # Save the experiment
        experiment.end()
        logger.debug(f"Cleaning data for experiment {experiment_name}")
        # Clean up the experiment
        experiment.clean()
        logger.debug(f"Experiment {experiment_name} was run successfully.")
    except KeyboardInterrupt:
        logger.info(
            f"Stopping experiment {experiment_name} through keyboard"
            "interrupt."
        )
        experiment.stop()
    except Exception as e:
        logger.critical(
            "Encountered exception while launching experiment"
            f"{experiment_name}: {e}"
        )
        experiment.fail()


cli.command()(run)


if __name__ == "__main__":
    cli()
