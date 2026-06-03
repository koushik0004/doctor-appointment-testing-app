import os
import sys
from pathlib import Path

from fastapi.testclient import TestClient
import pytest


TEST_DB = Path(__file__).resolve().parent / "test_doctors.sqlite3"
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB}"
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.db import database as database_module  # noqa: E402

database_module.get_engine.cache_clear()
database_module.get_session_factory.cache_clear()

from app.main import app  # noqa: E402


@pytest.fixture()
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_health_endpoint(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_list_doctors_returns_seeded_doctors(client):
    response = client.get("/api/doctors")
    payload = response.json()

    assert response.status_code == 200
    assert payload["total"] == len(payload["items"])
    assert payload["total"] == 10
    assert payload["items"][0]["name"] == "Dr. Elena Rodriguez"


def test_specialty_filtering(client):
    response = client.get("/api/doctors", params={"specialty": "Cardiology"})
    payload = response.json()

    assert response.status_code == 200
    assert payload["total"] == 2
    assert all(doctor["specialty"] == "Cardiology" for doctor in payload["items"])


def test_appointment_type_filtering(client):
    response = client.get(
        "/api/doctors",
        params={"appointment_type": "TELEMEDICINE"},
    )
    payload = response.json()

    assert response.status_code == 200
    assert payload["total"] == 7
    assert all("TELEMEDICINE" in doctor["appointment_types"] for doctor in payload["items"])


def test_combined_filtering(client):
    response = client.get(
        "/api/doctors",
        params={"specialty": "Cardiology", "appointment_type": "TELEMEDICINE"},
    )
    payload = response.json()

    assert response.status_code == 200
    assert payload["total"] == 1
    assert payload["items"][0]["name"] == "Dr. Daniel Park"


def test_invalid_doctor_id_returns_404(client):
    response = client.get("/api/doctors/9999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Doctor 9999 not found"


def test_empty_results(client):
    response = client.get(
        "/api/doctors",
        params={"specialty": "Pediatrics", "appointment_type": "TELEMEDICINE"},
    )
    payload = response.json()

    assert response.status_code == 200
    assert payload == {"items": [], "total": 0}
