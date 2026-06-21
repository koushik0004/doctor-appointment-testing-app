import importlib
import os
import sys
from pathlib import Path

from fastapi.testclient import TestClient
import pytest


TEST_DB = Path(__file__).resolve().parent / "test_chat_api.sqlite3"
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB}"
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.config import get_settings  # noqa: E402
from app.db import database as database_module  # noqa: E402
from app.schemas.chat import ChatRequest  # noqa: E402
from app.services.chat_service import create_chat_response  # noqa: E402

get_settings.cache_clear()
database_module.get_engine.cache_clear()
database_module.get_session_factory.cache_clear()


@pytest.fixture()
def client():
    if TEST_DB.exists():
        TEST_DB.unlink()
    database_module.get_engine.cache_clear()
    database_module.get_session_factory.cache_clear()

    app_main_module = importlib.reload(importlib.import_module("app.main"))

    with TestClient(app_main_module.app) as test_client:
        yield test_client

    database_module.get_engine.cache_clear()
    database_module.get_session_factory.cache_clear()
    if TEST_DB.exists():
        TEST_DB.unlink()


def test_chat_endpoint_returns_expected_response(client):
    response = client.post("/api/chat", json={"message": "Hello"})

    assert response.status_code == 200
    assert response.json() == {"response": "Hello, I am your AI Assistant."}


def test_chat_endpoint_supports_versioned_route(client):
    response = client.post("/api/v1/chat", json={"message": "Find cardiologist"})

    assert response.status_code == 200
    assert response.json() == {"response": "I can help you find a cardiologist."}


def test_chat_endpoint_rejects_blank_messages(client):
    response = client.post("/api/chat", json={"message": "   "})

    assert response.status_code == 422
    error = response.json()["detail"][0]
    assert error["loc"] == ["body", "message"]
    assert error["type"] == "string_too_short"


def test_chat_service_returns_default_fallback():
    result = create_chat_response(ChatRequest(message="Need some help"))

    assert result.response == "I can help with doctors, schedules, and booking questions."
