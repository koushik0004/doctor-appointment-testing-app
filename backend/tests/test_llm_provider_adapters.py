from app.llm import (
    ClaudeProviderAdapter,
    LLMConfiguration,
    LLMConfigurationLoader,
    LLMConfigurationSettings,
    LLMFinishReason,
    LLMGenerationBudget,
    LLMGenerationBudgetLatencyPreference,
    LLMGenerationBudgetQualityPreference,
    LLMGenerationBudgetReasoningEffort,
    LLMGenerationProfileName,
    LLMMessage,
    LLMMessageRole,
    LLMProviderAdapterFactory,
    LLMProviderName,
    OllamaProviderAdapter,
    OpenAIProviderAdapter,
)
from app.llm.models import (
    LLMGenerationConstraints,
    LLMGenerationRequest,
    LLMReasoningConfig,
    LLMReasoningEffort,
    LLMStructuredOutputMode,
    LLMStructuredOutputSchema,
    LLMToolChoice,
    LLMToolChoiceMode,
    LLMToolDefinition,
)


class RecordingTransport:
    def __init__(self, response: dict[str, object]) -> None:
        self.response = response
        self.calls: list[dict[str, object]] = []

    def invoke(self, request: dict[str, object]) -> dict[str, object]:
        self.calls.append(request)
        return dict(self.response)


def test_openai_adapter_translates_canonical_request_into_private_payload():
    config = LLMConfigurationLoader().load(
        LLMConfigurationSettings(
            openai={
                "enabled": True,
                "default_model_name": "gpt-4.1-mini",
                "api_key": "openai-key",
                "feature_flags": {
                    "structured_output": True,
                    "tool_calls": True,
                    "reasoning": True,
                },
            }
        )
    ).get_provider(LLMProviderName.OPENAI)
    assert config is not None

    adapter = OpenAIProviderAdapter(config)
    payload = adapter.translate_request(
        LLMGenerationRequest(
            system_prompt="Follow clinic policy.",
            messages=[LLMMessage(role=LLMMessageRole.USER, content="Summarize this.")],
            constraints=LLMGenerationConstraints(
                max_output_tokens=256,
                temperature=0.2,
                top_p=0.9,
                stop_sequences=["END"],
            ),
            structured_output=LLMStructuredOutputSchema(
                mode=LLMStructuredOutputMode.JSON_OBJECT,
                name="summary",
            ),
            tools=[
                LLMToolDefinition(
                    name="lookup_policy",
                    description="Look up clinic policy.",
                )
            ],
            tool_choice=LLMToolChoice(mode=LLMToolChoiceMode.REQUIRED),
            reasoning=LLMReasoningConfig(
                effort=LLMReasoningEffort.MEDIUM,
                include_summary=True,
            ),
            generation_budget=LLMGenerationBudget(
                profile=LLMGenerationProfileName.BALANCED,
                reasoning_effort=LLMGenerationBudgetReasoningEffort.MEDIUM,
                max_output_tokens=1024,
                max_context_tokens=24000,
                latency_preference=LLMGenerationBudgetLatencyPreference.BALANCED,
                quality_preference=LLMGenerationBudgetQualityPreference.HIGH,
            ),
        )
    )

    assert payload["model"] == "gpt-4.1-mini"
    assert payload["messages"][0]["role"] == "user"
    assert payload["max_completion_tokens"] == 256
    assert payload["response_format"]["mode"] == "json_object"
    assert payload["tools"][0]["name"] == "lookup_policy"
    assert payload["tool_choice"]["mode"] == "required"
    assert payload["reasoning"]["effort"] == "medium"
    assert payload["generation_budget"]["max_completion_tokens"] == 1024
    assert payload["generation_budget"]["latency_tier"] == "balanced"


def test_claude_adapter_translates_private_response_into_canonical_response():
    config = LLMConfigurationLoader().load(
        LLMConfigurationSettings(
            claude={
                "enabled": True,
                "default_model_name": "claude-sonnet",
                "api_key": "claude-key",
                "feature_flags": {
                    "tool_calls": True,
                    "reasoning": True,
                },
            }
        )
    ).get_provider(LLMProviderName.CLAUDE)
    assert config is not None

    adapter = ClaudeProviderAdapter(config)
    response = adapter.translate_response(
        {
            "content": "Here is the answer.",
            "stop_reason": "end_turn",
            "model": "claude-sonnet",
            "usage": {"input_tokens": 100, "output_tokens": 40},
            "tool_calls": [
                {
                    "tool_use_id": "tool-1",
                    "tool_name": "lookup_policy",
                    "arguments": {"policy_id": 1},
                }
            ],
            "thinking_summary": "Reviewed the policy notes first.",
            "provider_metadata": {"request_id": "claude-req-1"},
        },
        request=LLMGenerationRequest(
            messages=[LLMMessage(role=LLMMessageRole.USER, content="Need help")],
            reasoning=LLMReasoningConfig(effort=LLMReasoningEffort.HIGH),
        ),
    )

    assert response.finish_reason == LLMFinishReason.STOP
    assert response.message.content == "Here is the answer."
    assert response.model_name == "claude-sonnet"
    assert response.usage is not None
    assert response.usage.total_tokens == 140
    assert response.tool_calls[0].tool_name == "lookup_policy"
    assert response.reasoning is not None
    assert response.reasoning.effort == LLMReasoningEffort.HIGH
    assert response.provider_metadata["request_id"] == "claude-req-1"


def test_ollama_adapter_raises_when_no_explicit_transport_is_configured():
    config = LLMConfigurationLoader().load(
        LLMConfigurationSettings(
            ollama={
                "enabled": True,
                "default_model_name": "llama3.1",
                "base_url": "http://localhost:11434",
            }
        )
    ).get_provider(LLMProviderName.OLLAMA)
    assert config is not None

    adapter = OllamaProviderAdapter(config)

    try:
        adapter.generate(
            LLMGenerationRequest(
                messages=[LLMMessage(role=LLMMessageRole.USER, content="Hello")]
            )
        )
    except RuntimeError as exc:
        assert "inactive" in str(exc)
    else:
        raise AssertionError("Expected Ollama adapter without transport to remain inactive.")


def test_factory_builds_registry_from_enabled_provider_configurations():
    configuration = LLMConfigurationLoader().load(
        LLMConfigurationSettings(
            provider=LLMProviderName.OPENAI,
            openai={
                "enabled": True,
                "default_model_name": "gpt-4.1-mini",
                "api_key": "openai-key",
            },
            claude={
                "enabled": True,
                "default_model_name": "claude-sonnet",
                "api_key": "claude-key",
            },
        )
    )

    registry = LLMProviderAdapterFactory().create_registry(configuration)

    assert registry.get_default_provider_name() == "openai"
    assert [provider.provider_name for provider in registry.list_providers()] == [
        "openai",
        "claude",
    ]
    assert registry.get_provider("openai") is not None
    assert registry.get_provider("gemini") is None


def test_factory_generated_adapter_can_delegate_through_explicit_transport():
    configuration = LLMConfiguration(
        selected_provider_name=LLMProviderName.OPENAI,
        providers=[
            LLMConfigurationLoader().load(
                LLMConfigurationSettings(
                    openai={
                        "enabled": True,
                        "default_model_name": "gpt-4.1-mini",
                        "api_key": "openai-key",
                    }
                )
            ).get_provider(LLMProviderName.OPENAI)
        ],
    )
    provider_config = configuration.get_provider(LLMProviderName.OPENAI)
    assert provider_config is not None

    transport = RecordingTransport(
        {
            "content": "Echo: hello",
            "finish_reason": "stop",
            "model": "gpt-4.1-mini",
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 3,
                "total_tokens": 13,
            },
        }
    )
    adapter = LLMProviderAdapterFactory().create_adapter(
        provider_config,
        transport=transport,
    )

    response = adapter.generate(
        LLMGenerationRequest(
            messages=[LLMMessage(role=LLMMessageRole.USER, content="hello")]
        )
    )

    assert len(transport.calls) == 1
    assert transport.calls[0]["model"] == "gpt-4.1-mini"
    assert response.message.content == "Echo: hello"
    assert response.provider_name == "openai"
    assert response.usage is not None
    assert response.usage.total_tokens == 13
