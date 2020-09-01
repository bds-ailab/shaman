"""
This module defines the connection to IOI mongodb database as well as
all functions that interact with this database.
"""
import os
import configparser
from pathlib import Path

from typing import Optional
from pymongo import MongoClient
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import PyMongoError
from bson.objectid import ObjectId
from pymongo.cursor import Cursor
from ..models import Experiment, IntermediateResult, FinalResult, InitExperiment, ExperimentForm
from ..config import CONFIG
from ..logger import get_logger
from ..shaman_config import ShamanConfig, SHAMAN_CONFIG_TEMPLATE

# SHAMan dependency
from little_shaman.run_experiment import run


logger = get_logger(__name__)
shaman_db = None
async_shaman_db = None


def connect_shaman_db(**kwargs):
    global shaman_db
    global async_shaman_db
    host = CONFIG.shaman_mongodb_host
    port = CONFIG.shaman_mongodb_port
    database = CONFIG.shaman_mongodb_database
    logger.debug(
        f"Connecting to SHAMAN mongodb database with uri: mongodb://{host}:{port}/{database}"
    )
    shaman_client = MongoClient(host=host, port=port)
    shaman_db = shaman_client[CONFIG.shaman_mongodb_database]
    # hack: also perform asynchrone connection using motor, but will become the standard connection
    # method soon
    async_shaman_client = AsyncIOMotorClient(host=host, port=port)
    async_shaman_db = async_shaman_client[CONFIG.shaman_mongodb_database]


def close_shaman_db():
    logger.debug("Closing connections to SHAMAN mongodb database")
    shaman_db.client.close()
    async_shaman_db.client.close()


def create_experiment(experiment: InitExperiment):
    """
    Experiments are created inside shaman mongodb database
    """
    experiment.update({"status": "created"})
    return shaman_db["experiments"].insert_one(experiment)


def write_sbatch(sbatch_content, output_file):
    """Write the sbatch given the sbatch content sent by the application.

    Args:
        sbatch_content (str): The content to be written.
        output_file(str): The folder where the sbatch must be stored.
    """
    with open(output_file, "w+") as f:
        f.write(sbatch_content)
        f.close()


def launch_experiment(experiment_form: ExperimentForm):
    """Launches a SHAMan experiment.

    TODO: Do this through an external worker, so that there is no dependency between
    the API and little-shaman. This is only a POC and not a clean way to proceed.
    """
    # Create SHAMan configuration object
    # Take the default configuration from the shaman_config module
    # Output it in the running directory
    config_file = str((CONFIG.running_directory
                       / "config_shaman.cfg").absolute())
    shaman_config = ShamanConfig(SHAMAN_CONFIG_TEMPLATE, config_file)
    # Build the configuration file
    configuration_file = shaman_config.build_configuration(
        experiment_form.dict())
    # Write the sbatch from the request data
    sbatch_file = str((CONFIG.running_directory
                       / "ui_sbatch.sbatch").absolute())
    write_sbatch(sbatch_content=experiment_form.sbatch, output_file=sbatch_file)
    # Go to the running directory
    os.chdir(CONFIG.running_directory)
    # Launch the experiment
    run(accelerator_name=experiment_form.accelerator_name,
        nbr_iteration=experiment_form.nbr_iteration,
        sbatch_file=sbatch_file,
        experiment_name=experiment_form.experiment_name,
        configuration_file=config_file)


def get_experiments(limit: Optional[int] = None, offset: Optional[int] = None) -> Cursor:
    """
    Return a cursor of all experiments.
    Optionaly you can give a limit argument to return a limited number of experiments
    """
    all_experiments = shaman_db["experiments"].find(
        projection=Experiment._project())
    if offset:
        all_experiments = all_experiments.skip(offset)
    if limit:
        all_experiments = all_experiments.limit(limit)
    return all_experiments


def get_experiment(experiment_id: str) -> Experiment:
    """
    Return a single experiment based on given experiment ID
    Return None if the experiment do not exist.
    """
    experiment = shaman_db["experiments"].find_one(
        {"_id": ObjectId(experiment_id)})
    return experiment


def update_experiment(experiment_id: str, result: IntermediateResult):
    """
    Experiments are updated inside shaman mongodb database
    """
    shaman_db["experiments"].update_one({"_id": ObjectId(experiment_id)}, {"$set": {"status": "running"}, "$push": {"jobids": result["jobids"],
                                                                                                                    "execution_time": result["execution_time"],
                                                                                                                    "parameters": result["parameters"],
                                                                                                                    "truncated": result["truncated"],
                                                                                                                    "resampled": result["resampled"],
                                                                                                                    "initialization": result["initialization"]}}, upsert=True)


def close_experiment(experiment_id: str, final_result: FinalResult):
    """
    Experiments are terminated inside shaman mongodb database
    """
    final_result.update({"status": "finished"})
    shaman_db["experiments"].update_one(
        {"_id": ObjectId(experiment_id)}, {"$set": final_result})


def fail_experiment(experiment_id: str):
    """
    Experiments are terminated inside shaman mongodb database
    """
    shaman_db["experiments"].update_one(
        {"_id": ObjectId(experiment_id)}, {"$set": {"status": "failed"}})


def stop_experiment(experiment_id: str):
    """
    Experiments are terminated inside shaman mongodb database
    """
    shaman_db["experiments"].update_one(
        {"_id": ObjectId(experiment_id)}, {"$set": {"status": "stopped"}})


async def watch_experiments():
    """Watch the changes on a collection for a given experiment_id using Mongo Stream
    """
    # try:
    async with async_shaman_db["experiments"].watch(
            [{'$match':
              {"$or": [
                  {'operationType': 'insert'},
                  {'$and': [
                      {"updateDescription.updatedFields.status": {"$exists": True},
                       'operationType': 'update'}]}]}}], full_document="updateLookup") as stream:
        async for insert in stream:
            yield insert["fullDocument"]
    # except PyMongoError:
        # print("Error when watching change.")


async def watch_experiment(experiment_id: str):
    """Watch the changes on a collection for a given experiment_id using Mongo Stream
    """
    # try:
    async with async_shaman_db["experiments"].watch(
            [{'$match':
                {"$and": [{"fullDocument._id": ObjectId(experiment_id),
                           'operationType': 'update'}]}}
             ],
            full_document="updateLookup") as stream:
        async for update in stream:
            yield update["fullDocument"]
    # except PyMongoError:
        # print("Error when watching change.")


def get_experiment_status(experiment_id: str):
    """Given an experiment_id, get the status of the experiment.
    """
    experiment = shaman_db["experiments"].find_one(
        {"_id": ObjectId(experiment_id)}, projection={"status": 1})
    return experiment["status"]
