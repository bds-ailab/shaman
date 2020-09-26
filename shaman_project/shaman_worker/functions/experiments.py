"""
This module defines the function that will launch a SHAMan experiment.
"""
# SHAMan dependency
from typing import Dict, Optional
from pydantic import BaseModel

from ..shaman_config import ShamanConfig, SHAMAN_CONFIG_TEMPLATE

from bb_wrapper.run_experiment import run


class ExperimentForm(BaseModel):
    """A model describing the data received from the client to launch the experiment."""

    accelerator_name: str
    nbr_iteration: int
    sbatch: str
    experiment_name: str
    heuristic: str
    initial_sample_size: int
    with_ioi: Optional[bool]
    max_step_duration: Optional[int]
    resampling_policy: Optional[str]
    fitness_aggregation: Optional[str]
    estimator: Optional[str]
    nbr_resamples: Optional[int]
    percentage: Optional[float]
    selection_method: Optional[str]
    mutation_rate: Optional[float]
    elitism: Optional[bool]
    regression_model: Optional[str]
    next_parameter_strategy: Optional[str]
    cooling_schedule: Optional[str]
    restart: Optional[str]


async def launch_experiment(context, experiment: Dict):
    """Launches a SHAMan experiment."""
    experiment = ExperimentForm(**experiment)
    # Get sbatch file path
    sbatch_filepath = context["settings"].join_path("ui_sbatch.sbatch")
    # Write sbatch content
    sbatch_filepath.write_text(experiment.sbatch)
    # Get SHAMan configuration file path
    config_filepath = context["settings"].join_path("config_shaman.cfg")
    # Create ShamanConfig object
    shaman_config = ShamanConfig(SHAMAN_CONFIG_TEMPLATE, config_filepath)
    # Build the configuration file
    shaman_config.build_configuration(experiment.dict())
    # Launch the experiment
    print("Running the runner !")
    # run(
    #     experiment_name=experiment_form.experiment_name,
    #     accelerator_name=experiment_form.accelerator_name,
    #     nbr_iteration=experiment_form.nbr_iteration,
    #     sbatch_file=str(sbatch_filepath),
    #     configuration_file=str(config_filepath),
    # )
