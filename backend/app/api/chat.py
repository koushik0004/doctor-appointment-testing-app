from fastapi import APIRouter

from app.core.errors import chat_service_error
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import create_chat_response

router = APIRouter(prefix="/chat", tags=["chat"])
versioned_router = APIRouter(prefix="/v1/chat", tags=["chat"])


def _handle_chat(request: ChatRequest) -> ChatResponse:
    try:
        return create_chat_response(request)
    except Exception as exc:  # pragma: no cover
        raise chat_service_error() from exc


@router.post("", response_model=ChatResponse)
def create_chat_reply(request: ChatRequest) -> ChatResponse:
    return _handle_chat(request)


@versioned_router.post("", response_model=ChatResponse)
def create_chat_reply_v1(request: ChatRequest) -> ChatResponse:
    return _handle_chat(request)
