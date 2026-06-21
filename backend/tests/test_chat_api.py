import importlib
import os
import sys
from pathlib import Path

from fastapi.testclient import TestClient
import pytest
from sqlalchemy.orm import Session


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


def _session() -> Session:
    return database_module.get_session_factory()()


def test_chat_endpoint_returns_expected_response(client):
    response = client.post("/api/chat", json={"message": "Hello"})

    assert response.status_code == 200
    assert response.json() == {"response": "Hello, I am your AI Assistant."}


def test_chat_endpoint_lists_matching_specialists(client):
    response = client.post("/api/v1/chat", json={"message": "Show cardiologists"})

    assert response.status_code == 200
    payload = response.json()["response"]
    assert "Available Cardiology doctors:" in payload
    assert "Dr. Sarah Jenkins" in payload
    assert "Dr. Daniel Park" in payload


def test_chat_endpoint_returns_consultation_fee(client):
    response = client.post("/api/chat", json={"message": "What is Dr. Sarah Jenkins fee?"})

    assert response.status_code == 200
    assert response.json() == {
        "response": "Dr. Sarah Jenkins charges $120-$200 for a consultation."
    }


def test_chat_endpoint_returns_available_slots(client):
    response = client.post("/api/chat", json={"message": "What slots does Dr. Sarah Jenkins have?"})

    assert response.status_code == 200
    payload = response.json()["response"]
    assert "Available appointment slots for Dr. Sarah Jenkins on" in payload
    assert "08:00" in payload
    assert "10:00" in payload


def test_chat_endpoint_rejects_blank_messages(client):
    response = client.post("/api/chat", json={"message": "   "})

    assert response.status_code == 422
    error = response.json()["detail"][0]
    assert error["loc"] == ["body", "message"]
    assert error["type"] == "string_too_short"


def test_chat_service_returns_available_specialties(client):
    with _session() as session:
        result = create_chat_response(session, ChatRequest(message="What specializations are available?"))

    assert result.response == (
        "Available specializations: Cardiology, Dermatology, General Practice, "
        "Internal Medicine, Pediatrics."
    )


def test_chat_service_returns_default_fallback(client):
    with _session() as session:
        result = create_chat_response(session, ChatRequest(message="Need some help"))

    assert result.response == (
        "I can help with available doctors, specializations, consultation fees, "
        "and appointment slots."
    )
