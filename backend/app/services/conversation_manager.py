from __future__ import annotations

from typing import Protocol
from uuid import uuid4
from time import perf_counter

from sqlalchemy.orm import Session

from app.knowledge import KnowledgeRetrievalMatch, KnowledgeRetrievalService
from app.llm import (
    AIExecutionMode,
    AIExecutionOwner,
    AIExecutionPolicyRequest,
    LLMControlledGenerationRequest,
    LLMGenerationOrchestrationRequest,
    LLMRuntimeFacade,
    LLMRuntimeResponse,
    LLMShadowModeRequest,
)
from app.llm.runtime_trace import AIRuntimeTraceRegistry, AIRuntimeTraceSession
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


def _should_use_controlled_generation(
    intent_match: ChatIntentMatch,
    response: ChatResponse,
    *,
    has_active_workflow: bool,
) -> bool:
    if response.workflow is not None or has_active_workflow:
        return False
    return intent_match.intent in {
        ChatIntent.UNKNOWN,
        ChatIntent.APPOINTMENT_HELP,
        ChatIntent.CANCEL_APPOINTMENT_HELP,
    }


class ConversationManager:
    def __init__(
        self,
        session: Session,
        *,
        deterministic_engine: DeterministicChatEngine,
        knowledge_retrieval_service: KnowledgeRetrievalService | None = None,
        llm_runtime_facade: LLMRuntimeFacade | None = None,
        runtime_trace_enabled: bool = False,
    ) -> None:
        self._session = session
        self._deterministic_engine = deterministic_engine
        self._knowledge_retrieval_service = knowledge_retrieval_service
        self._llm_runtime_facade = llm_runtime_facade
        self._workflow_engine = WorkflowEngine(session)
        self._runtime_trace_enabled = runtime_trace_enabled

    def _resolve_route(self, response: ChatResponse) -> ChatRoutingTarget:
        if response.workflow is not None:
            return ChatRoutingTarget.WORKFLOW_ENGINE
        if response.knowledge_source is not None:
            return ChatRoutingTarget.FUTURE_AI_LAYER
        return ChatRoutingTarget.DETERMINISTIC_ENGINE

    def _resolve_controlled_route(self, response: ChatResponse) -> ChatRoutingTarget:
        if response.workflow is not None:
            return ChatRoutingTarget.WORKFLOW_ENGINE
        return ChatRoutingTarget.FUTURE_AI_LAYER

    def _retrieve_knowledge_match(
        self,
        message: str,
        base_context: ChatConversationContext,
        *,
        runtime_trace: AIRuntimeTraceSession | None = None,
    ) -> KnowledgeRetrievalMatch | None:
        if self._knowledge_retrieval_service is None or _has_active_workflow(base_context.current_workflow):
            return None
        return self._knowledge_retrieval_service.retrieve_top_match(message, runtime_trace=runtime_trace)

    def _run_shadow_mode(
        self,
        *,
        request: ChatRequest,
        response: ChatResponse,
        resolved_filters: ChatSearchFilters | None,
        intent_match: ChatIntentMatch,
        knowledge_match: KnowledgeRetrievalMatch | None,
        runtime_trace: AIRuntimeTraceSession,
    ) -> None:
        if self._llm_runtime_facade is None or response.conversation is None:
            runtime_trace.update_stage(
                "runtime_facade",
                {"entered": False, "skipped": True, "reason": "LLM runtime facade is unavailable."},
            )
            runtime_trace.mark_llm_not_invoked("runtime_facade", "LLM runtime facade is unavailable.")
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
            dispatch = self._llm_runtime_facade.run_shadow_mode(
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
                        "ai_runtime_trace_id": runtime_trace.trace_id,
                    },
                ),
                asynchronous=not runtime_trace.enabled,
                runtime_trace=runtime_trace,
            )
            runtime_trace.update_stage(
                "runtime_facade",
                {
                    "entered": True,
                    "skipped": not dispatch.scheduled and dispatch.diagnostic is not None and dispatch.diagnostic.status.value == "SKIPPED",
                    "reason": dispatch.decision.fallback_reason or dispatch.decision.routing_reason,
                },
            )
            runtime_trace.update_stage(
                "execution_policy",
                {
                    "llm_enabled": dispatch.decision.activation.llm_enabled,
                    "selected_provider": dispatch.decision.selected_provider_name,
                    "provider_healthy": dispatch.decision.activation.selected_provider_healthy,
                    "generation_allowed": dispatch.decision.activation.generation_allowed,
                    "generation_available": dispatch.decision.activation.generation_available,
                    "execution_owner": dispatch.decision.official_response_owner.value,
                    "decision": dispatch.decision.execution_mode.value,
                    "reason": dispatch.decision.fallback_reason or dispatch.decision.routing_reason,
                },
            )
            if dispatch.diagnostic is not None and dispatch.diagnostic.status.value == "SKIPPED":
                runtime_trace.mark_llm_not_invoked(
                    "execution_policy",
                    dispatch.decision.fallback_reason or dispatch.decision.routing_reason,
                )
        except Exception as exc:
            runtime_trace.record_exception("runtime_facade", exc, converted_to_fallback=True)
            runtime_trace.update_stage(
                "runtime_facade",
                {"entered": True, "skipped": True, "reason": "Shadow mode raised an exception."},
            )
            runtime_trace.mark_llm_not_invoked("runtime_facade", "Shadow mode raised an exception.")
            return

    def _run_controlled_generation(
        self,
        *,
        request: ChatRequest,
        base_context: ChatConversationContext,
        response: ChatResponse,
        resolved_filters: ChatSearchFilters | None,
        intent_match: ChatIntentMatch,
        knowledge_match: KnowledgeRetrievalMatch | None,
        runtime_trace: AIRuntimeTraceSession,
    ) -> tuple[ChatResponse, bool]:
        if self._llm_runtime_facade is None:
            runtime_trace.update_stage(
                "controlled_generation",
                {
                    "entered": False,
                    "skipped": True,
                    "reason": "LLM runtime facade is unavailable.",
                },
            )
            runtime_trace.mark_llm_not_invoked(
                "runtime_facade",
                "LLM runtime facade is unavailable.",
            )
            return response, False

        if not _should_use_controlled_generation(
            intent_match,
            response,
            has_active_workflow=_has_active_workflow(base_context.current_workflow),
        ):
            runtime_trace.update_stage(
                "controlled_generation",
                {
                    "entered": False,
                    "skipped": True,
                    "reason": "Execution policy kept this request on the deterministic path.",
                },
            )
            runtime_trace.mark_llm_not_invoked(
                "execution_policy",
                "Execution policy kept this request on the deterministic path.",
            )
            return response, False

        conversation_history = (
            [item.model_dump(mode="json") for item in request.conversation.history]
            if request.conversation is not None
            else []
        )
        conversation_state = {
            "conversation_id": base_context.conversation_id,
            "context": base_context.model_dump(mode="json"),
            "history": conversation_history,
        }
        if resolved_filters is not None:
            conversation_state["active_filters"] = resolved_filters.model_dump(mode="json")

        knowledge_route = _should_use_knowledge_response(intent_match) and knowledge_match is not None
        baseline_route = (
            ChatRoutingTarget.WORKFLOW_ENGINE
            if response.workflow is not None
            else ChatRoutingTarget.FUTURE_AI_LAYER
            if response.knowledge_source is not None
            else ChatRoutingTarget.DETERMINISTIC_ENGINE
        )
        deterministic_response = LLMRuntimeResponse(
            message=response.message,
            data={},
            metadata={
                "response_owner": baseline_route.value,
                "knowledge_source": (
                    response.knowledge_source.model_dump(mode="json")
                    if response.knowledge_source is not None
                    else None
                ),
            },
        )
        policy_request = AIExecutionPolicyRequest(
            preferred_mode=AIExecutionMode.HYBRID if knowledge_route else AIExecutionMode.LLM_ONLY,
            intent_name=intent_match.intent.value,
            has_active_workflow=False,
            knowledge_eligible=knowledge_route,
            knowledge_match_available=knowledge_match is not None,
        )
        composition = self._llm_runtime_facade.compose()
        provider_name = composition.activation_status.selected_provider_name
        runtime_trace.set_root("selected_provider", provider_name)
        runtime_trace.set_root("execution_mode", policy_request.preferred_mode.value)
        runtime_trace.set_root("activation_status", composition.activation_status.model_dump(mode="json"))
        try:
            result = self._llm_runtime_facade.run_controlled_generation(
                LLMControlledGenerationRequest(
                    correlation_id=base_context.conversation_id,
                    policy_request=policy_request,
                    deterministic_response=deterministic_response,
                    orchestration_request=LLMGenerationOrchestrationRequest(
                        user_message=request.message,
                        conversation_state=conversation_state,
                        documents=[knowledge_match.document] if knowledge_match is not None else [],
                        active_intent=intent_match.intent.value,
                        provider_name=provider_name,
                        metadata={
                            "routed_to": baseline_route.value,
                            "knowledge_used": response.knowledge_source is not None,
                            "ai_runtime_trace_id": runtime_trace.trace_id,
                        },
                    ),
                ),
                runtime_trace=runtime_trace,
            )
        except Exception as exc:
            runtime_trace.record_exception("runtime_facade", exc, converted_to_fallback=True)
            runtime_trace.update_stage(
                "controlled_generation",
                {
                    "entered": True,
                    "skipped": True,
                    "reason": "Controlled generation raised an exception.",
                },
            )
            runtime_trace.mark_llm_not_invoked(
                "runtime_facade",
                "Controlled generation raised an exception.",
            )
            return response, False

        runtime_trace.update_stage(
            "controlled_generation",
            {
                "entered": True,
                "execution_mode": result.decision.execution_mode.value,
                "execution_owner": result.decision.official_response_owner.value,
                "status": result.status.value,
                "reason": result.fallback_reason or result.decision.routing_reason,
            },
        )

        if result.final_response is None or result.status.value != "SUCCEEDED":
            return response, False

        return (
            ChatResponse(
                intent=ChatIntent.UNKNOWN,
                message=result.final_response.message,
                data=[],
                search_filters=resolved_filters,
                help_steps=[],
                knowledge_source=response.knowledge_source,
            ),
            True,
        )

    def handle(self, request: ChatRequest) -> ChatResponse:
        base_context = _build_context_from_request(request.conversation)
        runtime_trace = AIRuntimeTraceSession(
            enabled=self._runtime_trace_enabled,
            conversation_id=base_context.conversation_id,
        )
        AIRuntimeTraceRegistry.register(runtime_trace)
        started_at = perf_counter()
        try:
            runtime_trace.attach_user_message(request.message)
            runtime_trace.update_stage(
                "conversation_manager",
                {
                    "entered": True,
                    "completed": False,
                    "conversation_loaded": request.conversation is not None,
                    "history_size": len(request.conversation.history) if request.conversation else 0,
                    "conversation_state": {
                        "status": base_context.status.value,
                        "turn_count": base_context.turn_count,
                        "has_active_workflow": _has_active_workflow(base_context.current_workflow),
                        "selected_doctor_id": base_context.selected_doctor_id,
                    },
                },
            )
            current_filters = extract_chat_search_filters(request.message)
            resolved_filters = _merge_search_filters(base_context.active_filters, current_filters)
            intent_match = detect_chat_intent(request.message)
            runtime_trace.set_root("intent", intent_match.intent.value)
            runtime_trace.update_stage(
                "conversation_manager",
                {
                    "intent": intent_match.intent.value,
                    "routing_metadata": {
                        "current_filters": current_filters.model_dump(mode="json") if current_filters else {},
                        "resolved_filters": resolved_filters.model_dump(mode="json") if resolved_filters else {},
                    },
                },
            )
            knowledge_match = self._retrieve_knowledge_match(
                request.message,
                base_context,
                runtime_trace=runtime_trace,
            )
            runtime_trace.update_stage(
                "vectorless_rag",
                {
                    "executed": (
                        self._knowledge_retrieval_service is not None
                        and not _has_active_workflow(base_context.current_workflow)
                    ),
                    "knowledge_found": knowledge_match is not None,
                    "documents_returned": 1 if knowledge_match is not None else 0,
                },
            )
            response = self._workflow_engine.handle(
                request.message,
                conversation_context=base_context,
                search_filters=resolved_filters,
                runtime_trace=runtime_trace,
            )
            runtime_trace.update_stage(
                "workflow_engine",
                {
                    "workflow_detected": response is not None and response.workflow is not None,
                    "workflow_name": (
                        response.workflow.workflow_type.value
                        if response is not None and response.workflow is not None
                        else None
                    ),
                    "business_intent": (
                        response.intent.value if response is not None else intent_match.intent.value
                    ),
                },
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
            response, controlled_generation_used = self._run_controlled_generation(
                request=request,
                base_context=base_context,
                response=response,
                resolved_filters=resolved_filters,
                intent_match=intent_match,
                knowledge_match=knowledge_match,
                runtime_trace=runtime_trace,
            )
            routed_to = (
                self._resolve_controlled_route(response)
                if controlled_generation_used
                else self._resolve_route(response)
            )
            selected_doctor_id, selected_doctor_name = _resolve_selected_doctor(
                response,
                base_context.selected_doctor_id,
                base_context.selected_doctor_name,
            )
            history_turn_count = (
                _count_user_turns(request.conversation.history) if request.conversation else 0
            )
            next_turn_count = history_turn_count if history_turn_count > 0 else base_context.turn_count + 1
            next_workflow = _next_workflow_state(response, base_context)

            response.conversation = ChatConversationContext(
                conversation_id=base_context.conversation_id,
                status=ChatConversationStatus.ACTIVE,
                turn_count=next_turn_count,
                last_intent=response.intent,
                active_filters=(
                    resolved_filters if _has_filter_values(resolved_filters) else base_context.active_filters
                ),
                selected_doctor_id=selected_doctor_id,
                selected_doctor_name=selected_doctor_name,
                last_user_message=request.message,
                last_assistant_message=response.message,
                routed_to=routed_to,
                current_workflow=next_workflow,
            )
            final_response_source = (
                "workflow_engine"
                if response.workflow is not None
                else "controlled_generation"
                if controlled_generation_used
                else "vectorless_rag"
                if response.knowledge_source is not None
                else "deterministic_engine"
            )
            runtime_trace.set_final_response(
                source=final_response_source,
                preview=response.message[:240] if response.message else None,
            )
            if not controlled_generation_used:
                runtime_trace.update_stage(
                    "runtime_validator",
                    {"pass": None, "reason": "Skipped for visible conversation handling."},
                )
                runtime_trace.update_stage(
                    "eligibility",
                    {"pass": None, "reason": "Skipped for visible conversation handling."},
                )
                runtime_trace.update_stage(
                    "composer",
                    {
                        "deterministic": response.knowledge_source is None and response.workflow is None,
                        "llm": False,
                        "hybrid": False,
                        "reason": "Visible response was finalized before controlled-generation diagnostics.",
                    },
                )
                runtime_trace.update_stage(
                    "post_processor",
                    {
                        "executed": False,
                        "reason": "Post-processing is reserved for controlled generation.",
                    },
                )
            else:
                runtime_trace.update_stage(
                    "composer",
                    {
                        "deterministic": (
                            response.knowledge_source is None
                            and response.workflow is None
                            and not controlled_generation_used
                        ),
                        "llm": controlled_generation_used and response.knowledge_source is None,
                        "hybrid": controlled_generation_used and response.knowledge_source is not None,
                        "reason": "Visible response was finalized through controlled generation.",
                    },
                )
                runtime_trace.update_stage(
                    "post_processor",
                    {
                        "executed": True,
                        "reason": "Controlled generation response was already post-processed.",
                    },
                )
            runtime_trace.update_stage(
                "final_response",
                {
                    "routed_to": response.conversation.routed_to.value,
                    "response_owner": (
                        "WORKFLOW"
                        if response.workflow is not None
                        else "LLM"
                        if controlled_generation_used
                        else "KNOWLEDGE"
                        if response.knowledge_source is not None
                        else "DETERMINISTIC"
                    ),
                    "response_source": final_response_source,
                },
            )
            runtime_trace.update_stage(
                "conversation_manager",
                {
                    "entered": True,
                    "completed": True,
                    "duration_ms": round((perf_counter() - started_at) * 1000, 3),
                    "exit": True,
                },
            )
            return response
        except Exception as exc:
            runtime_trace.record_exception("conversation_manager", exc)
            runtime_trace.update_stage(
                "conversation_manager",
                {
                    "entered": True,
                    "completed": False,
                    "duration_ms": round((perf_counter() - started_at) * 1000, 3),
                    "exit": True,
                },
            )
            raise
        finally:
            runtime_trace.emit()
            AIRuntimeTraceRegistry.unregister(runtime_trace.trace_id)
