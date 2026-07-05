from app.llm import (
    LLMFinishReason,
    LLMGenerationOrchestrationRequest,
    LLMGenerationOrchestrationResult,
    LLMMessage,
    LLMMessageRole,
    LLMRuntimeResponseValidationRequest,
    LLMRuntimeResponseValidationStatus,
    LLMRuntimeResponseValidator,
    LLMStructuredOutputMode,
    LLMStructuredOutputSchema,
)


def _valid_orchestration_request() -> LLMGenerationOrchestrationRequest:
    return LLMGenerationOrchestrationRequest(
        user_message="How do I book an appointment?",
        conversation_state={"conversation_id": "conv-1"},
        structured_output=LLMStructuredOutputSchema(mode=LLMStructuredOutputMode.JSON_OBJECT),
        metadata={"request_id": "validation-1"},
    )


def _valid_orchestration_result() -> LLMGenerationOrchestrationResult:
    return LLMGenerationOrchestrationResult(
        prompt="Rendered prompt",
        prompt_blocks=[],
        prompt_truncated=False,
        included_document_ids=[],
        excluded_document_ids=[],
        requires_domain_validation=False,
        response_message=LLMMessage(
            role=LLMMessageRole.ASSISTANT,
            content="Generated answer",
        ),
        finish_reason=LLMFinishReason.STOP,
        provider_name="openai",
        model_name="gpt-4.1-mini",
        structured_output={"answer": "Generated answer"},
        provider_metadata={"request_id": "provider-1"},
        model_metadata={"family": "gpt"},
        metadata={"validated": True},
    )


def test_runtime_response_validator_accepts_valid_runtime_response():
    validator = LLMRuntimeResponseValidator()
    request = LLMRuntimeResponseValidationRequest(
        request_id="validation-1",
        orchestration_request=_valid_orchestration_request(),
        orchestration_result=_valid_orchestration_result(),
    )

    result = validator.validate(request)

    assert result.status is LLMRuntimeResponseValidationStatus.VALID
    assert result.is_valid is True
    assert result.issues == []
    assert result.diagnostics["issue_count"] == 0
    assert result.diagnostics["response_content_length"] == len("Generated answer")


def test_runtime_response_validator_rejects_empty_response_content():
    validator = LLMRuntimeResponseValidator()
    response_message = LLMMessage.model_construct(
        role=LLMMessageRole.ASSISTANT,
        content="",
    )
    result_payload = LLMGenerationOrchestrationResult.model_construct(
        prompt="Rendered prompt",
        response_message=response_message,
        finish_reason=LLMFinishReason.STOP,
        structured_output={"answer": "Generated answer"},
        provider_metadata={},
        model_metadata={},
        metadata={},
    )
    request = LLMRuntimeResponseValidationRequest(
        request_id="validation-2",
        orchestration_request=_valid_orchestration_request(),
        orchestration_result=result_payload,
    )

    result = validator.validate(request)

    assert result.status is LLMRuntimeResponseValidationStatus.INVALID
    assert any(issue.code == "empty_runtime_response" for issue in result.issues)


def test_runtime_response_validator_rejects_whitespace_response_content():
    validator = LLMRuntimeResponseValidator()
    response_message = LLMMessage.model_construct(
        role=LLMMessageRole.ASSISTANT,
        content="   ",
    )
    result_payload = LLMGenerationOrchestrationResult.model_construct(
        prompt="Rendered prompt",
        response_message=response_message,
        finish_reason=LLMFinishReason.STOP,
        structured_output={"answer": "Generated answer"},
        provider_metadata={},
        model_metadata={},
        metadata={},
    )
    request = LLMRuntimeResponseValidationRequest(
        request_id="validation-3",
        orchestration_request=_valid_orchestration_request(),
        orchestration_result=result_payload,
    )

    result = validator.validate(request)

    assert result.is_valid is False
    assert any(issue.code == "whitespace_runtime_response" for issue in result.issues)


def test_runtime_response_validator_rejects_malformed_structured_output():
    validator = LLMRuntimeResponseValidator()
    result_payload = LLMGenerationOrchestrationResult.model_construct(
        prompt="Rendered prompt",
        response_message=LLMMessage.model_construct(
            role=LLMMessageRole.ASSISTANT,
            content="Generated answer",
        ),
        finish_reason=LLMFinishReason.STOP,
        structured_output="not-a-dict",
        provider_metadata={},
        model_metadata={},
        metadata={},
    )
    request = LLMRuntimeResponseValidationRequest(
        request_id="validation-4",
        orchestration_request=_valid_orchestration_request(),
        orchestration_result=result_payload,
    )

    result = validator.validate(request)

    assert any(issue.code == "malformed_structured_output" for issue in result.issues)


def test_runtime_response_validator_rejects_invalid_finish_reason():
    validator = LLMRuntimeResponseValidator()
    result_payload = LLMGenerationOrchestrationResult.model_construct(
        prompt="Rendered prompt",
        response_message=LLMMessage.model_construct(
            role=LLMMessageRole.ASSISTANT,
            content="Generated answer",
        ),
        finish_reason="unsupported",
        structured_output={"answer": "Generated answer"},
        provider_metadata={},
        model_metadata={},
        metadata={},
    )
    request = LLMRuntimeResponseValidationRequest(
        request_id="validation-5",
        orchestration_request=_valid_orchestration_request(),
        orchestration_result=result_payload,
    )

    result = validator.validate(request)

    assert any(issue.code == "invalid_finish_reason" for issue in result.issues)
    assert result.diagnostics["finish_reason"] == "unsupported"


def test_runtime_response_validator_reports_diagnostics_for_invalid_metadata():
    validator = LLMRuntimeResponseValidator()
    result_payload = LLMGenerationOrchestrationResult.model_construct(
        prompt="Rendered prompt",
        response_message=LLMMessage.model_construct(
            role=LLMMessageRole.ASSISTANT,
            content="Generated answer",
            metadata=["bad-metadata"],
        ),
        finish_reason=LLMFinishReason.STOP,
        structured_output={"answer": "Generated answer"},
        provider_metadata=["bad-provider-metadata"],
        model_metadata={},
        metadata={},
    )
    request = LLMRuntimeResponseValidationRequest(
        request_id="validation-6",
        orchestration_request=_valid_orchestration_request(),
        orchestration_result=result_payload,
        metadata={"request_id": "validation-6"},
    )

    result = validator.validate(request)

    assert result.is_valid is False
    assert result.diagnostics["issue_count"] >= 1
    assert result.diagnostics["response_message_role"] == "assistant"
    assert any(issue.code == "invalid_canonical_metadata" for issue in result.issues)
    assert any(issue.path == "provider_metadata" for issue in result.issues)
