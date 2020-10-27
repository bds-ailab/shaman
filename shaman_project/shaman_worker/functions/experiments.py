"""
This module defines the function that will launch a SHAMan experiment.
"""
import pathlib

# SHAMan dependency
from typing import Dict
from loguru import logger
from ..shaman_config import SHAManConfigBuilder, SHAMAN_CONFIG_TEMPLATE
from bb_wrapper.run_experiment import run
from shaman_core.logger import setup_logger_from_settings, LoggingSettings


async def launch_experiment(context, experiment: Dict):
    """Launches a SHAMan experiment."""
    # Setup logger
    log_path = pathlib.Path.cwd() / "logs" / "shaman.log"
    logging_setting = LoggingSettings(filepath=log_path)
    setup_logger_from_settings(logging_setting)

    logger.info(
        f"Requested worker to run an experiment with parametrization: {experiment}"
    )
    # Get sbatch file path
    sbatch_filepath = context["settings"].join_path("ui_sbatch.sbatch")
    # Write sbatch content
    sbatch_filepath.write_text(experiment["sbatch"])
    logger.debug(f"Writing sbatch at {sbatch_filepath}")
    # Get SHAMan configuration file path
    config_filepath = context["settings"].join_path("config_shaman.yaml")
    # Create ShamanConfig object
    shaman_config = SHAManConfigBuilder(SHAMAN_CONFIG_TEMPLATE, config_filepath)
    # Build the configuration file
    shaman_config.build_configuration(experiment)
    # Launch the experiment
    logger.debug("Calling run function.")
    run(
        experiment_name=experiment["experiment_name"],
        component_name=experiment["component_name"],
        nbr_iteration=experiment["nbr_iteration"],
        sbatch_file=str(sbatch_filepath),
        configuration_file=str(config_filepath),
        sbatch_dir=None,
        slurm_dir=None,
        result_file=None,
    )
