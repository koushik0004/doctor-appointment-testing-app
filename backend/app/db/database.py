from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings
from app.db.base import Base


@lru_cache(maxsize=1)
def get_engine():
    settings = get_settings()
    connect_args = {}
    if settings.database_url.startswith("sqlite"):
        connect_args = {"check_same_thread": False}
    return create_engine(settings.database_url, connect_args=connect_args)


@lru_cache(maxsize=1)
def get_session_factory() -> sessionmaker[Session]:
    return sessionmaker(autocommit=False, autoflush=False, bind=get_engine())


def get_db():
    session = get_session_factory()()
    try:
        yield session
    finally:
        session.close()


def init_db() -> None:
    from app import models  # noqa: F401
    from app.db.seed import seed_doctors

    engine = get_engine()
    Base.metadata.create_all(bind=engine)

    session = get_session_factory()()
    try:
        seed_doctors(session)
    finally:
        session.close()
