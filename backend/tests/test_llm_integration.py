from app.llm import (
    BaseLLMProviderAdapter,
    LLMFinishReason,
    LLMGenerationRequest,
    LLMGenerationResponse,
    LLMIntegrationService,
    LLMMessage,
    LLMMessageRole,
    LLMProviderCapabilities,
    LLMProviderDescriptor,
    InMemoryLLMProviderRegistry,
)


class StubProvider(BaseLLMProviderAdapter[dict[str, object], dict[str, object]]):
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

    def translate_request(
        self,
        request: LLMGenerationRequest,
    ) -> dict[str, object]:
        return {
            "messages": [message.content for message in request.messages],
            "system_prompt": request.system_prompt,
        }

    def invoke_provider(self, request: dict[str, object]) -> dict[str, object]:
        messages = request["messages"]
        return {"text": f"Echo: {messages[-1]}"}

    def translate_response(
        self,
        response: dict[str, object],
        *,
        request: LLMGenerationRequest,
    ) -> LLMGenerationResponse:
        return LLMGenerationResponse(
            message=LLMMessage(
                role=LLMMessageRole.ASSISTANT,
                content=str(response["text"]),
            ),
            finish_reason=LLMFinishReason.STOP,
        )


class StubRegistry:
    def __init__(
        self,
        providers: list[StubProvider],
        *,
        default_provider_name: str | None = None,
    ) -> None:
        self._providers = {
            provider.describe().provider_name: provider for provider in providers
        }
        self._default_provider_name = default_provider_name

    def list_providers(self) -> list[LLMProviderDescriptor]:
        return [provider.describe() for provider in self._providers.values()]

    def get_provider(self, provider_name: str) -> StubProvider | None:
        return self._providers.get(provider_name)

    def get_default_provider_name(self) -> str | None:
        return self._default_provider_name


def test_llm_integration_service_reports_inactive_status_without_registry():
    service = LLMIntegrationService()

    status = service.get_status()

    assert status.enabled is False
    assert status.connected_provider_names == []
    assert status.default_provider_name is None


def test_llm_integration_service_lists_registered_providers_without_runtime_wiring():
    service = LLMIntegrationService(
        provider_registry=StubRegistry(
            [StubProvider("alpha"), StubProvider("beta")],
            default_provider_name="alpha",
        ),
    )

    status = service.get_status()
    providers = service.list_registered_providers()

    assert status.enabled is False
    assert status.connected_provider_names == ["alpha", "beta"]
    assert providers[0].provider_name == "alpha"
    assert providers[1].provider_name == "beta"


def test_llm_integration_service_delegates_to_registered_provider_when_explicitly_used():
    service = LLMIntegrationService(
        provider_registry=StubRegistry(
            [StubProvider("alpha")],
            default_provider_name="alpha",
        ),
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
        raise AssertionError(
            "Expected RuntimeError when no provider registry is configured."
        )


def test_base_adapter_keeps_provider_specific_payloads_internal():
    provider = StubProvider("alpha")
    request = LLMGenerationRequest(
        system_prompt="Follow clinic policy.",
        messages=[LLMMessage(role=LLMMessageRole.USER, content="Hello")],
    )

    response = provider.generate(request)

    assert response.provider_name == "alpha"
    assert response.model_name == "stub-model"
    assert response.message.content == "Echo: Hello"


def test_in_memory_registry_exposes_explicit_default_provider_without_runtime_wiring():
    registry = InMemoryLLMProviderRegistry(
        [StubProvider("alpha"), StubProvider("beta")],
        default_provider_name="beta",
    )
    service = LLMIntegrationService(provider_registry=registry)

    status = service.get_status()
    response = service.generate(
        LLMGenerationRequest(
            messages=[LLMMessage(role=LLMMessageRole.USER, content="Status?")]
        )
    )

    assert status.default_provider_name == "beta"
    assert response.provider_name == "beta"


def test_in_memory_registry_rejects_duplicate_provider_names():
    registry = InMemoryLLMProviderRegistry()
    registry.register(StubProvider("alpha"))

    try:
        registry.register(StubProvider("alpha"))
    except ValueError as exc:
        assert "already registered" in str(exc)
    else:
        raise AssertionError("Expected duplicate provider registration to fail.")
