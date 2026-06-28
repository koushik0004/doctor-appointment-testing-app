from __future__ import annotations

from typing import Protocol
from uuid import uuid4

from sqlalchemy.orm import Session

from app.schemas.chat import (
    ChatConversationContext,
    ChatConversationHistoryMessage,
    ChatConversationRequest,
    ChatConversationStatus,
    ChatRequest,
    ChatResponse,
    ChatRoutingTarget,
    ChatSearchFilters,
)
from app.services.chat_entity_extractor import extract_chat_search_filters
from app.services.chat_intent_detector import ChatIntentMatch, detect_chat_intent


class DeterministicChatEngine(Protocol):
    def generate(
        self,
        message: str,
        *,
        intent_match: ChatIntentMatch | None = None,
        search_filters: ChatSearchFilters | None = None,
        selected_doctor_name: str | None = None,
    ) -> ChatResponse:
        ...


def _filters_to_dict(filters: ChatSearchFilters | None) -> dict[str, object | None]:
    if filters is None:
        return {}
    return filters.model_dump()


def _has_filter_values(filters: ChatSearchFilters | None) -> bool:
    return any(value is not None for value in _filters_to_dict(filters).values())


def _merge_search_filters(
    base_filters: ChatSearchFilters | None,
    override_filters: ChatSearchFilters | None,
) -> ChatSearchFilters | None:
    merged_values = _filters_to_dict(base_filters)
    for key, value in _filters_to_dict(override_filters).items():
        if value is not None:
            merged_values[key] = value

    if not any(value is not None for value in merged_values.values()):
        return None

    return ChatSearchFilters(**merged_values)


def _last_history_filters(history: list[ChatConversationHistoryMessage]) -> ChatSearchFilters | None:
    for item in reversed(history):
        if _has_filter_values(item.search_filters):
            return item.search_filters
    return None


def _last_history_intent(history: list[ChatConversationHistoryMessage]):
    for item in reversed(history):
        if item.intent is not None:
            return item.intent
    return None


def _last_selected_doctor(history: list[ChatConversationHistoryMessage]) -> tuple[int | None, str | None]:
    for item in reversed(history):
        if item.selected_doctor_id is not None or item.selected_doctor_name is not None:
            return item.selected_doctor_id, item.selected_doctor_name
    return None, None


def _last_message_for_role(history: list[ChatConversationHistoryMessage], role: str) -> str | None:
    for item in reversed(history):
        if item.role == role:
            return item.text
    return None


def _count_user_turns(history: list[ChatConversationHistoryMessage]) -> int:
    return sum(1 for item in history if item.role == "user")


def _build_context_from_request(conversation: ChatConversationRequest | None) -> ChatConversationContext:
    history = conversation.history if conversation else []
    history_filters = _last_history_filters(history)
    history_intent = _last_history_intent(history)
    selected_doctor_id, selected_doctor_name = _last_selected_doctor(history)
    history_turn_count = _count_user_turns(history)

    if conversation and conversation.context is not None:
        context = conversation.context.model_copy(deep=True)
        context.turn_count = max(context.turn_count, history_turn_count)
        context.active_filters = _merge_search_filters(
            context.active_filters,
            history_filters,
        )
        context.last_intent = history_intent or context.last_intent
        context.selected_doctor_id = selected_doctor_id or context.selected_doctor_id
        context.selected_doctor_name = selected_doctor_name or context.selected_doctor_name
        context.last_user_message = _last_message_for_role(history, "user") or context.last_user_message
        context.last_assistant_message = (
            _last_message_for_role(history, "assistant") or context.last_assistant_message
        )
        if conversation.conversation_id:
            context.conversation_id = conversation.conversation_id
        return context

    return ChatConversationContext(
        conversation_id=(conversation.conversation_id if conversation and conversation.conversation_id else str(uuid4())),
        status=ChatConversationStatus.ACTIVE,
        turn_count=history_turn_count,
        last_intent=history_intent,
        active_filters=history_filters,
        selected_doctor_id=selected_doctor_id,
        selected_doctor_name=selected_doctor_name,
        last_user_message=_last_message_for_role(history, "user"),
        last_assistant_message=_last_message_for_role(history, "assistant"),
        routed_to=ChatRoutingTarget.DETERMINISTIC_ENGINE,
    )


def _resolve_selected_doctor(
    response: ChatResponse,
    fallback_doctor_id: int | None,
    fallback_doctor_name: str | None,
) -> tuple[int | None, str | None]:
    if not response.data:
        return fallback_doctor_id, fallback_doctor_name

    doctor_ids = {item.doctor_id for item in response.data}
    if len(doctor_ids) != 1:
        return None, None

    first_item = response.data[0]
    return first_item.doctor_id, first_item.doctor_name


class ConversationManager:
    def __init__(
        self,
        session: Session,
        *,
        deterministic_engine: DeterministicChatEngine,
    ) -> None:
        self._session = session
        self._deterministic_engine = deterministic_engine

    def _resolve_route(self, intent_match: ChatIntentMatch) -> ChatRoutingTarget:
        del intent_match
        return ChatRoutingTarget.DETERMINISTIC_ENGINE

    def handle(self, request: ChatRequest) -> ChatResponse:
        del self._session

        base_context = _build_context_from_request(request.conversation)
        current_filters = extract_chat_search_filters(request.message)
        resolved_filters = _merge_search_filters(base_context.active_filters, current_filters)
        intent_match = detect_chat_intent(request.message)
        routed_to = self._resolve_route(intent_match)

        response = self._deterministic_engine.generate(
            request.message,
            intent_match=intent_match,
            search_filters=resolved_filters,
            selected_doctor_name=base_context.selected_doctor_name,
        )

        selected_doctor_id, selected_doctor_name = _resolve_selected_doctor(
            response,
            base_context.selected_doctor_id,
            base_context.selected_doctor_name,
        )
        history_turn_count = _count_user_turns(request.conversation.history) if request.conversation else 0
        next_turn_count = history_turn_count if history_turn_count > 0 else base_context.turn_count + 1

        response.conversation = ChatConversationContext(
            conversation_id=base_context.conversation_id,
            status=ChatConversationStatus.ACTIVE,
            turn_count=next_turn_count,
            last_intent=response.intent,
            active_filters=resolved_filters if _has_filter_values(resolved_filters) else base_context.active_filters,
            selected_doctor_id=selected_doctor_id,
            selected_doctor_name=selected_doctor_name,
            last_user_message=request.message,
            last_assistant_message=response.message,
            routed_to=routed_to,
        )
        return response
