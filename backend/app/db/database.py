import logging
from collections.abc import Generator
from functools import lru_cache

from sqlalchemy import Engine, create_engine, inspect
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings
from app.db.base import Base

logger = logging.getLogger(__name__)

DOCTORS_REQUIRED_COLUMNS = {
    "id",
    "name",
    "specialty",
    "rating",
    "review_count",
    "clinic_name",
    "location",
    "consultation_fee_min",
    "consultation_fee_max",
    "next_available_slot",
    "appointment_types",
    "languages",
    "description",
    "image_url",
    "is_active",
}


@lru_cache(maxsize=1)
def get_engine() -> Engine:
    settings = get_settings()
    connect_args = {}
    if settings.database_url.startswith("sqlite"):
        connect_args = {"check_same_thread": False}
    return create_engine(settings.database_url, connect_args=connect_args)


@lru_cache(maxsize=1)
def get_session_factory() -> sessionmaker[Session]:
    return sessionmaker(autocommit=False, autoflush=False, bind=get_engine())


def get_db() -> Generator[Session, None, None]:
    session = get_session_factory()()
    try:
        yield session
    finally:
        session.close()


def _reset_seeded_tables_if_schema_mismatch(engine: Engine) -> None:
    inspector = inspect(engine)

    if "doctors" not in inspector.get_table_names():
        return

    existing_columns = {column["name"] for column in inspector.get_columns("doctors")}
    missing_columns = DOCTORS_REQUIRED_COLUMNS - existing_columns

    if not missing_columns:
        return

    logger.warning(
        "Rebuilding doctors table due to schema mismatch. Missing columns: %s",
        ", ".join(sorted(missing_columns)),
    )
    Base.metadata.drop_all(bind=engine, tables=[Base.metadata.tables["doctors"]])


def init_db() -> None:
    from app import models  # noqa: F401
    from app.db.seed import seed_availability, seed_doctors

    engine = get_engine()
    _reset_seeded_tables_if_schema_mismatch(engine)
    Base.metadata.create_all(bind=engine)

    session = get_session_factory()()
    try:
        seed_doctors(session)
        seed_availability(session)
    finally:
        session.close()
