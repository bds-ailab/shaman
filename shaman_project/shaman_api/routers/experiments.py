"""
Rest API endpoints related to SHAman are defined in this module
"""
from typing import List, Optional
from starlette.responses import Response
from fastapi import APIRouter, HTTPException, WebSocket
from ..models import (
    Experiment,
    WebSocketExperiment,
    DetailedExperiment,
    IntermediateResult,
    FinalResult,
    Message,
    InitExperiment,
    ExperimentForm,
)
from ..databases import (
    create_experiment,
    get_experiments,
    get_experiment,
    update_experiment,
    close_experiment,
    connect_shaman_db,
    close_shaman_db,
    watch_experiments,
    watch_experiment,
    get_experiment_status,
    fail_experiment,
    stop_experiment,
    launch_experiment,
)
from ..logger import get_logger


logger = get_logger(__name__)


router = APIRouter(on_startup=[connect_shaman_db], on_shutdown=[close_shaman_db])


@router.post(
    "/",
    status_code=202,
    response_description="Successfully created experiment",
    summary="Create a new experiment",
    description="Create a new experiment and store experiment data inside SHAMAN MongoDB database",
)
def create_shaman_experiment(experiment: InitExperiment):
    """
    Receive experiment data inside POST request and store experiment inside SHAMAN MongoDB database
    """
    result = create_experiment(experiment.dict())
    print(result)
    return {"id": str(result.inserted_id)}


@router.get(
    "/",
    status_code=200,
    response_description="Successfully read experiments",
    response_model=List[Experiment],
    summary="Get experiments",
    description="Get all or a limited number of experiments",
)
def get_shaman_experiments(limit: Optional[int] = None, offset: Optional[int] = None):
    """
    Receive experiment data inside POST request and store experiment inside SHAMAN MongoDB database
    """
    experiments = get_experiments(limit=limit, offset=offset)
    return list(experiments)


@router.post(
    "/launch",
    status_code=200,
    response_description="Successfully launched experiment",
    response_model=ExperimentForm,
    summary="Launch an experiment",
    description="Launch an experiment through the user interface",
)
def launch_shaman_experiment(experiment_form: ExperimentForm):
    """Given the data from the user, launch a SHAMan experiment.

    Args:
        experiment_form (ExperimentForm): the data sent from the UI to describe an experiment.
    """
    launch_experiment(experiment_form)


@router.get(
    "/{experiment_id}",
    status_code=200,
    response_description="Successfully read experiment",
    response_model=DetailedExperiment,
    responses={404: {"model": Message}},
    summary="Get experiment by ID",
    description="Get a single experiment by ID",
)
def get_shaman_experiments(experiment_id: str):
    """
    Receive experiment data inside POST request and store experiment inside SHAMAN MongoDB database
    """
    experiment = get_experiment(experiment_id)
    if experiment is None:
        raise HTTPException(
            status_code=404, detail=f"Experiment {experiment_id} not found"
        )
    return experiment


@router.put(
    "/{experiment_id}/update",
    status_code=202,
    response_class=Response,
    response_description="Successfully stored intermediate result",
    summary="Update experiment with intermediate result",
    description="Update experiment and store intermediate resul inside SHAMAN MongoDB database",
)
def update_shaman_experiment(experiment_id: str, result: IntermediateResult):
    update_experiment(experiment_id, result.dict())
    return Response(content=None, status_code=202)


@router.websocket("/stream")
async def websocket_endpoint(websocket: WebSocket):
    # Get experiment status
    await websocket.accept()
    async for insert in watch_experiments():
        experiment = Experiment(**insert)
        await websocket.send_text(experiment.json())


@router.websocket("/{experiment_id}/stream")
async def websocket_endpoint(experiment_id: str, websocket: WebSocket):
    # Get experiment status
    status = get_experiment_status(experiment_id)
    if not status == "finished":
        await websocket.accept()
        print("Accepted connection to websocket")
        async for update in watch_experiment(experiment_id):
            experiment = DetailedExperiment(**update)
            await websocket.send_text(experiment.json())


@router.put(
    "/{experiment_id}/finish",
    status_code=202,
    response_class=Response,
    response_description="Successfully closed experiment",
    summary="Store final experiment data and close experiment",
    description=(
        "Update experiment with final data inside SHAMAN MongoDB database"
        "and consider experiment as finished"
    ),
)
def close_shaman_experiment(experiment_id: str, result: FinalResult):
    close_experiment(experiment_id, result.dict())
    return Response(content=None, status_code=202)


@router.put(
    "/{experiment_id}/fail",
    status_code=202,
    response_class=Response,
    response_description="Successfully closed experiment",
    summary="Store final experiment data and close experiment",
    description=(
        "Update experiment with final data inside SHAMAN MongoDB database"
        "and consider experiment as finished"
    ),
)
def fail_shaman_experiment(experiment_id: str):
    fail_experiment(experiment_id)
    return Response(content=None, status_code=202)


@router.put(
    "/{experiment_id}/stop",
    status_code=202,
    response_class=Response,
    response_description="Successfully closed experiment",
    summary="Store final experiment data and close experiment",
    description=(
        "Update experiment with final data inside SHAMAN MongoDB database"
        "and consider experiment as finished"
    ),
)
def stop_shaman_experiment(experiment_id: str):
    stop_experiment(experiment_id)
    return Response(content=None, status_code=202)
