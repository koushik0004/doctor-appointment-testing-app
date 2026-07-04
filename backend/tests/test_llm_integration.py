from app.llm import (
    LLMFinishReason,
    LLMGenerationRequest,
    LLMGenerationResponse,
    LLMIntegrationService,
    LLMMessage,
    LLMMessageRole,
    LLMProviderCapabilities,
    LLMProviderDescriptor,
)


class StubProvider:
    def __init__(self, name: str = "stub-provider") -> None:
        self._descriptor = LLMProviderDescriptor(
            provider_name=name,
            default_model_name="stub-model",
            capabilities=LLMProviderCapabilities(
                supports_system_prompt=True,
                supports_message_history=True,
                supports_streaming=False,
                supports_json_output=True,
            ),
        )

    def describe(self) -> LLMProviderDescriptor:
        return self._descriptor

    def generate(self, request: LLMGenerationRequest) -> LLMGenerationResponse:
        return LLMGenerationResponse(
            message=LLMMessage(
                role=LLMMessageRole.ASSISTANT,
                content=f"Echo: {request.messages[-1].content}",
            ),
            finish_reason=LLMFinishReason.STOP,
            provider_name=self._descriptor.provider_name,
            model_name=self._descriptor.default_model_name,
        )


class StubRegistry:
    def __init__(self, providers: list[StubProvider]) -> None:
        self._providers = {provider.describe().provider_name: provider for provider in providers}

    def list_providers(self) -> list[LLMProviderDescriptor]:
        return [
            provider.describe()
            for provider in self._providers.values()
        ]

    def get_provider(self, provider_name: str) -> StubProvider | None:
        return self._providers.get(provider_name)


def test_llm_integration_service_reports_inactive_status_without_registry():
    service = LLMIntegrationService()

    status = service.get_status()

    assert status.enabled is False
    assert status.connected_provider_names == []
    assert status.default_provider_name is None


def test_llm_integration_service_lists_registered_providers_without_runtime_wiring():
    service = LLMIntegrationService(
        provider_registry=StubRegistry([StubProvider("alpha"), StubProvider("beta")]),
        default_provider_name="alpha",
    )

    status = service.get_status()
    providers = service.list_registered_providers()

    assert status.enabled is False
    assert status.connected_provider_names == ["alpha", "beta"]
    assert providers[0].provider_name == "alpha"
    assert providers[1].provider_name == "beta"


def test_llm_integration_service_delegates_to_registered_provider_when_explicitly_used():
    service = LLMIntegrationService(
        provider_registry=StubRegistry([StubProvider("alpha")]),
        default_provider_name="alpha",
    )

    response = service.generate(
        LLMGenerationRequest(
            messages=[LLMMessage(role=LLMMessageRole.USER, content="Summarize this.")]
        )
    )

    assert response.provider_name == "alpha"
    assert response.model_name == "stub-model"
    assert response.message.role == LLMMessageRole.ASSISTANT
    assert response.message.content == "Echo: Summarize this."


def test_llm_integration_service_rejects_generate_without_registry():
    service = LLMIntegrationService()

    try:
        service.generate(
            LLMGenerationRequest(
                messages=[LLMMessage(role=LLMMessageRole.USER, content="Hello")]
            )
        )
    except RuntimeError as exc:
        assert "inactive" in str(exc)
    else:
        raise AssertionError("Expected RuntimeError when no provider registry is configured.")
