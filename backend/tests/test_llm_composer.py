from app.llm import (
    AIExecutionMode,
    LLMFinishReason,
    LLMMessage,
    LLMMessageRole,
    LLMRuntimeResponse,
    LLMRuntimeResponseComposer,
    LLMRuntimeResponseComposerRequest,
    LLMRuntimeResponseCompositionStatus,
    LLMRuntimeResponseEligibilityResult,
    LLMRuntimeResponseEligibilityStatus,
    LLMRuntimeResponseValidationResult,
    LLMRuntimeResponseValidationStatus,
)
from app.llm.orchestrator import LLMGenerationOrchestrationResult


def _validation_result(*, is_valid: bool = True) -> LLMRuntimeResponseValidationResult:
    return LLMRuntimeResponseValidationResult(
        request_id="req-validation",
        status=(
            LLMRuntimeResponseValidationStatus.VALID
            if is_valid
            else LLMRuntimeResponseValidationStatus.INVALID
        ),
        is_valid=is_valid,
        issues=[],
        diagnostics={"validation_is_valid": is_valid},
    )


def _eligibility_result(*, is_eligible: bool = True) -> LLMRuntimeResponseEligibilityResult:
    return LLMRuntimeResponseEligibilityResult(
        request_id="req-eligibility",
        status=(
            LLMRuntimeResponseEligibilityStatus.ELIGIBLE
            if is_eligible
            else LLMRuntimeResponseEligibilityStatus.INELIGIBLE
        ),
        is_eligible=is_eligible,
        eligibility_reason=(
            "The validated runtime response is approved for user visibility."
            if is_eligible
            else "The validated runtime response is not approved for user visibility."
        ),
        fallback_reason=(
            None
            if is_eligible
            else "Runtime response eligibility preserved the deterministic reply."
        ),
        issues=[],
        diagnostics={"eligibility_is_eligible": is_eligible},
    )


def _llm_result() -> LLMGenerationOrchestrationResult:
    return LLMGenerationOrchestrationResult(
        prompt="Rendered prompt",
        response_message=LLMMessage(
            role=LLMMessageRole.ASSISTANT,
            content="Please arrive 15 minutes early and bring your ID.",
        ),
        finish_reason=LLMFinishReason.STOP,
        provider_name="openai",
        model_name="gpt-4.1-mini",
        structured_output={"tip": "Bring your ID."},
        provider_metadata={"provider": "openai"},
        model_metadata={"model": "gpt-4.1-mini"},
        metadata={"runtime": "llm"},
    )


def test_runtime_response_composer_returns_deterministic_only_response():
    composer = LLMRuntimeResponseComposer()
    deterministic_response = LLMRuntimeResponse(
        message="Your appointment is confirmed for July 10 at 9:30 AM.",
        data={
            "booking_id": "BK-1001",
            "appointment_id": 17,
            "doctor_name": "Dr. Patel",
        },
        metadata={"source": "workflow"},
    )

    result = composer.compose(
        LLMRuntimeResponseComposerRequest(
            request_id="compose-1",
            composition_mode=AIExecutionMode.DETERMINISTIC_ONLY,
            deterministic_response=deterministic_response,
        )
    )

    assert result.status is LLMRuntimeResponseCompositionStatus.COMPOSED
    assert result.augmentation_applied is False
    assert result.final_response.message == deterministic_response.message
    assert result.final_response.data == deterministic_response.data
    assert result.preserved_business_fields == [
        "appointment_id",
        "booking_id",
        "doctor_name",
    ]
    assert result.final_response.metadata["runtime_response_composition"][
        "composition_mode"
    ] == "DETERMINISTIC_ONLY"


def test_runtime_response_composer_returns_llm_only_response():
    composer = LLMRuntimeResponseComposer()

    result = composer.compose(
        LLMRuntimeResponseComposerRequest(
            request_id="compose-2",
            composition_mode=AIExecutionMode.LLM_ONLY,
            deterministic_response=LLMRuntimeResponse(
                message="This should be ignored.",
                data={"booking_id": "BK-ignored"},
            ),
            validation_result=_validation_result(),
            eligibility_result=_eligibility_result(),
            orchestration_result=_llm_result(),
        )
    )

    assert result.status is LLMRuntimeResponseCompositionStatus.COMPOSED
    assert result.augmentation_applied is False
    assert result.final_response.message == "Please arrive 15 minutes early and bring your ID."
    assert result.final_response.data == {"tip": "Bring your ID."}
    assert result.final_response.metadata["provider_name"] == "openai"


def test_runtime_response_composer_returns_hybrid_response():
    composer = LLMRuntimeResponseComposer()
    deterministic_response = LLMRuntimeResponse(
        message="Your appointment is confirmed for July 10 at 9:30 AM.",
        data={
            "booking_id": "BK-1002",
            "appointment_id": 23,
            "doctor_name": "Dr. Mehta",
            "appointment_date": "2026-07-10",
            "start_time": "09:30",
            "consultation_fee": 500,
        },
        metadata={"source": "workflow"},
    )

    result = composer.compose(
        LLMRuntimeResponseComposerRequest(
            request_id="compose-3",
            composition_mode=AIExecutionMode.HYBRID,
            deterministic_response=deterministic_response,
            validation_result=_validation_result(),
            eligibility_result=_eligibility_result(),
            orchestration_result=_llm_result(),
        )
    )

    assert result.status is LLMRuntimeResponseCompositionStatus.COMPOSED
    assert result.augmentation_applied is True
    assert result.final_response.message.startswith(
        "Your appointment is confirmed for July 10 at 9:30 AM."
    )
    assert "Additional guidance:" in result.final_response.message
    assert result.final_response.message.endswith(
        "Please arrive 15 minutes early and bring your ID."
    )
    assert result.final_response.data == deterministic_response.data
    assert result.preserved_business_fields == sorted(deterministic_response.data.keys())
    assert result.final_response.metadata["runtime_response_composition"][
        "augmentation_applied"
    ] is True


def test_runtime_response_composer_preserves_business_fields_when_llm_is_not_usable():
    composer = LLMRuntimeResponseComposer()
    deterministic_response = LLMRuntimeResponse(
        message="Your appointment is confirmed for July 10 at 9:30 AM.",
        data={
            "booking_id": "BK-1003",
            "appointment_id": 31,
            "doctor_name": "Dr. Rao",
        },
    )

    result = composer.compose(
        LLMRuntimeResponseComposerRequest(
            request_id="compose-4",
            composition_mode=AIExecutionMode.HYBRID,
            deterministic_response=deterministic_response,
            validation_result=_validation_result(is_valid=False),
            eligibility_result=_eligibility_result(),
            orchestration_result=_llm_result(),
        )
    )

    assert result.status is LLMRuntimeResponseCompositionStatus.FALLBACK
    assert result.augmentation_applied is False
    assert result.final_response.message == deterministic_response.message
    assert result.final_response.data == deterministic_response.data
    assert result.fallback_reason is not None


def test_runtime_response_composer_serializes_deterministically():
    composer = LLMRuntimeResponseComposer()

    first = composer.compose(
        LLMRuntimeResponseComposerRequest(
            request_id="compose-5",
            composition_mode=AIExecutionMode.HYBRID,
            deterministic_response=LLMRuntimeResponse(
                message="Your appointment is confirmed.",
                data={"booking_id": "BK-1004"},
            ),
            validation_result=_validation_result(),
            eligibility_result=_eligibility_result(),
            orchestration_result=_llm_result(),
        )
    ).model_dump(mode="json")
    second = composer.compose(
        LLMRuntimeResponseComposerRequest(
            request_id="compose-5",
            composition_mode=AIExecutionMode.HYBRID,
            deterministic_response=LLMRuntimeResponse(
                message="Your appointment is confirmed.",
                data={"booking_id": "BK-1004"},
            ),
            validation_result=_validation_result(),
            eligibility_result=_eligibility_result(),
            orchestration_result=_llm_result(),
        )
    ).model_dump(mode="json")

    assert first == second
