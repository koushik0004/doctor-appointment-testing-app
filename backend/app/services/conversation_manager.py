from __future__ import annotations

from typing import Protocol
from uuid import uuid4

from sqlalchemy.orm import Session

from app.knowledge import KnowledgeRetrievalMatch, KnowledgeRetrievalService
from app.llm import AIExecutionOwner, LLMRuntimeFacade, LLMShadowModeRequest
from app.schemas.chat import (
    ChatConversationContext,
    ChatConversationHistoryMessage,
    ChatConversationRequest,
    ChatConversationStatus,
    ChatIntent,
    ChatKnowledgeSource,
    ChatRequest,
    ChatResponse,
    ChatRoutingTarget,
    ChatSearchFilters,
    ChatWorkflowState,
    ChatWorkflowStatus,
)
from app.services.chat_entity_extractor import extract_chat_search_filters
from app.services.chat_intent_detector import ChatIntentMatch, detect_chat_intent
from app.services.workflow_engine import WorkflowEngine


def _join_english_list(items: list[str]) -> str:
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return f"{items[0]} and {items[1]}"
    return ", ".join(items[:-1]) + f", and {items[-1]}"


def _knowledge_document_message(document) -> str:
    if isinstance(document.content, dict):
        help_items = [
            item
            for item in document.content.get("can_help_with", [])
            if isinstance(item, str) and item.strip()
        ]
        if help_items:
            return f"I can help with {_join_english_list(help_items)}."

    if isinstance(document.content, str):
        content = " ".join(line.strip() for line in document.content.splitlines() if line.strip())
        if document.prompt_hints is not None and document.prompt_hints.safe_to_quote and content:
            return content

    if document.summary.strip():
        return document.summary.strip()

    return document.title


class DeterministicChatEngine(Protocol):
    def generate(
        self,
        message: str,
        *,
        intent_match: ChatIntentMatch | None = None,
        search_filters: ChatSearchFilters | None = None,
        selected_doctor_name: str | None = None,
        conversation_context: ChatConversationContext | None = None,
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


def _next_workflow_state(
    response: ChatResponse,
    base_context: ChatConversationContext,
) -> ChatWorkflowState | None:
    if response.workflow is not None:
        return ChatWorkflowState(
            workflow_type=response.workflow.workflow_type,
            status=response.workflow.status,
            missing_fields=response.workflow.missing_fields,
            draft=response.workflow.draft,
        )

    if base_context.current_workflow and base_context.current_workflow.status != ChatWorkflowStatus.COMPLETED:
        return base_context.current_workflow

    return None


def _has_active_workflow(workflow: ChatWorkflowState | None) -> bool:
    return workflow is not None and workflow.status != ChatWorkflowStatus.COMPLETED


def _resolve_selected_doctor(
    response: ChatResponse,
    fallback_doctor_id: int | None,
    fallback_doctor_name: str | None,
) -> tuple[int | None, str | None]:
    if response.workflow and response.workflow.draft.doctor_id is not None:
        return response.workflow.draft.doctor_id, response.workflow.draft.doctor_name

    if not response.data:
        return fallback_doctor_id, fallback_doctor_name

    doctor_ids = {item.doctor_id for item in response.data}
    if len(doctor_ids) != 1:
        return None, None

    first_item = response.data[0]
    return first_item.doctor_id, first_item.doctor_name


def _knowledge_source_from_match(knowledge_match: KnowledgeRetrievalMatch) -> ChatKnowledgeSource:
    document = knowledge_match.document
    return ChatKnowledgeSource(
        document_id=document.id,
        title=document.title,
        source_type=document.source_type,
        source_path=document.source_path,
        domain=document.domain,
        audience=document.audience,
        status=document.status,
        matched_terms=list(knowledge_match.matched_terms),
        score=knowledge_match.score,
    )


def _should_use_knowledge_response(intent_match: ChatIntentMatch) -> bool:
    return intent_match.intent in {ChatIntent.UNKNOWN, ChatIntent.APPOINTMENT_HELP}


class ConversationManager:
    def __init__(
        self,
        session: Session,
        *,
        deterministic_engine: DeterministicChatEngine,
        knowledge_retrieval_service: KnowledgeRetrievalService | None = None,
        llm_runtime_facade: LLMRuntimeFacade | None = None,
    ) -> None:
        self._session = session
        self._deterministic_engine = deterministic_engine
        self._knowledge_retrieval_service = knowledge_retrieval_service
        self._llm_runtime_facade = llm_runtime_facade
        self._workflow_engine = WorkflowEngine(session)

    def _resolve_route(self, response: ChatResponse) -> ChatRoutingTarget:
        if response.workflow is not None:
            return ChatRoutingTarget.WORKFLOW_ENGINE
        if response.knowledge_source is not None:
            return ChatRoutingTarget.FUTURE_AI_LAYER
        return ChatRoutingTarget.DETERMINISTIC_ENGINE

    def _retrieve_knowledge_match(self, message: str, base_context: ChatConversationContext) -> KnowledgeRetrievalMatch | None:
        if self._knowledge_retrieval_service is None or _has_active_workflow(base_context.current_workflow):
            return None
        return self._knowledge_retrieval_service.retrieve_top_match(message)

    def _run_shadow_mode(
        self,
        *,
        request: ChatRequest,
        response: ChatResponse,
        resolved_filters: ChatSearchFilters | None,
        intent_match: ChatIntentMatch,
        knowledge_match: KnowledgeRetrievalMatch | None,
    ) -> None:
        if self._llm_runtime_facade is None or response.conversation is None:
            return

        conversation_history = (
            [item.model_dump(mode="json") for item in request.conversation.history]
            if request.conversation is not None
            else []
        )
        conversation_state = {
            "conversation_id": response.conversation.conversation_id,
            "context": response.conversation.model_dump(mode="json"),
            "history": conversation_history,
        }
        if resolved_filters is not None:
            conversation_state["active_filters"] = resolved_filters.model_dump(mode="json")

        try:
            self._llm_runtime_facade.run_shadow_mode(
                LLMShadowModeRequest(
                    correlation_id=response.conversation.conversation_id,
                    user_message=request.message,
                    official_response_owner=(
                        AIExecutionOwner.WORKFLOW
                        if response.workflow is not None
                        else (
                            AIExecutionOwner.KNOWLEDGE
                            if response.knowledge_source is not None
                            else AIExecutionOwner.DETERMINISTIC
                        )
                    ),
                    official_intent_name=response.intent.value,
                    has_active_workflow=_has_active_workflow(response.conversation.current_workflow),
                    knowledge_eligible=_should_use_knowledge_response(intent_match),
                    knowledge_match_available=knowledge_match is not None,
                    conversation_state=conversation_state,
                    documents=[knowledge_match.document] if knowledge_match is not None else [],
                    metadata={
                        "routed_to": response.conversation.routed_to.value,
                        "knowledge_used": response.knowledge_source is not None,
                    },
                )
            )
        except Exception:
            return

    def handle(self, request: ChatRequest) -> ChatResponse:
        base_context = _build_context_from_request(request.conversation)
        current_filters = extract_chat_search_filters(request.message)
        resolved_filters = _merge_search_filters(base_context.active_filters, current_filters)
        intent_match = detect_chat_intent(request.message)
        knowledge_match = self._retrieve_knowledge_match(request.message, base_context)
        response = self._workflow_engine.handle(
            request.message,
            conversation_context=base_context,
            search_filters=resolved_filters,
        )
        if response is None:
            if knowledge_match is not None and _should_use_knowledge_response(intent_match):
                response = ChatResponse(
                    intent=ChatIntent.UNKNOWN,
                    message=_knowledge_document_message(knowledge_match.document),
                    data=[],
                    search_filters=resolved_filters,
                    help_steps=[],
                    knowledge_source=_knowledge_source_from_match(knowledge_match),
                )
            else:
                response = self._deterministic_engine.generate(
                    request.message,
                    intent_match=intent_match,
                    search_filters=resolved_filters,
                    selected_doctor_name=base_context.selected_doctor_name,
                    conversation_context=base_context,
                )
        routed_to = self._resolve_route(response)
        selected_doctor_id, selected_doctor_name = _resolve_selected_doctor(
            response,
            base_context.selected_doctor_id,
            base_context.selected_doctor_name,
        )
        history_turn_count = _count_user_turns(request.conversation.history) if request.conversation else 0
        next_turn_count = history_turn_count if history_turn_count > 0 else base_context.turn_count + 1
        next_workflow = _next_workflow_state(response, base_context)

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
            current_workflow=next_workflow,
        )
        self._run_shadow_mode(
            request=request,
            response=response,
            resolved_filters=resolved_filters,
            intent_match=intent_match,
            knowledge_match=knowledge_match,
        )
        return response
