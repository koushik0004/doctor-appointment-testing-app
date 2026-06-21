from fastapi import APIRouter

from app.api.appointments import router as appointments_router
from app.api.availability import router as availability_router
from app.api.chat import router as chat_router
from app.api.chat import versioned_router as versioned_chat_router
from app.api.doctors import router as doctors_router
from app.api.health import router as health_router


api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(chat_router)
api_router.include_router(versioned_chat_router)
api_router.include_router(doctors_router)
api_router.include_router(availability_router)
api_router.include_router(appointments_router)
