from pydantic import BaseModel, Field, validator
from typing import List, Dict, Optional


class MongoModel(BaseModel):
    @classmethod
    def _project(cls):
        return {key: 1 for key in cls.__fields__.keys()}


class DefaultRun(MongoModel):
    """Schema for the default run of an experiment.
    """

    execution_time: float
    job_id: int
    parameters: dict


class InitExperiment(MongoModel):
    """
    A model describing an experiment upon initialization.
    """

    experiment_name: str
    experiment_start: str
    experiment_budget: int
    accelerator: str
    experiment_parameters: Dict
    noise_reduction_strategy: Dict
    pruning_strategy: Dict
    sbatch: str


class Experiment(MongoModel):
    """
    A model describing an experiment once it has finished running.
    """

    id: str = Field(..., alias="_id")
    experiment_name: str = None
    experiment_start: str = None
    accelerator: str = None
    status: str = None

    @validator("id", pre=True)
    def convert_objectId(cls, object_id):
        return str(object_id)


class WebSocketExperiment(Experiment):
    """
    A model describing an experiment once it has finished running.
    """

    send_type: str


class FinalResult(MongoModel):
    """
    Data to push at the end of an experiment.
    """

    average_noise: float
    default_run: DefaultRun
    averaged_execution_time: List[float]
    min_execution_time: List[float]
    max_execution_time: List[float]
    std_execution_time: List[float]
    resampled_nbr: List[int]
    improvement_default: float
    elapsed_time: float
    explored_space: float


class DetailedExperiment(Experiment):
    """Detailed experiment model.
    """

    jobids: List[int] = None
    parameters: List[dict] = None
    execution_time: List[float] = None
    truncated: List[float] = None
    resampled: List[bool] = None
    initialization: List[bool] = None
    experiment_parameters: dict = None
    average_noise: float = None
    default_run: DefaultRun = None
    averaged_execution_time: List[float] = None
    min_execution_time: List[float] = None
    max_execution_time: List[float] = None
    std_execution_time: List[float] = None
    resampled_nbr: List[int] = None
    improvement_default: float = None
    accelerator: str = None
    elapsed_time: float = None
    experiment_name: str = None
    explored_space: float = None
    noise_reduction_strategy: dict = None
    pruning_strategy: dict = None
    status: str = None
    experiment_budget: int = None
    sbatch: str = None


class IntermediateResult(MongoModel):
    """
    A model describing an intermediate result of an experiment
    """

    jobids: int
    parameters: Dict
    execution_time: float
    truncated: bool
    resampled: bool
    initialization: bool
    improvement_default: float
    average_noise: float


class ExperimentForm(MongoModel):
    """A model describing the data received from the client to launch the experiment.
    """

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


class Message(MongoModel):
    detail: str
