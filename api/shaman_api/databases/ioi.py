"""
This module defines the connection to IOI mongodb database as well as
all functions that interact with this database.

TODO: very inefficient in terms of requests, would benefit from being refactored into a class.
"""
import numpy as np
from pymongo import MongoClient
from .shaman import get_experiment
from ..config import CONFIG
from ..logger import get_logger


logger = get_logger(__name__)
ioi_db = None

# For each available time range located in the IOI database, the average of the bin, converted
# in seconds
TIME_PER_RANGE = {f"range{i}": (
    4**i + 4**(i - 1)) / (2 * 10 ** 6) for i in range(1, 16)}
TIME_PER_RANGE.update({"range0": .5 * 10 ** (-6)})


def connect_ioi_db(**kwargs):
    global ioi_db
    host = CONFIG.ioi_mongodb_host
    port = CONFIG.ioi_mongodb_port
    database = CONFIG.ioi_mongodb_database
    logger.debug(
        f"Connecting to ioi mongodb database with uri: mongodb://{host}:{port}/{database}"
    )
    ioi_client = MongoClient(host=host, port=port)
    ioi_db = ioi_client[CONFIG.ioi_mongodb_database]


def close_ioi_db():
    logger.debug("Closing connections to IOI mongodb database")
    ioi_db.client.close()


def get_time_spent_ios_jobid(jobid, type_):
    """
    Given a jobid, compute the time spent doing I/Os of type "type", type being either write or
    read, by summing over each timeframe the time spent in each category.
    """
    io_durations = ioi_db["IODurations"].find({"jobid": jobid})
    ios = [io_duration[type_] for io_duration in io_durations]
    # Compute time per range as the product of the count in each bin and the average in each bin.
    return sum([sum([TIME_PER_RANGE[range_] * count for range_, count in io.items()]) for io in ios])


def get_time_spent_ios(jobids, type_):
    """
    Given a list of jobid, compute the time spent doing I/Os of type type_.
    """
    return [get_time_spent_ios_jobid(jobid, type_) for jobid in jobids]


def _aggregate_consecutives(values, parameters, estimator):
    """Given an array containing values and an array containing parameters, computes the
    estimator to aggregate these values according to consecutive parameters.

    Args:
        values (list): The list of values to aggregate.
        parameters (list): The list of parameters to aggregate from.
        estimator (function): The function to use for aggregation.
    """
    values_array = np.array(values)
    parameters_array = np.array([list(parameter.values())
                                 for parameter in parameters])
    ix = 1
    consecutives = list()
    consecutive_per_parametrization = [values_array[ix - 1]]
    while ix < len(values_array):
        if np.all(parameters_array[ix - 1] == parameters_array[ix]):
            consecutive_per_parametrization.append(values_array[ix])
            ix += 1
            continue
        consecutives.append(consecutive_per_parametrization)
        consecutive_per_parametrization = [values_array[ix]]
        ix += 1
    consecutives.append(consecutive_per_parametrization)
    # Cast as float in order to get rid of the enforced numpy float np.
    return [float(estimator(consecutive)) for consecutive in consecutives]


def _get_time_spent_ios_parametrization(experiment, estimator, type_):
    """Given an experiment_id from the SHAMan DB, returns the times spent doing I/Os, as well as
    their parametrization, and computes an estimator computed on their consecutive parametrization.
    """
    # Try to get the jobids corresponding to the experiment id.
    try:
        jobids = experiment["jobids"]
    # If not possible, it means there is no record in the IOI and return None
    except KeyError:
        return None
    # Get the parametrization corresponding to the jobids
    parameters = experiment["parameters"]
    # Use the jobids to retrieve the time spent doing IOs
    time_spent_doing_io = get_time_spent_ios(jobids, type_)
    # Return the aggregation of time_spent_doing_io aggregated by parameters
    return _aggregate_consecutives(time_spent_doing_io, parameters, estimator)


def averaged_time_spent_ios(experiment, type_):
    """Given an experiment_id from the SHAMan DB, returns the averaged time spent doing I/Os.
    """
    # Aggregate the data according to the mean
    return _get_time_spent_ios_parametrization(experiment, np.mean, type_)


def min_time_spent_ios(experiment, type_):
    """Given an experiment_id from the SHAMan DB, returns the minimum time spent doing I/Os, averaged
    per consecutive parametrization.
    """
    return _get_time_spent_ios_parametrization(experiment, np.min, type_)


def max_time_spent_ios(experiment, type_):
    """Given an experiment_id from the SHAMan DB, returns the maximum time spent doing I/Os, averaged
    per consecutive parametrization.
    """
    return _get_time_spent_ios_parametrization(experiment, np.max, type_)


def get_io_durations(experiment_id):
    """Given an experiment id, returns the IO durations as a dictionary, for reads and writes,
    and returning:
        - The min
        - The max
        - The average

    Args:
        experiment_id (str): The ID of the experiment.
    """
    experiment = get_experiment(experiment_id)
    return {"experiment_id": experiment_id,
            "min_duration_read": min_time_spent_ios(experiment, "read"),
            "average_duration_read": averaged_time_spent_ios(experiment, "read"),
            "max_duration_read": max_time_spent_ios(experiment, "read"),
            "min_duration_write": min_time_spent_ios(experiment, "write"),
            "average_duration_write": averaged_time_spent_ios(experiment, "write"),
            "max_duration_write": max_time_spent_ios(experiment, "write")}
