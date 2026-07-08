from __future__ import annotations

import json
from dataclasses import dataclass
from types import SimpleNamespace

from app.knowledge.documents import (
    KnowledgeDocument,
    KnowledgeDocumentAudience,
    KnowledgeDocumentDomain,
    KnowledgeDocumentSourceType,
    KnowledgeDocumentStatus,
)
from app.knowledge.retrieval import KnowledgeRetrievalMatch
from app.llm import (
    AIExecutionActivationSnapshot,
    AIExecutionDecision,
    AIExecutionMode,
    AIExecutionOwner,
    LLMControlledGenerationResult,
    LLMControlledGenerationStatus,
    LLMShadowModeDispatchResult,
    LLMRuntimeResponse,
)
from app.schemas.chat import (
    ChatConversationRequest,
    ChatConversationContext,
    ChatIntent,
    ChatRequest,
    ChatResponse,
    ChatRoutingTarget,
    ChatWorkflowDraft,
    ChatWorkflowResult,
    ChatWorkflowStatus,
    ChatWorkflowType,
)
from app.services.conversation_manager import ConversationManager


class StubWorkflowEngine:
    def __init__(self, response: ChatResponse | None) -> None:
        self.response = response
        self.calls: list[str] = []

    def handle(self, message: str, **_: object) -> ChatResponse | None:
        self.calls.append(message)
        return self.response


class StubDeterministicEngine:
    def __init__(self, response: ChatResponse) -> None:
        self.response = response
        self.calls: list[str] = []

    def generate(self, message: str, **_: object) -> ChatResponse:
        self.calls.append(message)
        return self.response


@dataclass
class StubKnowledgeService:
    match: KnowledgeRetrievalMatch | None
    calls: list[str]

    def retrieve_top_match(self, query: str, **_: object) -> KnowledgeRetrievalMatch | None:
        self.calls.append(query)
        return self.match


class StubRuntimeFacade:
    def __init__(self, *, should_raise: bool = False) -> None:
        self.should_raise = should_raise
        self.shadow_calls: list[object] = []
        self.controlled_calls: list[object] = []

    def compose(self):
        return SimpleNamespace(
            activation_status=SimpleNamespace(
                selected_provider_name="openai",
                model_dump=lambda mode="json": {"selected_provider_name": "openai"},
            )
        )

    def run_shadow_mode(self, request, *, asynchronous=True, runtime_trace=None) -> LLMShadowModeDispatchResult:
        del asynchronous, runtime_trace
        self.shadow_calls.append(request)
        if self.should_raise:
            raise RuntimeError("shadow execution failed")
        return LLMShadowModeDispatchResult(
            decision={
                "requested_mode": "SHADOW",
                "execution_mode": "SHADOW",
                "primary_owner": "DETERMINISTIC",
                "official_response_owner": "DETERMINISTIC",
                "activation": {
                    "llm_enabled": True,
                    "shadow_mode": True,
                    "generation_allowed": True,
                    "generation_available": True,
                    "provider_readiness": True,
                    "selected_provider_name": "openai",
                    "selected_provider_enabled": True,
                    "selected_provider_healthy": True,
                    "status_reason": "shadow enabled",
                },
                "routing_reason": "test",
                "should_execute_shadow": True,
                "should_execute_llm": True,
            }
        )

    def run_controlled_generation(self, request, *, runtime_trace=None) -> LLMControlledGenerationResult:
        del runtime_trace
        self.controlled_calls.append(request)
        if self.should_raise:
            raise RuntimeError("controlled generation failed")
        execution_mode = request.policy_request.preferred_mode
        owner = (
            AIExecutionOwner.KNOWLEDGE
            if execution_mode.value == "HYBRID" and request.policy_request.knowledge_eligible
            else AIExecutionOwner.LLM
        )
        return LLMControlledGenerationResult(
            request_id=request.request_id,
            correlation_id=request.correlation_id,
            decision=AIExecutionDecision(
                requested_mode=request.policy_request.preferred_mode,
                execution_mode=execution_mode,
                primary_owner=owner,
                official_response_owner=owner,
                activation=AIExecutionActivationSnapshot(
                    llm_enabled=True,
                    shadow_mode=False,
                    generation_allowed=True,
                    generation_available=True,
                    provider_readiness=True,
                    selected_provider_name="openai",
                    selected_provider_enabled=True,
                    selected_provider_healthy=True,
                    status_reason="generation enabled",
                ),
                should_execute_llm=True,
                routing_reason="test",
            ),
            status=LLMControlledGenerationStatus.SUCCEEDED,
            final_response=LLMRuntimeResponse(
                message="Claude guidance: seek a neurologist first.",
            ),
        )


def _knowledge_match() -> KnowledgeRetrievalMatch:
    document = KnowledgeDocument(
        id="faq.telemedicine.general",
        title="Telemedicine Appointments",
        source_type=KnowledgeDocumentSourceType.MARKDOWN,
        source_path="faq/telemedicine.md",
        domain=KnowledgeDocumentDomain.FAQ,
        audience=KnowledgeDocumentAudience.PATIENT,
        status=KnowledgeDocumentStatus.ACTIVE,
        version="1.0",
        tags=["telemedicine"],
        priority=10,
        summary="Telemedicine summary.",
        content="# Telemedicine Appointments\n\nTelemedicine is a remote appointment option.",
    )
    return KnowledgeRetrievalMatch(document=document, score=12, matched_terms=("telemedicine",))


def test_conversation_manager_returns_knowledge_before_deterministic_fallback():
    deterministic = StubDeterministicEngine(
        ChatResponse(
            intent=ChatIntent.APPOINTMENT_HELP,
            message="Here is how to book an appointment in the app.",
        )
    )
    knowledge_service = StubKnowledgeService(match=_knowledge_match(), calls=[])
    facade = StubRuntimeFacade()
    manager = ConversationManager(
        session=None,
        deterministic_engine=deterministic,
        knowledge_retrieval_service=knowledge_service,
        llm_runtime_facade=facade,
    )
    manager._workflow_engine = StubWorkflowEngine(response=None)

    response = manager.handle(ChatRequest(message="What is telemedicine?"))

    assert knowledge_service.calls == ["What is telemedicine?"]
    assert deterministic.calls == []
    assert len(facade.controlled_calls) == 1
    controlled_request = facade.controlled_calls[0]
    assert controlled_request.policy_request.preferred_mode.value == "HYBRID"
    assert response.knowledge_source is not None
    assert response.knowledge_source.document_id == "faq.telemedicine.general"
    assert response.message == "Claude guidance: seek a neurologist first."
    assert response.conversation is not None
    assert response.conversation.routed_to == ChatRoutingTarget.FUTURE_AI_LAYER


def test_conversation_manager_falls_back_when_knowledge_is_missing():
    deterministic = StubDeterministicEngine(
        ChatResponse(
            intent=ChatIntent.UNKNOWN,
            message="I can help with available doctors, specializations, consultation fees, and appointment slots.",
        )
    )
    knowledge_service = StubKnowledgeService(match=None, calls=[])
    facade = StubRuntimeFacade()
    manager = ConversationManager(
        session=None,
        deterministic_engine=deterministic,
        knowledge_retrieval_service=knowledge_service,
        llm_runtime_facade=facade,
    )
    manager._workflow_engine = StubWorkflowEngine(response=None)

    response = manager.handle(ChatRequest(message="Do you support pharmacy refills?"))

    assert knowledge_service.calls == ["Do you support pharmacy refills?"]
    assert deterministic.calls == ["Do you support pharmacy refills?"]
    assert len(facade.controlled_calls) == 1
    assert response.knowledge_source is None
    assert response.message == "Claude guidance: seek a neurologist first."
    assert response.conversation is not None
    assert response.conversation.routed_to == ChatRoutingTarget.FUTURE_AI_LAYER


def test_conversation_manager_keeps_workflow_responses_first():
    deterministic = StubDeterministicEngine(
        ChatResponse(intent=ChatIntent.UNKNOWN, message="fallback")
    )
    knowledge_service = StubKnowledgeService(match=_knowledge_match(), calls=[])
    facade = StubRuntimeFacade()
    manager = ConversationManager(
        session=None,
        deterministic_engine=deterministic,
        knowledge_retrieval_service=knowledge_service,
        llm_runtime_facade=facade,
    )
    manager._workflow_engine = StubWorkflowEngine(
        response=ChatResponse(
            intent=ChatIntent.BOOK_APPOINTMENT,
            message="Please share the patient's full name.",
            workflow=ChatWorkflowResult(
                workflow_type=ChatWorkflowType.BOOK_APPOINTMENT,
                status=ChatWorkflowStatus.INPUT_REQUIRED,
                missing_fields=["patient_full_name"],
                draft=ChatWorkflowDraft(
                    doctor_id=1,
                    doctor_name="Dr. Sarah Jenkins",
                ),
            ),
        )
    )

    response = manager.handle(ChatRequest(message="Book an appointment with Dr. Sarah Jenkins tomorrow"))

    assert knowledge_service.calls == ["Book an appointment with Dr. Sarah Jenkins tomorrow"]
    assert deterministic.calls == []
    assert len(facade.controlled_calls) == 0
    assert response.workflow is not None
    assert response.knowledge_source is None
    assert response.conversation is not None
    assert response.conversation.routed_to == ChatRoutingTarget.WORKFLOW_ENGINE


def test_conversation_manager_skips_knowledge_lookup_for_active_workflows():
    deterministic = StubDeterministicEngine(
        ChatResponse(intent=ChatIntent.UNKNOWN, message="fallback")
    )
    knowledge_service = StubKnowledgeService(match=_knowledge_match(), calls=[])
    facade = StubRuntimeFacade()
    manager = ConversationManager(
        session=None,
        deterministic_engine=deterministic,
        knowledge_retrieval_service=knowledge_service,
        llm_runtime_facade=facade,
    )
    manager._workflow_engine = StubWorkflowEngine(response=None)

    response = manager.handle(
        ChatRequest(
            message="My name is Ava Thompson",
            conversation=ChatConversationRequest(
                conversation_id="conv-1",
                context=ChatConversationContext(
                    conversation_id="conv-1",
                    current_workflow={
                        "workflow_type": ChatWorkflowType.BOOK_APPOINTMENT,
                        "status": ChatWorkflowStatus.INPUT_REQUIRED,
                        "missing_fields": ["patient_full_name"],
                        "draft": {},
                    },
                ),
            ),
        )
    )

    assert knowledge_service.calls == []
    assert deterministic.calls == ["My name is Ava Thompson"]
    assert len(facade.controlled_calls) == 0
    assert response.conversation is not None
    assert response.conversation.routed_to == ChatRoutingTarget.DETERMINISTIC_ENGINE


def test_conversation_manager_uses_controlled_generation_for_low_risk_chat():
    deterministic = StubDeterministicEngine(
        ChatResponse(intent=ChatIntent.UNKNOWN, message="fallback")
    )
    facade = StubRuntimeFacade()
    manager = ConversationManager(
        session=None,
        deterministic_engine=deterministic,
        knowledge_retrieval_service=StubKnowledgeService(match=None, calls=[]),
        llm_runtime_facade=facade,
    )
    manager._workflow_engine = StubWorkflowEngine(response=None)

    response = manager.handle(ChatRequest(message="Do you support pharmacy refills?"))

    assert response.message == "Claude guidance: seek a neurologist first."
    assert len(facade.controlled_calls) == 1
    controlled_request = facade.controlled_calls[0]
    assert controlled_request.orchestration_request.user_message == "Do you support pharmacy refills?"
    assert controlled_request.policy_request.preferred_mode.value == "LLM_ONLY"
    assert controlled_request.correlation_id == response.conversation.conversation_id
    assert response.conversation is not None
    assert response.conversation.routed_to == ChatRoutingTarget.FUTURE_AI_LAYER


def test_conversation_manager_ignores_shadow_mode_failures():
    deterministic = StubDeterministicEngine(
        ChatResponse(intent=ChatIntent.UNKNOWN, message="fallback")
    )
    manager = ConversationManager(
        session=None,
        deterministic_engine=deterministic,
        knowledge_retrieval_service=StubKnowledgeService(match=None, calls=[]),
        llm_runtime_facade=StubRuntimeFacade(should_raise=True),
    )
    manager._workflow_engine = StubWorkflowEngine(response=None)

    response = manager.handle(ChatRequest(message="Hello"))

    assert response.message == "fallback"
    assert len(manager._llm_runtime_facade.controlled_calls) == 1


def test_conversation_manager_emits_runtime_trace_when_enabled(runtime_trace_log):
    deterministic = StubDeterministicEngine(
        ChatResponse(intent=ChatIntent.UNKNOWN, message="fallback")
    )
    manager = ConversationManager(
        session=None,
        deterministic_engine=deterministic,
        knowledge_retrieval_service=StubKnowledgeService(match=None, calls=[]),
        llm_runtime_facade=None,
        runtime_trace_enabled=True,
    )
    manager._workflow_engine = StubWorkflowEngine(response=None)

    response = manager.handle(
        ChatRequest(message="My name is Ava Thompson and my email is ava@example.com")
    )

    assert response.message == "fallback"
    payload = json.loads(runtime_trace_log.read_text(encoding="utf-8").splitlines()[0])
    assert payload["user_message"] == "My name is [REDACTED_NAME] and my email is [REDACTED_EMAIL]"
    assert payload["llm_not_invoked"] is True
    assert payload["stop_component"] == "runtime_facade"
    assert payload["final_response"]["response_source"] == "deterministic_engine"
