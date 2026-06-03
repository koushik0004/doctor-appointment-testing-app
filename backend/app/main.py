from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.router import api_router
from app.db.database import init_db


def create_app() -> FastAPI:
    @asynccontextmanager
    async def lifespan(_: FastAPI):
        init_db()
        yield

    app = FastAPI(title="Doctor Appointment Testing App", lifespan=lifespan)

    app.include_router(api_router)
    return app


app = create_app()
