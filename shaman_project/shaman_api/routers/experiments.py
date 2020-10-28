"""Rest API endpoints related to SHAman are defined in this module."""
from typing import List, Optional
from starlette.responses import Response
from fastapi import HTTPException, WebSocket, WebSocketDisconnect
from shaman_core.models.experiment_models import (
    Experiment,
    DetailedExperiment,
    IntermediateResult,
    FinalResult,
    Message,
    InitExperiment,
    ExperimentForm,
)
from .experiment_router import ExperimentRouter


router = ExperimentRouter()


# TODO: Add response type hint (and create associated pydantic model)
@router.post(
    "/",
    summary="Create a new experiment",
    description="Create a new experiment and store experiment"
    "data inside SHAMAN MongoDB database",
    response_description="Successfully created experiment",
    status_code=202,
)
async def create_shaman_experiment(experiment: InitExperiment):
    """Receive experiment data inside POST request and store experiment inside
    SHAMAN MongoDB database."""
    result = await router.db.create_experiment(experiment.dict())
    return {"id": str(result.inserted_id)}


@router.get(
    "/",
    summary="Get experiments",
    description="Get all or a limited number of experiments",
    response_description="Successfully read experiments",
    status_code=200,
)
async def get_shaman_experiments(
    limit: int = 1000, offset: Optional[int] = None
) -> List[Experiment]:
    """Receive experiment data inside POST request and store experiment inside
    SHAMAN MongoDB database."""
    return await router.db.get_experiments(limit=limit, offset=offset)


@router.post(
    "/launch",
    summary="Launch an experiment",
    description="Launch an experiment through the user interface",
    response_description="Successfully launched experiment",
    response_class=Response,
    status_code=202,
)
async def launch_shaman_experiment(experiment_form: ExperimentForm):
    """Given the data from the user, launch a SHAMan experiment.

    Args:
        experiment_form (ExperimentForm): the data sent from
            the UI to describe an experiment.
    """
    await router.redis.enqueue_job("launch_experiment", experiment_form.dict())
    return Response(content=None, status_code=202)


@router.get(
    "/{experiment_id}",
    summary="Get experiment by ID",
    description="Get a single experiment by ID",
    response_description="Successfully read experiment",
    responses={404: {"model": Message}},
    status_code=200,
)
async def get_shaman_experiment(experiment_id: str) -> DetailedExperiment:
    """Receive experiment data inside POST request and store experiment inside
    SHAMAN MongoDB database."""
    experiment = await router.db.get_experiment(experiment_id)
    if experiment is None:
        raise HTTPException(
            status_code=404, detail=f"Experiment {experiment_id} not found"
        )
    return experiment


@router.put(
    "/{experiment_id}/update",
    summary="Update experiment with intermediate result",
    description="Update experiment and store intermediate result"
    "inside SHAMAN MongoDB database",
    response_description="Successfully stored intermediate result",
    response_class=Response,
    status_code=202,
)
async def update_shaman_experiment(experiment_id: str,
                                   result: IntermediateResult):
    await router.db.update_experiment(experiment_id, result.dict())
    return Response(content=None, status_code=202)


@router.websocket("/stream")
async def websocket_endpoint(websocket: WebSocket):
    # Get experiment status
    await websocket.accept()
    try:
        async for insert in router.db.watch_experiments():
            experiment = Experiment(**insert)
            await websocket.send_text(experiment.json())
    except WebSocketDisconnect:
        print("Disconnected websocket.")


@router.websocket("/{experiment_id}/stream")
async def websocket_endpoint_experiment(experiment_id: str,
                                        websocket: WebSocket):
    # Get experiment status
    status = await router.db.get_experiment_status(experiment_id)
    if not status == "finished":
        try:
            await websocket.accept()
            print("Accepted connection to websocket")
            async for update in router.db.watch_experiment(experiment_id):
                experiment = DetailedExperiment(**update)
                await websocket.send_text(experiment.json())
        except WebSocketDisconnect:
            print(f"Disconnected websocket to experiment {experiment_id}.")


@router.put(
    "/{experiment_id}/finish",
    summary="Store final experiment data and close experiment",
    description=(
        "Update experiment with final data inside SHAMAN MongoDB database"
        "and consider experiment as finished"
    ),
    response_description="Successfully closed experiment",
    response_class=Response,
    status_code=202,
)
async def close_shaman_experiment(experiment_id: str, result: FinalResult):
    await router.db.close_experiment(experiment_id, result.dict())
    return Response(content=None, status_code=202)


@router.put(
    "/{experiment_id}/fail",
    summary="Store final experiment data and close experiment",
    description=(
        "Update experiment with final data inside SHAMAN MongoDB database"
        "and consider experiment as finished"
    ),
    response_description="Successfully closed experiment",
    response_class=Response,
    status_code=202,
)
async def fail_shaman_experiment(experiment_id: str):
    await router.db.fail_experiment(experiment_id)
    return Response(content=None, status_code=202)


@router.put(
    "/{experiment_id}/stop",
    summary="Store final experiment data and close experiment",
    description=(
        "Update experiment with final data inside SHAMAN MongoDB database"
        "and consider experiment as finished"
    ),
    response_description="Successfully closed experiment",
    response_class=Response,
    status_code=202,
)
async def stop_shaman_experiment(experiment_id: str):
    await router.db.stop_experiment(experiment_id)
    return Response(content=None, status_code=202)
