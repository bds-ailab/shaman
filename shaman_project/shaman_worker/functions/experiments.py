"""
This module defines the function that will launch a SHAMan experiment.
"""
# SHAMan dependency
from typing import Dict, Optional
from pydantic import BaseModel

from ..shaman_config import SHAManConfigBuilder, SHAMAN_CONFIG_TEMPLATE
from bb_wrapper.run_experiment import run

from devtools import debug
import time


async def launch_experiment(context, experiment: Dict):
    """Launches a SHAMan experiment."""
    debug(experiment)
    # Get sbatch file path
    sbatch_filepath = context["settings"].join_path("ui_sbatch.sbatch")
    # Write sbatch content
    sbatch_filepath.write_text(experiment["sbatch"])
    # Get SHAMan configuration file path
    config_filepath = context["settings"].join_path("config_shaman.yaml")
    # Create ShamanConfig object
    shaman_config = SHAManConfigBuilder(SHAMAN_CONFIG_TEMPLATE, config_filepath)
    # Build the configuration file
    shaman_config.build_configuration(experiment)
    # Launch the experiment
    debug("Running the runner !")
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
