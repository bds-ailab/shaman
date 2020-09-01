"""
Rest API endpoints related to IOI are defined in this module
"""
from typing import List, Optional
from starlette.responses import Response
from fastapi import APIRouter, HTTPException
from ..databases import connect_ioi_db, close_ioi_db, get_io_durations
from ..models import IODurations, Message
from ..logger import get_logger


logger = get_logger(__name__)


router = APIRouter(on_startup=[connect_ioi_db], on_shutdown=[close_ioi_db])


@router.get(
    "/",
    status_code=200,
    response_description="Successfully read I/O durations",
    response_model=IODurations,
    responses={404: {"model": Message}},
    summary="Get I/O durations by ID",
    description="Get an empty value for the general endpoint")
def get_duration():
    return None


@router.get(
    "/{experiment_id}",
    status_code=200,
    response_description="Successfully read I/O durations",
    response_model=IODurations,
    responses={404: {"model": Message}},
    summary="Get I/O durations by ID",
    description="Get a single experiment by ID",
)
def get_durations(experiment_id: str):
    """
    Receive experiment data inside POST request and store experiment inside SHAMAN MongoDB database
    """
    io_durations = get_io_durations(experiment_id)
    if io_durations is None:
        raise HTTPException(
            status_code=404, detail=f"Experiment {experiment_id} not found"
        )
    return io_durations
