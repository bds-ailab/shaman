"""
Test databases related functions
"""
import pytest
import mongomock

from shaman_api.databases import (
    connect_ioi_db,
    connect_shaman_db,
    close_ioi_db,
    close_shaman_db,
    get_experiments,
    get_experiment,
    create_experiment,
)
from shaman_api.databases import ioi
from shaman_api.databases import shaman


def test_connect_and_close_ioi_db():
    # Ensure ioi_db is None
    assert ioi.ioi_db is None
    # Connect ioi_db
    connect_ioi_db()
    # Close ioi_db. By doing so we ensute that ioi_db is no longer None
    close_ioi_db()


def test_connect_and_close_shaman_db():
    # Ensure shaman_db is None
    assert shaman.shaman_db is None
    # Connect to Mongo
    connect_shaman_db()
    # Close connection. By doing so we ensure that shaman_db is no longer None
    close_shaman_db()


@pytest.fixture
def fake_experiments():
    return [
        {"experiment_id": "a", "jobids": [], "experiment_name": "test1"},
        {"experiment_id": "b", "jobids": [], "experiment_name": "test2"},
    ]


def test_get_experiments(monkeypatch, fake_experiments):
    """
    Test function to retrieve experiments.
    In order to test retrieval of experiments, we need to create experiments before.
    """
    # Mock mongodb connection
    monkeypatch.setattr(shaman, "shaman_db", mongomock.MongoClient()["test"])

    # Create some experiments
    for experiment in fake_experiments:
        create_experiment(experiment)

    # Get the experiments
    all_experiments = list(get_experiments())
    assert len(all_experiments) == 2

    # Get the experiments with limit
    all_experiments = list(get_experiments(limit=1))
    assert len(all_experiments) == 1


def test_get_experiment(monkeypatch, fake_experiments):
    # Mock mongodb connection
    monkeypatch.setattr(shaman, "shaman_db", mongomock.MongoClient()["test"])

    # Create some experiments
    for experiment in fake_experiments:
        create_experiment(experiment)

    exp_a = get_experiment("a")
    exp_b = get_experiment("b")
    assert exp_a["experiment_id"] == "a"
    assert exp_b["experiment_id"] == "b"

    exp_null = get_experiment("donotexists")
    assert exp_null is None
