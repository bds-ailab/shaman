import os
from typing import Optional, List, Dict

from bson.objectid import ObjectId
from motor.motor_asyncio import (
    AsyncIOMotorClient,
    AsyncIOMotorDatabase,
    AsyncIOMotorCollection,
)
from pymongo.results import UpdateResult

from ..models import Experiment, IntermediateResult, FinalResult, InitExperiment
from ..config import AppConfig
from ..logger import get_logger


logger = get_logger("experiments_database")


class ExperimentDatabase:
    def __init__(self):
        self.async_client: Optional[AsyncIOMotorClient] = None
        self.async_db: Optional[AsyncIOMotorDatabase] = None
        self.experiments_collection: Optional[AsyncIOMotorCollection] = None
        self.components_collection: Optional[AsyncIOMotorCollection] = None
        self.server_info: Optional[dict] = None

    async def connect(self, config: AppConfig = None):
        # Parse config from environment if not provided
        if config is None:
            config = AppConfig()
        # Create asynchronous Mongo client
        self.async_client = AsyncIOMotorClient(
            host=config.shaman_mongodb_host, port=config.shaman_mongodb_port
        )
        self.async_db = self.async_client[config.shaman_mongodb_database]
        self.experiments_collection = self.async_db["experiments"]
        self.components_collection = self.async_db["components"]
        self.server_info = await self.async_client.server_info()
        logger.info(
            "Connected to mongodb server version {0} on host 'mongodb://{1}:{2}'.".format(
                self.server_info["version"], *self.async_client.address
            )
        )
        return self

    async def close(self):
        self.async_client.close()
        logger.info("Closed connection to mongodb server.")

    async def create_experiment(self, experiment: InitExperiment):
        """
        Experiments are created inside shaman mongodb database
        """
        experiment.update({"status": "created"})
        return await self.experiments_collection.insert_one(experiment)

    async def get_experiments(self, limit: int, offset: Optional[int] = None) -> List:
        """
        Return a cursor of all experiments.
        Optionaly you can give a limit argument to return a limited number of experiments
        """
        all_experiments = self.experiments_collection.find(
            projection=Experiment._project()
        )
        if offset:
            all_experiments = all_experiments.skip(offset)
        return await all_experiments.to_list(length=limit)

    async def get_experiment(self, experiment_id: str) -> Experiment:
        """
        Return a single experiment based on given experiment ID
        Return None if the experiment do not exist.
        """
        experiment = await self.experiments_collection.find_one(
            {"_id": ObjectId(experiment_id)}
        )
        return experiment

    async def update_experiment(self, experiment_id: str, result: IntermediateResult):
        """
        Experiments are updated inside shaman mongodb database
        """
        await self.experiments_collection.update_one(
            {"_id": ObjectId(experiment_id)},
            {
                "$set": {"status": "running"},
                "$push": {
                    "jobids": result["jobids"],
                    "execution_time": result["execution_time"],
                    "parameters": result["parameters"],
                    "truncated": result["truncated"],
                    "resampled": result["resampled"],
                    "initialization": result["initialization"],
                },
            },
            upsert=True,
        )

    async def close_experiment(self, experiment_id: str, final_result: FinalResult):
        """
        Experiments are terminated inside shaman mongodb database
        """
        final_result.update({"status": "finished"})
        await self.experiments_collection.update_one(
            {"_id": ObjectId(experiment_id)}, {"$set": final_result}
        )

    async def fail_experiment(self, experiment_id: str):
        """
        Experiments are terminated inside shaman mongodb database
        """
        await self.experiments_collection.update_one(
            {"_id": ObjectId(experiment_id)}, {"$set": {"status": "failed"}}
        )

    async def stop_experiment(self, experiment_id: str):
        """
        Experiments are terminated inside shaman mongodb database
        """
        await self.experiments_collection.update_one(
            {"_id": ObjectId(experiment_id)}, {"$set": {"status": "stopped"}}
        )

    async def watch_experiments(self):
        """Watch the changes on a collection for a given experiment_id using Mongo Stream"""
        # try:
        async with self.experiments_collection.watch(
            [
                {
                    "$match": {
                        "$or": [
                            {"operationType": "insert"},
                            {
                                "$and": [
                                    {
                                        "updateDescription.updatedFields.status": {
                                            "$exists": True
                                        },
                                        "operationType": "update",
                                    }
                                ]
                            },
                        ]
                    }
                }
            ],
            full_document="updateLookup",
        ) as stream:
            async for insert in stream:
                yield insert["fullDocument"]

    async def watch_experiment(self, experiment_id: str):
        """Watch the changes on a collection for a given experiment_id using Mongo Stream"""
        # try:
        async with self.experiments_collection.watch(
            [
                {
                    "$match": {
                        "$and": [
                            {
                                "fullDocument._id": ObjectId(experiment_id),
                                "operationType": "update",
                            }
                        ]
                    }
                }
            ],
            full_document="updateLookup",
        ) as stream:
            async for update in stream:
                yield update["fullDocument"]

    async def get_experiment_status(self, experiment_id: str):
        """Given an experiment_id, get the status of the experiment."""
        experiment = await self.experiments_collection.find_one(
            {"_id": ObjectId(experiment_id)}, projection={"status": 1}
        )
        return experiment["status"]

    # Components related functions
    async def get_components(self) -> List:
        """List all the available components."""
        all_components = self.components_collection.find({}, projection={"_id": 0})
        return await all_components.to_list(length=1)

    async def update_components(self, component) -> UpdateResult:
        """Update the component data: replace if already exists."""
        return await self.components_collection.replace_one({}, component, upsert=True)

    async def get_components_parameters(self) -> Dict:
        """Returns the list of available components and their
        """
        components = await self.components_collection.find(
            {}, projection={"_id": 0}
        ).to_list(length=1)
        return {
            component: parameters["parameters"]
            for component, parameters in components[0]["components"].items()
        }

