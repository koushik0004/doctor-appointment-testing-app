from app.llm import (
    LLMCitation,
    LLMFinishReason,
    LLMGenerationBudget,
    LLMGenerationBudgetQualityPreference,
    LLMGenerationBudgetReasoningEffort,
    LLMGenerationRequest,
    LLMGenerationResponse,
    LLMGenerationProfileName,
    LLMMessage,
    LLMMessageRole,
    LLMProviderCapabilities,
    LLMReasoningConfig,
    LLMReasoningEffort,
    LLMReasoningResult,
    LLMRequestedModality,
    LLMStreamingMetadata,
    LLMStreamingOptions,
    LLMStructuredOutputMode,
    LLMStructuredOutputSchema,
    LLMToolCall,
    LLMToolChoice,
    LLMToolChoiceMode,
    LLMToolDefinition,
)


def test_canonical_request_supports_future_provider_neutral_generation_controls():
    request = LLMGenerationRequest(
        system_prompt="Follow clinic policy.",
        model_name="canonical-model",
        messages=[
            LLMMessage(role=LLMMessageRole.USER, content="Summarize the visit."),
        ],
        requested_modalities=[LLMRequestedModality.TEXT],
        structured_output=LLMStructuredOutputSchema(
            mode=LLMStructuredOutputMode.JSON_SCHEMA,
            name="visit_summary",
            schema={
                "type": "object",
                "properties": {"summary": {"type": "string"}},
                "required": ["summary"],
            },
            strict=True,
        ),
        tools=[
            LLMToolDefinition(
                name="lookup_doctor_profile",
                description="Retrieve a doctor profile by id.",
                input_schema={
                    "type": "object",
                    "properties": {"doctor_id": {"type": "integer"}},
                    "required": ["doctor_id"],
                },
            )
        ],
        tool_choice=LLMToolChoice(
            mode=LLMToolChoiceMode.NAMED,
            tool_name="lookup_doctor_profile",
        ),
        reasoning=LLMReasoningConfig(
            effort=LLMReasoningEffort.MEDIUM,
            include_summary=True,
        ),
        generation_budget=LLMGenerationBudget(
            profile=LLMGenerationProfileName.BALANCED,
            reasoning_effort=LLMGenerationBudgetReasoningEffort.MEDIUM,
            max_output_tokens=1024,
            max_context_tokens=24000,
            quality_preference=LLMGenerationBudgetQualityPreference.HIGH,
        ),
        streaming=LLMStreamingOptions(enabled=True, include_usage=True),
    )

    dumped = request.model_dump(mode="json", exclude_none=True)

    assert dumped["model_name"] == "canonical-model"
    assert dumped["structured_output"]["mode"] == "json_schema"
    assert dumped["tools"][0]["name"] == "lookup_doctor_profile"
    assert dumped["tool_choice"]["mode"] == "named"
    assert dumped["reasoning"]["effort"] == "medium"
    assert dumped["generation_budget"]["profile"] == "balanced"
    assert dumped["streaming"]["enabled"] is True


def test_canonical_response_supports_future_provider_neutral_result_metadata():
    response = LLMGenerationResponse(
        message=LLMMessage(
            role=LLMMessageRole.ASSISTANT,
            content="Here is the visit summary.",
        ),
        finish_reason=LLMFinishReason.TOOL_CALL,
        structured_output={"summary": "Stable and ready for discharge."},
        tool_calls=[
            LLMToolCall(
                call_id="call-1",
                tool_name="lookup_doctor_profile",
                arguments={"doctor_id": 3},
            )
        ],
        reasoning=LLMReasoningResult(
            effort=LLMReasoningEffort.LOW,
            summary="Checked the requested doctor context before answering.",
        ),
        streaming=LLMStreamingMetadata(enabled=True, chunk_count=3),
        citations=[
            LLMCitation(
                citation_id="doc-1",
                label="Clinic policy",
                excerpt="Appointments require confirmation.",
                start_index=0,
                end_index=32,
            )
        ],
        provider_metadata={"request_id": "opaque"},
        model_metadata={"context_window": 128000},
    )

    dumped = response.model_dump(mode="json", exclude_none=True)

    assert dumped["finish_reason"] == "tool_call"
    assert dumped["tool_calls"][0]["tool_name"] == "lookup_doctor_profile"
    assert dumped["reasoning"]["summary"].startswith("Checked")
    assert dumped["streaming"]["chunk_count"] == 3
    assert dumped["citations"][0]["label"] == "Clinic policy"
    assert dumped["provider_metadata"]["request_id"] == "opaque"


def test_canonical_request_backward_compatibility_defaults_remain_minimal():
    request = LLMGenerationRequest(
        messages=[LLMMessage(role=LLMMessageRole.USER, content="Hello")]
    )

    assert request.model_name is None
    assert request.requested_modalities == []
    assert request.structured_output is None
    assert request.tools == []
    assert request.tool_choice is None
    assert request.reasoning is None
    assert request.generation_budget is None
    assert request.streaming.enabled is False


def test_canonical_response_backward_compatibility_defaults_remain_minimal():
    response = LLMGenerationResponse(
        message=LLMMessage(role=LLMMessageRole.ASSISTANT, content="Hello")
    )

    assert response.structured_output is None
    assert response.tool_calls == []
    assert response.reasoning is None
    assert response.streaming is None
    assert response.citations == []
    assert response.provider_metadata == {}
    assert response.model_metadata == {}


def test_canonical_models_validate_optional_fields_without_provider_leakage():
    request = LLMGenerationRequest(
        messages=[
            LLMMessage(
                role=LLMMessageRole.TOOL,
                content="Tool completed successfully.",
                tool_call_id="call-123",
            )
        ],
        tools=[LLMToolDefinition(name="book_appointment")],
    )

    assert request.messages[0].tool_call_id == "call-123"
    assert request.tools[0].name == "book_appointment"


def test_canonical_model_serialization_is_deterministic_for_equal_inputs():
    request_a = LLMGenerationRequest(
        messages=[LLMMessage(role=LLMMessageRole.USER, content="Need help")],
        metadata={"phase": "6.3"},
    )
    request_b = LLMGenerationRequest(
        messages=[LLMMessage(role=LLMMessageRole.USER, content="Need help")],
        metadata={"phase": "6.3"},
    )

    assert request_a.model_dump(mode="json") == request_b.model_dump(mode="json")


def test_provider_capabilities_can_advertise_future_optional_features():
    capabilities = LLMProviderCapabilities(
        supports_json_output=True,
        supports_tool_calls=True,
        supports_streaming=True,
        supports_reasoning=True,
        supports_citations=True,
        supports_audio_input=True,
    )

    dumped = capabilities.model_dump(mode="json")

    assert dumped["supports_reasoning"] is True
    assert dumped["supports_citations"] is True
    assert dumped["supports_audio_input"] is True
