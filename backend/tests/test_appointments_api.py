import importlib
import os
import sys
from datetime import date, timedelta
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


TEST_DB = Path(__file__).resolve().parent / "test_appointments_api.sqlite3"
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB}"
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pydantic import ValidationError

from app.core.config import get_settings  # noqa: E402
from app.db import database as database_module  # noqa: E402
from app.schemas.appointment import AppointmentCreateRequest  # noqa: E402

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


def _get_doctor_id(client: TestClient, name: str) -> int:
    response = client.get("/api/doctors")
    assert response.status_code == 200
    for item in response.json()["items"]:
        if item["name"] == name:
            return item["id"]
    raise AssertionError(f"Doctor {name} not found")


def test_booking_flow_and_confirmation_endpoint(client):
    doctor_id = _get_doctor_id(client, "Dr. Sarah Jenkins")
    booking_date = date.today() + timedelta(days=1)
    booking_payload = {
        "doctor_id": doctor_id,
        "appointment_date": booking_date.isoformat(),
        "start_time": "10:00",
        "appointment_type": "IN_PERSON",
        "patient": {
            "full_name": "John Doe",
            "email": "john.doe@example.com",
            "phone": "9999999999",
        },
        "health_description": "Regular follow-up for high blood pressure.",
    }

    booking_response = client.post("/api/appointments", json=booking_payload)
    assert booking_response.status_code == 201
    created = booking_response.json()
    assert created["status"] == "CONFIRMED"
    assert created["doctor_id"] == doctor_id
    assert created["appointment_date"] == booking_date.isoformat()
    assert created["start_time"] == "10:00"
    assert created["end_time"] == "10:30"
    assert created["confirmation_code"].startswith("CN-")

    confirmation_response = client.get(f"/api/appointments/{created['id']}")
    assert confirmation_response.status_code == 200
    confirmation = confirmation_response.json()
    assert confirmation["confirmation_code"] == created["confirmation_code"]
    assert confirmation["doctor"]["name"] == "Dr. Sarah Jenkins"
    assert confirmation["patient"]["full_name"] == "John Doe"
    assert confirmation["status"] == "CONFIRMED"
    assert confirmation["appointment_date"] == booking_date.isoformat()
    assert confirmation["start_time"] == "10:00"
    assert confirmation["end_time"] == "10:30"

    availability_response = client.get(
        f"/api/doctors/{doctor_id}/availability",
        params={"date": booking_date.isoformat()},
    )
    assert availability_response.status_code == 200
    availability = availability_response.json()
    assert availability["date"] == booking_date.isoformat()
    assert availability["doctor_id"] == doctor_id
    assert len(availability["available_slots"]) == 5
    assert "10:00" not in {slot["start_time"] for slot in availability["available_slots"]}

    conflict_response = client.post("/api/appointments", json=booking_payload)
    assert conflict_response.status_code == 409
    assert "already booked" in conflict_response.json()["detail"]


def test_booking_payload_validation():
    with pytest.raises(ValidationError) as exc_info:
        AppointmentCreateRequest.model_validate(
            {
                "doctor_id": 1,
                "appointment_date": "2026-06-09",
                "start_time": "bad-time",
                "appointment_type": "IN_PERSON",
                "patient": {
                    "full_name": "J",
                    "email": "not-an-email",
                    "phone": "9999999999",
                },
                "health_description": "x" * 501,
            }
        )

    error_locations = {tuple(error["loc"]) for error in exc_info.value.errors()}
    assert ("start_time",) in error_locations
    assert ("patient", "full_name") in error_locations
    assert ("patient", "email") in error_locations
    assert ("health_description",) in error_locations


def test_booking_rejects_elapsed_slots(client):
    doctor_id = _get_doctor_id(client, "Dr. Sarah Jenkins")
    booking_response = client.post(
        "/api/appointments",
        json={
            "doctor_id": doctor_id,
            "appointment_date": (date.today() - timedelta(days=1)).isoformat(),
            "start_time": "10:00",
            "appointment_type": "IN_PERSON",
            "patient": {
                "full_name": "John Doe",
                "email": "john.doe@example.com",
                "phone": "9999999999",
            },
            "health_description": "Past slot booking attempt.",
        },
    )

    assert booking_response.status_code == 400
    assert "already passed" in booking_response.json()["detail"]
