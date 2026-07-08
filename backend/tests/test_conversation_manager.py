from __future__ import annotations

import json
from dataclasses import dataclass

from app.knowledge.documents import (
    KnowledgeDocument,
    KnowledgeDocumentAudience,
    KnowledgeDocumentDomain,
    KnowledgeDocumentSourceType,
    KnowledgeDocumentStatus,
)
from app.knowledge.retrieval import KnowledgeRetrievalMatch
from app.llm import LLMShadowModeDispatchResult
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

    def retrieve_top_match(self, query: str) -> KnowledgeRetrievalMatch | None:
        self.calls.append(query)
        return self.match


class StubRuntimeFacade:
    def __init__(self, *, should_raise: bool = False) -> None:
        self.should_raise = should_raise
        self.calls: list[object] = []

    def run_shadow_mode(self, request, *, asynchronous=True, runtime_trace=None) -> LLMShadowModeDispatchResult:
        del asynchronous, runtime_trace
        self.calls.append(request)
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
    manager = ConversationManager(
        session=None,
        deterministic_engine=deterministic,
        knowledge_retrieval_service=knowledge_service,
    )
    manager._workflow_engine = StubWorkflowEngine(response=None)

    response = manager.handle(ChatRequest(message="What is telemedicine?"))

    assert knowledge_service.calls == ["What is telemedicine?"]
    assert deterministic.calls == []
    assert response.knowledge_source is not None
    assert response.knowledge_source.document_id == "faq.telemedicine.general"
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
    manager = ConversationManager(
        session=None,
        deterministic_engine=deterministic,
        knowledge_retrieval_service=knowledge_service,
    )
    manager._workflow_engine = StubWorkflowEngine(response=None)

    response = manager.handle(ChatRequest(message="Do you support pharmacy refills?"))

    assert knowledge_service.calls == ["Do you support pharmacy refills?"]
    assert deterministic.calls == ["Do you support pharmacy refills?"]
    assert response.knowledge_source is None
    assert response.conversation is not None
    assert response.conversation.routed_to == ChatRoutingTarget.DETERMINISTIC_ENGINE


def test_conversation_manager_keeps_workflow_responses_first():
    deterministic = StubDeterministicEngine(
        ChatResponse(intent=ChatIntent.UNKNOWN, message="fallback")
    )
    knowledge_service = StubKnowledgeService(match=_knowledge_match(), calls=[])
    manager = ConversationManager(
        session=None,
        deterministic_engine=deterministic,
        knowledge_retrieval_service=knowledge_service,
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
    assert response.workflow is not None
    assert response.knowledge_source is None
    assert response.conversation is not None
    assert response.conversation.routed_to == ChatRoutingTarget.WORKFLOW_ENGINE


def test_conversation_manager_skips_knowledge_lookup_for_active_workflows():
    deterministic = StubDeterministicEngine(
        ChatResponse(intent=ChatIntent.UNKNOWN, message="fallback")
    )
    knowledge_service = StubKnowledgeService(match=_knowledge_match(), calls=[])
    manager = ConversationManager(
        session=None,
        deterministic_engine=deterministic,
        knowledge_retrieval_service=knowledge_service,
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
    assert response.conversation is not None
    assert response.conversation.routed_to == ChatRoutingTarget.DETERMINISTIC_ENGINE


def test_conversation_manager_triggers_shadow_mode_without_changing_response():
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

    assert response.message == "fallback"
    assert len(facade.calls) == 1
    shadow_request = facade.calls[0]
    assert shadow_request.user_message == "Do you support pharmacy refills?"
    assert shadow_request.official_response_owner.value == "DETERMINISTIC"
    assert shadow_request.correlation_id == response.conversation.conversation_id


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


def test_conversation_manager_emits_runtime_trace_when_enabled(caplog):
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

    with caplog.at_level("INFO"):
        response = manager.handle(
            ChatRequest(message="My name is Ava Thompson and my email is ava@example.com")
        )

    assert response.message == "fallback"
    trace_record = next(
        record for record in caplog.records if record.message.startswith("ai_runtime_trace ")
    )
    payload = json.loads(trace_record.message.removeprefix("ai_runtime_trace "))
    assert payload["user_message"] == "My name is [REDACTED_NAME] and my email is [REDACTED_EMAIL]"
    assert payload["llm_not_invoked"] is True
    assert payload["stop_component"] == "runtime_facade"
    assert payload["final_response"]["response_source"] == "deterministic_engine"
