import os
import sys
from pathlib import Path

import importlib
from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine, inspect, text


TEST_DB = Path(__file__).resolve().parent / "test_doctors.sqlite3"
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB}"
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.config import get_settings  # noqa: E402
from app.db import database as database_module  # noqa: E402

get_settings.cache_clear()
database_module.get_engine.cache_clear()
database_module.get_session_factory.cache_clear()


@pytest.fixture()
def client():
    app_main_module = importlib.reload(importlib.import_module("app.main"))

    with TestClient(app_main_module.app) as test_client:
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


def test_init_db_rebuilds_stale_doctors_schema(tmp_path, monkeypatch):
    stale_db = tmp_path / "stale_doctors.sqlite3"
    stale_engine = create_engine(f"sqlite:///{stale_db}")

    with stale_engine.begin() as connection:
        connection.execute(
            text(
                """
                CREATE TABLE doctors (
                    id INTEGER NOT NULL PRIMARY KEY,
                    name VARCHAR NOT NULL,
                    slug VARCHAR NOT NULL,
                    specialty VARCHAR NOT NULL,
                    title VARCHAR,
                    rating FLOAT NOT NULL,
                    review_count INTEGER NOT NULL,
                    clinic_name VARCHAR NOT NULL,
                    location VARCHAR NOT NULL,
                    address VARCHAR,
                    fee_min INTEGER,
                    fee_max INTEGER,
                    languages VARCHAR,
                    image_url VARCHAR,
                    is_active BOOLEAN NOT NULL
                )
                """
            )
        )

    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{stale_db}")
    get_settings.cache_clear()
    database_module.get_engine.cache_clear()
    database_module.get_session_factory.cache_clear()

    database_module.init_db()

    repaired_columns = {
        column["name"]
        for column in inspect(database_module.get_engine()).get_columns("doctors")
    }

    assert "consultation_fee_min" in repaired_columns
    assert "consultation_fee_max" in repaired_columns
    assert "next_available_slot" in repaired_columns

    with database_module.get_session_factory()() as session:
        doctor_count = session.execute(text("SELECT COUNT(*) FROM doctors")).scalar_one()

    assert doctor_count == 10
