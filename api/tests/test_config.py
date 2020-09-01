"""
Test the config module of shaman_api package
"""
import pytest
from shaman_api.config import AppConfig


@pytest.fixture
def config_env(monkeypatch):
    # IOI Config
    monkeypatch.setenv("IOI_MONGODB_HOST", "example.com")
    monkeypatch.setenv("IOI_MONGODB_PORT", "1234")
    monkeypatch.setenv("IOI_MONGODB_DATABASE", "test_db")
    # Shaman Config
    monkeypatch.setenv("SHAMAN_MONGODB_HOST", "localhost")
    monkeypatch.setenv("SHAMAN_MONGODB_PORT", "12345")
    monkeypatch.setenv("SHAMAN_MONGODB_DATABASE", "exp_db")
    # Log
    monkeypatch.setenv("LOG_LEVEL", "INFO")


def test_config_from_env(config_env):

    config = AppConfig()

    assert config.ioi_mongodb_database == "test_db"
    assert config.ioi_mongodb_host == "example.com"
    assert config.ioi_mongodb_port == 1234

    assert config.shaman_mongodb_database == "exp_db"
    assert config.shaman_mongodb_host == "localhost"
    assert config.shaman_mongodb_port == 12345

    assert config.log_level == "INFO"
