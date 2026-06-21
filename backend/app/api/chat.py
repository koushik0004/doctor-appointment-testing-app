from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.errors import chat_service_error
from app.db.database import get_db
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import create_chat_response

router = APIRouter(prefix="/chat", tags=["chat"])
versioned_router = APIRouter(prefix="/v1/chat", tags=["chat"])


def _handle_chat(request: ChatRequest, session: Session) -> ChatResponse:
    try:
        return create_chat_response(session, request)
    except Exception as exc:  # pragma: no cover
        raise chat_service_error() from exc


@router.post("", response_model=ChatResponse)
def create_chat_reply(
    request: ChatRequest,
    session: Session = Depends(get_db),
) -> ChatResponse:
    return _handle_chat(request, session)


@versioned_router.post("", response_model=ChatResponse)
def create_chat_reply_v1(
    request: ChatRequest,
    session: Session = Depends(get_db),
) -> ChatResponse:
    return _handle_chat(request, session)
