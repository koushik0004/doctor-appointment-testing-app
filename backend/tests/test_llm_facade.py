from app.llm import (
    AIExecutionOwner,
    AIExecutionMode,
    AIExecutionPolicyRequest,
    AIExecutionPolicyResult,
    LLMFinishReason,
    LLMControlledGenerationRequest,
    LLMControlledGenerationStatus,
    InlineLLMShadowExecutionRunner,
    LLMConfigurationSettings,
    LLMGenerationOrchestrationResult,
    LLMMessage,
    LLMMessageRole,
    LLMProviderName,
    LLMRuntimeCompositionRoot,
    LLMRuntimeFacade,
    LLMRuntimeFacadeSnapshot,
    LLMGenerationOrchestrationRequest,
    LLMRuntimeResponseEligibilityStatus,
    LLMRuntimeResponseValidationStatus,
    LLMShadowModeRequest,
    LLMShadowModeStatus,
)
from app.services.prompt_builder import PromptBuildRequest, PromptBuilderService


class RecordingPromptBuilder(PromptBuilderService):
    def __init__(self) -> None:
        super().__init__()
        self.calls: list[PromptBuildRequest] = []

    def build(self, request: PromptBuildRequest):  # type: ignore[override]
        self.calls.append(request.model_copy(deep=True))
        return super().build(request)


class StaticTransport:
    def __init__(self, response: dict[str, object]) -> None:
        self._response = dict(response)
        self.calls: list[dict[str, object]] = []

    def invoke(self, request: dict[str, object]) -> dict[str, object]:
        self.calls.append(request)
        return dict(self._response)


class FailingTransport:
    def invoke(self, request: dict[str, object]) -> dict[str, object]:
        del request
        raise RuntimeError("transport failure")


class StaticTransportFactory:
    def __init__(self, provider_transports: dict[str, object]) -> None:
        self._provider_transports = dict(provider_transports)

    def create_transports(self, configuration) -> dict[str, object]:
        del configuration
        return dict(self._provider_transports)


def _base_settings(
    *,
    shadow_mode: bool = False,
    allow_generation: bool = True,
) -> LLMConfigurationSettings:
    return LLMConfigurationSettings(
        provider=LLMProviderName.OPENAI,
        enabled=True,
        allow_generation=allow_generation,
        shadow_mode=shadow_mode,
        openai={
            "enabled": True,
            "default_model_name": "gpt-4.1-mini",
            "api_key": "openai-key",
        },
        claude={
            "enabled": False,
        },
    )


def test_runtime_facade_caches_composition_and_exposes_a_save_ready_snapshot():
    root = LLMRuntimeCompositionRoot(
        prompt_builder=PromptBuilderService(),
        configuration_settings=_base_settings(),
        transport_factory=StaticTransportFactory(
            {
                "openai": StaticTransport(
                    {
                        "content": "shadow",
                        "finish_reason": "stop",
                        "model": "gpt-4.1-mini",
                    }
                )
            }
        ),
    )
    facade = LLMRuntimeFacade(composition_root=root)

    first = facade.compose()
    second = facade.get_composition()
    snapshot = facade.save_integration_boundary()

    assert first is second
    assert isinstance(snapshot, LLMRuntimeFacadeSnapshot)
    assert snapshot.configuration_loaded is True
    assert snapshot.composition_cached is True
    assert snapshot.connected_provider_names == ["openai"]
    assert snapshot.default_provider_name == "openai"
    assert snapshot.selected_provider_name == "openai"
    assert snapshot.activation_status.generation_available is True
    assert snapshot.integration_status.enabled is False
    assert snapshot.shadow_execution_count == 0
    assert snapshot.last_shadow_status is None


def test_runtime_facade_snapshot_serializes_deterministically():
    facade = LLMRuntimeFacade(
        composition_root=LLMRuntimeCompositionRoot(
            prompt_builder=PromptBuilderService(),
            configuration_settings=_base_settings(),
            transport_factory=StaticTransportFactory(
                {
                    "openai": StaticTransport(
                        {
                            "content": "shadow",
                            "finish_reason": "stop",
                            "model": "gpt-4.1-mini",
                        }
                    )
                }
            ),
        )
    )

    first = facade.snapshot().model_dump(mode="json")
    second = facade.save_integration_boundary().model_dump(mode="json")

    assert first == second


def test_runtime_facade_runs_controlled_generation_when_policy_and_activation_allow_it():
    transport = StaticTransport(
        {
            "content": "Generated runtime answer",
            "finish_reason": "stop",
            "model": "gpt-4.1-mini",
            "usage": {
                "prompt_tokens": 12,
                "completion_tokens": 7,
                "total_tokens": 19,
            },
        }
    )
    prompt_builder = RecordingPromptBuilder()
    facade = LLMRuntimeFacade(
        composition_root=LLMRuntimeCompositionRoot(
            prompt_builder=prompt_builder,
            configuration_settings=_base_settings(allow_generation=True),
            transport_factory=StaticTransportFactory({"openai": transport}),
        )
    )

    result = facade.run_controlled_generation(
        LLMControlledGenerationRequest(
            policy_request=AIExecutionPolicyRequest(
                preferred_mode=AIExecutionMode.HYBRID,
            ),
            orchestration_request=LLMGenerationOrchestrationRequest(
                user_message="What payment methods do you accept?",
                conversation_state={
                    "conversation_id": "conv-control-1",
                    "current_workflow": {
                        "workflow_type": "BOOK_APPOINTMENT",
                        "status": "INPUT_REQUIRED",
                        "draft": {"doctor_name": "Dr. Smith"},
                        "missing_fields": ["appointment_date"],
                    },
                },
                documents=[],
                active_intent="UNKNOWN",
                provider_name="openai",
                metadata={"request_id": "controlled-1"},
            ),
        )
    )

    assert result.status is LLMControlledGenerationStatus.SUCCEEDED
    assert result.generated_result is not None
    assert result.validation_result is not None
    assert result.validation_result.status is LLMRuntimeResponseValidationStatus.VALID
    assert result.eligibility_result is not None
    assert result.eligibility_result.status is LLMRuntimeResponseEligibilityStatus.ELIGIBLE
    assert result.generated_result.provider_name == "openai"
    assert result.generated_result.prompt is not None
    assert "[Workflow State]" in result.generated_result.prompt
    assert len(prompt_builder.calls) == 1
    assert len(transport.calls) == 1
    prompt_payload = transport.calls[0]["messages"][0]["content"]
    assert "[User Message]" in prompt_payload
    assert "[Conversation State]" in prompt_payload
    assert "[Workflow State]" in prompt_payload


def test_runtime_facade_skips_controlled_generation_when_generation_is_disabled():
    transport = StaticTransport(
        {
            "content": "Generated runtime answer",
            "finish_reason": "stop",
            "model": "gpt-4.1-mini",
        }
    )
    prompt_builder = RecordingPromptBuilder()
    facade = LLMRuntimeFacade(
        composition_root=LLMRuntimeCompositionRoot(
            prompt_builder=prompt_builder,
            configuration_settings=_base_settings(allow_generation=False),
            transport_factory=StaticTransportFactory({"openai": transport}),
        )
    )

    result = facade.run_controlled_generation(
        LLMControlledGenerationRequest(
            policy_request=AIExecutionPolicyRequest(
                preferred_mode=AIExecutionMode.HYBRID,
            ),
            orchestration_request=LLMGenerationOrchestrationRequest(
                user_message="What payment methods do you accept?",
                conversation_state={"conversation_id": "conv-control-2"},
                provider_name="openai",
            ),
        )
    )

    assert result.status is LLMControlledGenerationStatus.SKIPPED
    assert result.generated_result is None
    assert result.fallback_reason is not None
    assert len(prompt_builder.calls) == 0
    assert len(transport.calls) == 0


def test_runtime_facade_skips_controlled_generation_when_runtime_response_is_not_low_risk():
    transport = StaticTransport(
        {
            "content": "Generated runtime answer",
            "finish_reason": "stop",
            "model": "gpt-4.1-mini",
        }
    )
    prompt_builder = RecordingPromptBuilder()
    facade = LLMRuntimeFacade(
        composition_root=LLMRuntimeCompositionRoot(
            prompt_builder=prompt_builder,
            configuration_settings=_base_settings(allow_generation=True),
            transport_factory=StaticTransportFactory({"openai": transport}),
        )
    )
    composition = facade.compose()
    approved_decision = composition.execution_policy_service.evaluate(
        AIExecutionPolicyRequest(
            preferred_mode=AIExecutionMode.LLM_ONLY,
        )
    ).decision
    composition.execution_policy_service.evaluate = lambda request: AIExecutionPolicyResult(  # type: ignore[assignment]
        decision=approved_decision
    )
    facade.compose = lambda: composition  # type: ignore[assignment]

    result = facade.run_controlled_generation(
        LLMControlledGenerationRequest(
            policy_request=AIExecutionPolicyRequest(
                preferred_mode=AIExecutionMode.LLM_ONLY,
            ),
            orchestration_request=LLMGenerationOrchestrationRequest(
                user_message="Generate a runtime answer.",
                active_intent="BOOK_APPOINTMENT",
                provider_name="openai",
            ),
        )
    )

    assert result.status is LLMControlledGenerationStatus.SKIPPED
    assert result.generated_result is None
    assert result.validation_result is not None
    assert result.validation_result.is_valid is True
    assert result.eligibility_result is not None
    assert result.eligibility_result.is_eligible is False
    assert result.eligibility_result.status is LLMRuntimeResponseEligibilityStatus.INELIGIBLE
    assert any(
        issue.code == "non_eligible_intent"
        for issue in result.eligibility_result.issues
    )
    assert result.fallback_reason is not None
    assert len(prompt_builder.calls) == 1
    assert len(transport.calls) == 1


def test_runtime_facade_falls_back_when_controlled_generation_fails():
    facade = LLMRuntimeFacade(
        composition_root=LLMRuntimeCompositionRoot(
            prompt_builder=PromptBuilderService(),
            configuration_settings=_base_settings(allow_generation=True),
            transport_factory=StaticTransportFactory({"openai": FailingTransport()}),
        )
    )

    result = facade.run_controlled_generation(
        LLMControlledGenerationRequest(
            policy_request=AIExecutionPolicyRequest(
                preferred_mode=AIExecutionMode.LLM_ONLY,
            ),
            orchestration_request=LLMGenerationOrchestrationRequest(
                user_message="Generate a runtime answer.",
                provider_name="openai",
            ),
        )
    )

    assert result.status is LLMControlledGenerationStatus.FAILED
    assert result.generated_result is None
    assert result.error_message is not None
    assert result.error_type == "RuntimeError"


def test_runtime_facade_falls_back_when_controlled_generation_validation_fails():
    transport = StaticTransport(
        {
            "content": "Generated runtime answer",
            "finish_reason": "stop",
            "model": "gpt-4.1-mini",
        }
    )
    facade = LLMRuntimeFacade(
        composition_root=LLMRuntimeCompositionRoot(
            prompt_builder=PromptBuilderService(),
            configuration_settings=_base_settings(allow_generation=True),
            transport_factory=StaticTransportFactory({"openai": transport}),
        )
    )
    composition = facade.compose()
    invalid_result = LLMGenerationOrchestrationResult.model_construct(
        prompt="Rendered prompt",
        response_message=LLMMessage.model_construct(
            role=LLMMessageRole.ASSISTANT,
            content="   ",
        ),
        finish_reason=LLMFinishReason.STOP,
        provider_name="openai",
        model_name="gpt-4.1-mini",
        structured_output={"answer": "Generated runtime answer"},
        provider_metadata={},
        model_metadata={},
        metadata={},
    )
    composition.orchestrator.generate = lambda request: invalid_result  # type: ignore[assignment]
    facade.compose = lambda: composition  # type: ignore[assignment]

    result = facade.run_controlled_generation(
        LLMControlledGenerationRequest(
            policy_request=AIExecutionPolicyRequest(
                preferred_mode=AIExecutionMode.LLM_ONLY,
            ),
            orchestration_request=LLMGenerationOrchestrationRequest(
                user_message="Generate a runtime answer.",
                provider_name="openai",
            ),
        )
    )

    assert result.status is LLMControlledGenerationStatus.FAILED
    assert result.generated_result is None
    assert result.validation_result is not None
    assert result.validation_result.is_valid is False
    assert any(
        issue.code == "whitespace_runtime_response"
        for issue in result.validation_result.issues
    )
    assert result.eligibility_result is None
    assert result.fallback_reason is not None


def test_runtime_facade_keeps_deterministic_compatibility_for_non_llm_policies():
    transport = StaticTransport(
        {
            "content": "Generated runtime answer",
            "finish_reason": "stop",
            "model": "gpt-4.1-mini",
        }
    )
    prompt_builder = RecordingPromptBuilder()
    facade = LLMRuntimeFacade(
        composition_root=LLMRuntimeCompositionRoot(
            prompt_builder=prompt_builder,
            configuration_settings=_base_settings(allow_generation=True),
            transport_factory=StaticTransportFactory({"openai": transport}),
        )
    )

    result = facade.run_controlled_generation(
        LLMControlledGenerationRequest(
            policy_request=AIExecutionPolicyRequest(
                preferred_mode=AIExecutionMode.DETERMINISTIC_ONLY,
            ),
            orchestration_request=LLMGenerationOrchestrationRequest(
                user_message="Keep this deterministic.",
                provider_name="openai",
            ),
        )
    )

    assert result.status is LLMControlledGenerationStatus.SKIPPED
    assert result.generated_result is None
    assert len(prompt_builder.calls) == 0
    assert len(transport.calls) == 0


def test_runtime_facade_executes_shadow_mode_and_captures_diagnostics():
    transport = StaticTransport(
        {
            "content": "Hidden LLM answer",
            "finish_reason": "stop",
            "model": "gpt-4.1-mini",
            "usage": {
                "prompt_tokens": 14,
                "completion_tokens": 6,
                "total_tokens": 20,
            },
        }
    )
    facade = LLMRuntimeFacade(
        composition_root=LLMRuntimeCompositionRoot(
            prompt_builder=PromptBuilderService(),
            configuration_settings=_base_settings(shadow_mode=True),
            transport_factory=StaticTransportFactory({"openai": transport}),
        ),
        shadow_execution_runner=InlineLLMShadowExecutionRunner(),
    )

    dispatch = facade.run_shadow_mode(
        LLMShadowModeRequest(
            correlation_id="conv-1",
            user_message="What payment methods do you accept?",
            official_response_owner=AIExecutionOwner.DETERMINISTIC,
            official_intent_name="UNKNOWN",
            knowledge_eligible=True,
            knowledge_match_available=False,
            conversation_state={
                "conversation_id": "conv-1",
                "history": [{"role": "user", "text": "What payment methods do you accept?"}],
            },
        ),
        asynchronous=False,
    )

    assert dispatch.decision.should_execute_shadow is True
    assert dispatch.diagnostic is not None
    assert dispatch.diagnostic.status is LLMShadowModeStatus.SUCCEEDED
    assert dispatch.diagnostic.provider_name == "openai"
    assert dispatch.diagnostic.model_name == "gpt-4.1-mini"
    assert dispatch.diagnostic.token_accounting is not None
    assert dispatch.diagnostic.token_accounting.total_tokens == 20
    assert dispatch.diagnostic.observability.metadata["shadow_mode"] is True
    assert dispatch.diagnostic.audit_record.correlation_id == "conv-1"
    assert len(transport.calls) == 1
    assert facade.snapshot().shadow_execution_count == 1
    assert facade.snapshot().last_shadow_status == "SUCCEEDED"


def test_runtime_facade_shadow_mode_uses_rendered_prompt_builder_output():
    transport = StaticTransport(
        {
            "content": "Hidden LLM answer",
            "finish_reason": "stop",
            "model": "gpt-4.1-mini",
        }
    )
    prompt_builder = RecordingPromptBuilder()
    facade = LLMRuntimeFacade(
        composition_root=LLMRuntimeCompositionRoot(
            prompt_builder=prompt_builder,
            configuration_settings=_base_settings(shadow_mode=True),
            transport_factory=StaticTransportFactory({"openai": transport}),
        ),
        shadow_execution_runner=InlineLLMShadowExecutionRunner(),
    )

    dispatch = facade.run_shadow_mode(
        LLMShadowModeRequest(
            correlation_id="conv-7-3",
            user_message="Book an appointment with Dr. Smith tomorrow",
            official_response_owner=AIExecutionOwner.DETERMINISTIC,
            official_intent_name="UNKNOWN",
            has_active_workflow=False,
            conversation_state={
                "conversation_id": "conv-7-3",
                "context": {
                    "conversation_id": "conv-7-3",
                    "current_workflow": {
                        "workflow_type": "BOOK_APPOINTMENT",
                        "status": "INPUT_REQUIRED",
                        "draft": {"doctor_name": "Dr. Smith"},
                        "missing_fields": ["appointment_date", "patient_email"],
                    },
                },
                "history": [
                    {"role": "user", "text": "Book an appointment with Dr. Smith tomorrow"}
                ],
            },
        ),
        asynchronous=False,
    )

    assert dispatch.diagnostic is not None
    assert dispatch.diagnostic.status is LLMShadowModeStatus.SUCCEEDED
    assert len(prompt_builder.calls) == 1
    assert prompt_builder.calls[0].user_message == "Book an appointment with Dr. Smith tomorrow"
    assert len(transport.calls) == 1
    prompt_payload = transport.calls[0]["messages"][0]["content"]
    assert "[User Message]" in prompt_payload
    assert "[Conversation State]" in prompt_payload
    assert "[Workflow State]" in prompt_payload
    assert '"workflow_status":"INPUT_REQUIRED"' in prompt_payload
    assert '"missing_fields":["appointment_date","patient_email"]' in prompt_payload


def test_runtime_facade_skips_shadow_execution_when_shadow_mode_is_disabled():
    transport = StaticTransport(
        {
            "content": "Hidden LLM answer",
            "finish_reason": "stop",
            "model": "gpt-4.1-mini",
        }
    )
    facade = LLMRuntimeFacade(
        composition_root=LLMRuntimeCompositionRoot(
            prompt_builder=PromptBuilderService(),
            configuration_settings=_base_settings(shadow_mode=False),
            transport_factory=StaticTransportFactory({"openai": transport}),
        ),
        shadow_execution_runner=InlineLLMShadowExecutionRunner(),
    )

    dispatch = facade.run_shadow_mode(
        LLMShadowModeRequest(
            correlation_id="conv-2",
            user_message="Hello",
            official_response_owner=AIExecutionOwner.DETERMINISTIC,
            official_intent_name="UNKNOWN",
        ),
        asynchronous=False,
    )

    assert dispatch.decision.should_execute_shadow is False
    assert dispatch.diagnostic is not None
    assert dispatch.diagnostic.status is LLMShadowModeStatus.SKIPPED
    assert transport.calls == []


def test_runtime_facade_records_shadow_failures_without_raising():
    facade = LLMRuntimeFacade(
        composition_root=LLMRuntimeCompositionRoot(
            prompt_builder=PromptBuilderService(),
            configuration_settings=_base_settings(shadow_mode=True),
            transport_factory=StaticTransportFactory({"openai": FailingTransport()}),
        ),
        shadow_execution_runner=InlineLLMShadowExecutionRunner(),
    )

    dispatch = facade.run_shadow_mode(
        LLMShadowModeRequest(
            correlation_id="conv-3",
            user_message="Hello",
            official_response_owner=AIExecutionOwner.DETERMINISTIC,
            official_intent_name="UNKNOWN",
        ),
        asynchronous=False,
    )

    assert dispatch.decision.should_execute_shadow is True
    assert dispatch.diagnostic is not None
    assert dispatch.diagnostic.status is LLMShadowModeStatus.FAILED
    assert dispatch.diagnostic.error_message is not None
    assert facade.get_last_shadow_diagnostic() is not None
    assert facade.get_last_shadow_diagnostic().status is LLMShadowModeStatus.FAILED
