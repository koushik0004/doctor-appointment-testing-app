from copy import deepcopy

from app.knowledge import (
    KnowledgeDocument,
    KnowledgeDocumentAudience,
    KnowledgeDocumentDomain,
    KnowledgeDocumentSourceType,
    KnowledgeDocumentStatus,
)
from app.llm import (
    LLMCitation,
    LLMFinishReason,
    LLMGenerationConstraints,
    LLMGenerationOrchestrationRequest,
    LLMGenerationOrchestrationResult,
    LLMGenerationOrchestrator,
    LLMGenerationResponse,
    LLMIntegrationService,
    InMemoryLLMProviderRegistry,
    LLMMessage,
    LLMMessageRole,
    LLMReasoningConfig,
    LLMReasoningEffort,
    LLMReasoningResult,
    LLMStreamingMetadata,
    LLMStructuredOutputMode,
    LLMStructuredOutputSchema,
    LLMTokenUsage,
    LLMToolCall,
    LLMToolChoice,
    LLMToolChoiceMode,
    LLMToolDefinition,
)
from app.services.prompt_builder import PromptBuildResult, PromptBuilderService


class RecordingPromptBuilder(PromptBuilderService):
    def __init__(self, result: PromptBuildResult) -> None:
        super().__init__()
        self.result = result
        self.calls = []

    def build(self, request):  # type: ignore[override]
        self.calls.append(deepcopy(request))
        return deepcopy(self.result)


class RecordingLLMIntegrationService:
    def __init__(self, response: LLMGenerationResponse) -> None:
        self.response = response
        self.calls = []

    def generate(self, request, *, provider_name=None):
        self.calls.append(
            {
                "request": deepcopy(request),
                "provider_name": provider_name,
            }
        )
        return deepcopy(self.response)


def _make_document() -> KnowledgeDocument:
    return KnowledgeDocument(
        id="clinic-hours",
        title="Clinic Hours",
        category="hours",
        source_type=KnowledgeDocumentSourceType.MARKDOWN,
        source_path="knowledge/clinic-hours.md",
        domain=KnowledgeDocumentDomain.FAQ,
        audience=KnowledgeDocumentAudience.PATIENT,
        status=KnowledgeDocumentStatus.ACTIVE,
        version="1.0.0",
        summary="Weekday consultation hours.",
        content="The clinic is open from 9 AM to 5 PM.",
    )


def _make_prompt_result() -> PromptBuildResult:
    return PromptBuildResult(
        prompt="[System Instructions]\n- Stay accurate.\n\n[User Message]\nWhen is the clinic open?",
        included_document_ids=["clinic-hours"],
        excluded_document_ids=["parking"],
        truncated=False,
        requires_domain_validation=False,
    )


def _make_llm_response() -> LLMGenerationResponse:
    return LLMGenerationResponse(
        message=LLMMessage(
            role=LLMMessageRole.ASSISTANT,
            content="The clinic is open from 9 AM to 5 PM on weekdays.",
        ),
        finish_reason=LLMFinishReason.STOP,
        provider_name="stub-provider",
        model_name="stub-model",
        usage=LLMTokenUsage(input_tokens=11, output_tokens=14, total_tokens=25),
        structured_output={"answer": "weekday hours"},
        tool_calls=[
            LLMToolCall(
                call_id="tool-1",
                tool_name="lookup_hours",
                arguments={"day": "weekday"},
            )
        ],
        reasoning=LLMReasoningResult(
            effort=LLMReasoningEffort.LOW,
            summary="Used retrieved scheduling context.",
        ),
        streaming=LLMStreamingMetadata(enabled=False),
        citations=[LLMCitation(citation_id="doc-1", label="Clinic Hours")],
        provider_metadata={"request_id": "req-123"},
        model_metadata={"family": "stub"},
        metadata={"normalized": True},
    )


def test_orchestrator_delegates_in_order_and_normalizes_result():
    prompt_builder = RecordingPromptBuilder(_make_prompt_result())
    llm_service = RecordingLLMIntegrationService(_make_llm_response())
    orchestrator = LLMGenerationOrchestrator(
        prompt_builder=prompt_builder,
        llm_integration_service=llm_service,
    )

    result = orchestrator.generate(
        LLMGenerationOrchestrationRequest(
            user_message="When is the clinic open?",
            conversation_state={"session_id": "abc"},
            documents=[_make_document()],
            active_intent="FAQ",
            system_instructions=["Stay accurate."],
            provider_name="stub-provider",
            model_name="stub-model",
            constraints=LLMGenerationConstraints(
                max_output_tokens=128,
                temperature=0.2,
            ),
            structured_output=LLMStructuredOutputSchema(
                mode=LLMStructuredOutputMode.JSON_OBJECT,
            ),
            tools=[
                LLMToolDefinition(
                    name="lookup_hours",
                    description="Fetch clinic hours.",
                )
            ],
            tool_choice=LLMToolChoice(mode=LLMToolChoiceMode.AUTO),
            reasoning=LLMReasoningConfig(effort=LLMReasoningEffort.LOW),
            metadata={"request_id": "orchestrator-1"},
        )
    )

    assert len(prompt_builder.calls) == 1
    assert len(llm_service.calls) == 1
    assert prompt_builder.calls[0].user_message == "When is the clinic open?"

    llm_call = llm_service.calls[0]
    llm_request = llm_call["request"]
    assert llm_call["provider_name"] == "stub-provider"
    assert llm_request.prompt == prompt_builder.result.prompt
    assert llm_request.messages == [
        LLMMessage(
            role=LLMMessageRole.USER,
            content=prompt_builder.result.prompt,
            metadata={"source": "prompt_builder", "block_count": 0},
        )
    ]
    assert llm_request.model_name == "stub-model"
    assert llm_request.constraints.max_output_tokens == 128
    assert llm_request.structured_output is not None
    assert llm_request.tools[0].name == "lookup_hours"
    assert llm_request.reasoning is not None
    assert llm_request.metadata["request_id"] == "orchestrator-1"
    assert llm_request.metadata["orchestration"] == {
        "included_document_ids": ["clinic-hours"],
        "excluded_document_ids": ["parking"],
        "truncated": False,
        "requires_domain_validation": False,
        "block_count": 0,
    }

    assert isinstance(result, LLMGenerationOrchestrationResult)
    assert result.prompt == prompt_builder.result.prompt
    assert result.response_message.content == (
        "The clinic is open from 9 AM to 5 PM on weekdays."
    )
    assert result.provider_name == "stub-provider"
    assert result.model_name == "stub-model"
    assert result.structured_output == {"answer": "weekday hours"}
    assert result.tool_calls[0].tool_name == "lookup_hours"
    assert result.reasoning is not None
    assert result.reasoning.summary == "Used retrieved scheduling context."
    assert result.citations[0].label == "Clinic Hours"


def test_orchestrator_build_llm_request_is_deterministic_for_equal_inputs():
    prompt_result = _make_prompt_result()
    orchestrator = LLMGenerationOrchestrator(
        prompt_builder=RecordingPromptBuilder(prompt_result),
        llm_integration_service=RecordingLLMIntegrationService(_make_llm_response()),
    )
    request = LLMGenerationOrchestrationRequest(
        user_message="When is the clinic open?",
        documents=[_make_document()],
        metadata={"request_id": "orchestrator-1"},
    )

    llm_request_a = orchestrator.build_llm_request(request, prompt_result=prompt_result)
    llm_request_b = orchestrator.build_llm_request(request, prompt_result=prompt_result)

    assert llm_request_a.model_dump(mode="json") == llm_request_b.model_dump(mode="json")


def test_orchestrator_requires_explicit_dependencies_and_stays_inactive_with_empty_registry():
    orchestrator = LLMGenerationOrchestrator(
        prompt_builder=PromptBuilderService(),
        llm_integration_service=LLMIntegrationService(
            provider_registry=InMemoryLLMProviderRegistry()
        ),
    )

    try:
        orchestrator.generate(
            LLMGenerationOrchestrationRequest(user_message="Hello")
        )
    except RuntimeError as exc:
        assert "inactive" in str(exc)
    else:
        raise AssertionError(
            "Expected explicitly composed orchestrator to remain inactive without a registered provider."
        )


def test_orchestrator_does_not_mutate_caller_input():
    prompt_builder = RecordingPromptBuilder(_make_prompt_result())
    llm_service = RecordingLLMIntegrationService(_make_llm_response())
    orchestrator = LLMGenerationOrchestrator(
        prompt_builder=prompt_builder,
        llm_integration_service=llm_service,
    )
    request = LLMGenerationOrchestrationRequest(
        user_message="When is the clinic open?",
        conversation_state={"history": [{"role": "user", "message": "Earlier question"}]},
        documents=[_make_document()],
        metadata={"request_id": "orchestrator-1"},
    )
    snapshot = request.model_dump(mode="python")

    orchestrator.generate(request)

    assert request.model_dump(mode="python") == snapshot
