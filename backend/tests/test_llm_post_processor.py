from app.llm import (
    AIExecutionMode,
    LLMRuntimeResponse,
    LLMRuntimeResponseComposerResult,
    LLMRuntimeResponseCompositionStatus,
    LLMRuntimeResponsePostProcessor,
    LLMRuntimeResponsePostProcessingRequest,
    LLMRuntimeResponsePostProcessingStatus,
)


def _composition_result(
    *,
    mode: AIExecutionMode = AIExecutionMode.HYBRID,
    message: str = "Your appointment is confirmed.",
    data: dict[str, object] | None = None,
    metadata: dict[str, object] | None = None,
) -> LLMRuntimeResponseComposerResult:
    return LLMRuntimeResponseComposerResult(
        request_id="compose-post-1",
        correlation_id="corr-post-1",
        composition_mode=mode,
        status=LLMRuntimeResponseCompositionStatus.COMPOSED,
        final_response=LLMRuntimeResponse(
            message=message,
            data=data or {},
            metadata=metadata or {},
        ),
        deterministic_response=LLMRuntimeResponse(
            message="Your appointment is confirmed.",
            data={"booking_id": "BK-1", "appointment_id": 101},
            metadata={"source": "workflow"},
        ),
        llm_response=LLMRuntimeResponse(
            message="Please arrive early.",
            metadata={"provider_name": "openai"},
        ),
        augmentation_applied=mode is AIExecutionMode.HYBRID,
        preserved_business_fields=["appointment_id", "booking_id"],
        diagnostics={"composition_mode": mode.value},
    )


def test_runtime_response_post_processor_normalizes_whitespace_and_line_breaks():
    processor = LLMRuntimeResponsePostProcessor()

    result = processor.process(
        LLMRuntimeResponsePostProcessingRequest(
            request_id="post-1",
            final_response=LLMRuntimeResponse(
                message="  Hello there. \r\n\r\nPlease wait.  ",
                data={"booking_id": "BK-1001"},
                metadata={"source": "workflow"},
            ),
            composition_result=_composition_result(
                message="  Hello there. \r\n\r\nPlease wait.  ",
            ),
        )
    )

    assert result.status is LLMRuntimeResponsePostProcessingStatus.PROCESSED
    assert result.message_changed is True
    assert result.final_response.message == "Hello there.\n\nPlease wait."
    assert result.final_response.data == {"booking_id": "BK-1001"}
    assert result.diagnostics["trailing_spaces_removed"] > 0


def test_runtime_response_post_processor_removes_duplicate_blank_lines():
    processor = LLMRuntimeResponsePostProcessor()

    result = processor.process(
        LLMRuntimeResponsePostProcessingRequest(
            request_id="post-2",
            final_response=LLMRuntimeResponse(
                message="Line one\n\n\nLine two\n\n\n\nLine three",
                data={"booking_id": "BK-1002"},
            ),
            composition_result=_composition_result(
                message="Line one\n\n\nLine two\n\n\n\nLine three",
            ),
        )
    )

    assert result.final_response.message == "Line one\n\nLine two\n\nLine three"
    assert result.diagnostics["duplicate_blank_lines_removed"] == 3


def test_runtime_response_post_processor_normalizes_markdown_presentation():
    processor = LLMRuntimeResponsePostProcessor()

    result = processor.process(
        LLMRuntimeResponsePostProcessingRequest(
            request_id="post-3",
            final_response=LLMRuntimeResponse(
                message="#Heading\n-   item one\n1.    item two\n>   quoted",
                data={"booking_id": "BK-1003"},
            ),
            composition_result=_composition_result(
                message="#Heading\n-   item one\n1.    item two\n>   quoted",
            ),
        )
    )

    assert result.final_response.message == "# Heading\n- item one\n1. item two\n> quoted"
    assert result.diagnostics["heading_markdown_normalized"] is True
    assert result.diagnostics["bullet_markdown_normalized"] is True
    assert result.diagnostics["ordered_list_markdown_normalized"] is True
    assert result.diagnostics["blockquote_markdown_normalized"] is True


def test_runtime_response_post_processor_sanitizes_presentation_metadata():
    processor = LLMRuntimeResponsePostProcessor()

    result = processor.process(
        LLMRuntimeResponsePostProcessingRequest(
            request_id="post-4",
            final_response=LLMRuntimeResponse(
                message="Confirmed.",
                data={"booking_id": "BK-1004", "appointment_id": 303},
                metadata={
                    "runtime_response_composition": {"mode": "HYBRID"},
                    "presentation_metadata": {"ui": "card"},
                    "ui_metadata": {"theme": "warm"},
                    "preserved_business_fields": ["booking_id", "appointment_id"],
                },
            ),
            composition_result=_composition_result(
                metadata={
                    "runtime_response_composition": {"mode": "HYBRID"},
                    "presentation_metadata": {"ui": "card"},
                    "ui_metadata": {"theme": "warm"},
                }
            ),
        )
    )

    assert "presentation_metadata" not in result.final_response.metadata
    assert "ui_metadata" not in result.final_response.metadata
    assert result.final_response.metadata["runtime_response_composition"] == {
        "mode": "HYBRID"
    }
    assert result.removed_metadata_keys == [
        "presentation_metadata",
        "ui_metadata",
    ]
    assert result.sanitized_presentation_metadata == {
        "presentation_metadata": {"ui": "card"},
        "ui_metadata": {"theme": "warm"},
    }


def test_runtime_response_post_processor_preserves_deterministic_business_data():
    processor = LLMRuntimeResponsePostProcessor()

    result = processor.process(
        LLMRuntimeResponsePostProcessingRequest(
            request_id="post-5",
            final_response=LLMRuntimeResponse(
                message="Your appointment is confirmed for July 10 at 9:30 AM.",
                data={
                    "booking_id": "BK-1005",
                    "appointment_id": 404,
                    "doctor_name": "Dr. Rao",
                    "consultation_fee": 500,
                },
                metadata={"source": "workflow"},
            ),
            composition_result=_composition_result(
                message="Your appointment is confirmed for July 10 at 9:30 AM.",
                data={
                    "booking_id": "BK-1005",
                    "appointment_id": 404,
                    "doctor_name": "Dr. Rao",
                    "consultation_fee": 500,
                },
            ),
        )
    )

    assert result.final_response.data == {
        "booking_id": "BK-1005",
        "appointment_id": 404,
        "doctor_name": "Dr. Rao",
        "consultation_fee": 500,
    }
    assert result.final_response.metadata["runtime_response_post_processing"][
        "removed_metadata_keys"
    ] == []


def test_runtime_response_post_processor_supports_deterministic_llm_and_hybrid_modes():
    processor = LLMRuntimeResponsePostProcessor()

    deterministic = processor.process(
        LLMRuntimeResponsePostProcessingRequest(
            request_id="post-6-det",
            final_response=LLMRuntimeResponse(
                message=" Confirmed. ",
                data={"booking_id": "BK-1006"},
            ),
            composition_result=_composition_result(
                mode=AIExecutionMode.DETERMINISTIC_ONLY,
                message=" Confirmed. ",
                data={"booking_id": "BK-1006"},
            ),
        )
    )
    llm_only = processor.process(
        LLMRuntimeResponsePostProcessingRequest(
            request_id="post-6-llm",
            final_response=LLMRuntimeResponse(
                message="  Please arrive early.  ",
                data={"tip": "Bring ID."},
            ),
            composition_result=_composition_result(
                mode=AIExecutionMode.LLM_ONLY,
                message="  Please arrive early.  ",
                data={"tip": "Bring ID."},
            ),
        )
    )
    hybrid = processor.process(
        LLMRuntimeResponsePostProcessingRequest(
            request_id="post-6-hybrid",
            final_response=LLMRuntimeResponse(
                message="Confirmed.\n\nAdditional guidance:\n##Heading",
                data={"booking_id": "BK-1006", "appointment_id": 505},
            ),
            composition_result=_composition_result(
                mode=AIExecutionMode.HYBRID,
                message="Confirmed.\n\nAdditional guidance:\n##Heading",
                data={"booking_id": "BK-1006", "appointment_id": 505},
            ),
        )
    )

    assert deterministic.final_response.message == "Confirmed."
    assert llm_only.final_response.message == "Please arrive early."
    assert hybrid.final_response.message == "Confirmed.\n\nAdditional guidance:\n## Heading"
    assert deterministic.diagnostics["composition_mode"] == "DETERMINISTIC_ONLY"
    assert llm_only.diagnostics["composition_mode"] == "LLM_ONLY"
    assert hybrid.diagnostics["composition_mode"] == "HYBRID"


def test_runtime_response_post_processor_serializes_deterministically():
    processor = LLMRuntimeResponsePostProcessor()

    first = processor.process(
        LLMRuntimeResponsePostProcessingRequest(
            request_id="post-7",
            correlation_id="corr-post-7",
            final_response=LLMRuntimeResponse(
                message="  Confirmed.  ",
                data={"booking_id": "BK-1007"},
                metadata={"presentation_metadata": {"ui": "card"}},
            ),
            composition_result=_composition_result(
                mode=AIExecutionMode.HYBRID,
                message="  Confirmed.  ",
                data={"booking_id": "BK-1007"},
                metadata={"presentation_metadata": {"ui": "card"}},
            ),
        )
    ).model_dump(mode="json")
    second = processor.process(
        LLMRuntimeResponsePostProcessingRequest(
            request_id="post-7",
            correlation_id="corr-post-7",
            final_response=LLMRuntimeResponse(
                message="  Confirmed.  ",
                data={"booking_id": "BK-1007"},
                metadata={"presentation_metadata": {"ui": "card"}},
            ),
            composition_result=_composition_result(
                mode=AIExecutionMode.HYBRID,
                message="  Confirmed.  ",
                data={"booking_id": "BK-1007"},
                metadata={"presentation_metadata": {"ui": "card"}},
            ),
        )
    ).model_dump(mode="json")

    assert first == second
