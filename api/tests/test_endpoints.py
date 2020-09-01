"""
Test the API endpoints
"""
import pytest
import mongomock
from fastapi.testclient import TestClient

from shaman_api import app
from shaman_api.databases import shaman, create_experiment
from .parametrize import (
    parametrize_create_experiment,
    parametrize_update_experiment,
    parametrize_close_experiment,
)


def test_read_main():
    """
    Root endpoint is not defined. It should return a 404 not found.
    """
    with TestClient(app) as client:
        response = client.get("/")

    assert response.status_code == 404


@pytest.mark.parametrize(*parametrize_create_experiment)
def test_create_shaman_experiment(monkeypatch, experiment, status_code, result):
    """
    Test call to /experiments/ endpoint using data defined in parametrize.py
    """

    with TestClient(app) as client:
        # Mock mongodb connection
        monkeypatch.setattr(shaman, "shaman_db", mongomock.MongoClient()["test"])
        response = client.post("/experiments/", json=experiment)

    assert response.status_code == status_code
    assert response.json() == result


def test_get_shaman_experiments(monkeypatch):
    """
    Test call to /experiments/ endpoint using data defined in parametrize.py
    """

    with TestClient(app) as client:
        # Mock mongodb connection
        monkeypatch.setattr(shaman, "shaman_db", mongomock.MongoClient()["test"])
        response = client.get("/experiments/")

    assert response.status_code == 200
    assert response.json() == []

    with TestClient(app) as client:
        # Mock mongodb connection
        monkeypatch.setattr(shaman, "shaman_db", mongomock.MongoClient()["test"])
        create_experiment(
            {"experiment_id": "a", "jobids": [], "experiment_name": "test"}
        )
        response = client.get("/experiments/")

    assert response.status_code == 200
    assert response.json() == [
        {"experiment_id": "a", "jobids": [], "experiment_name": "test"}
    ]


def test_get_shaman_experiment(monkeypatch):
    """
    Test call to /experiments/{experiment_id} endpoint
    """

    with TestClient(app) as client:
        # Mock mongodb connection
        monkeypatch.setattr(shaman, "shaman_db", mongomock.MongoClient()["test"])
        response = client.get("/experiments/donotexists")

    assert response.status_code == 404
    assert response.json() == {"detail": "Experiment donotexists not found"}

    with TestClient(app) as client:
        # Mock mongodb connection
        monkeypatch.setattr(shaman, "shaman_db", mongomock.MongoClient()["test"])
        create_experiment(
            {"experiment_id": "a", "jobids": [], "experiment_name": "test"}
        )
        response = client.get("/experiments/a")

    assert response.status_code == 200
    assert response.json() == {
        "experiment_id": "a",
        "jobids": [],
        "experiment_name": "test",
    }


def test_create_shaman_experiment_redirect():
    """
    Test call to /experiments (without trailing slash) endpoints using data defined in parametrize.py.
    It ensures that redirection to /experiments/ is performed and status code is 307 (temporary redirect)
    """
    with TestClient(app) as client:
        response = client.post(
            "/experiments", json=parametrize_create_experiment[1][0][0]
        )

    assert response.status_code == 307


@pytest.mark.parametrize(*parametrize_update_experiment)
def test_update_shaman_experiment(
    monkeypatch, experiment_id, intermediate_result, status_code
):
    """
    Test call to /experiments/{experiment_id}/update endpoints using data defined in parametrize.py
    """
    with TestClient(app) as client:
        # Mock mongodb connection
        monkeypatch.setattr(shaman, "shaman_db", mongomock.MongoClient()["test"])

        response = client.put(
            f"/experiments/{experiment_id}/update", json=intermediate_result
        )

    assert response.status_code == status_code


@mongomock.patch(servers=(("localhost", 27018),))
@pytest.mark.parametrize(*parametrize_close_experiment)
def test_close_shaman_experiment(monkeypatch, experiment_id, final_result, status_code):
    """
    Test call to /experiments/{experiment_id}/finish endpoints using data defined in parametrize.py
    """
    with TestClient(app) as client:
        #   Mock mongodb connection
        monkeypatch.setattr(shaman, "shaman_db", mongomock.MongoClient()["test"])

        response = client.put(f"/experiments/{experiment_id}/finish", json=final_result)

    assert response.text == ""
    assert response.status_code == status_code
