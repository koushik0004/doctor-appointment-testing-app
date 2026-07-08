import os
from json import loads
from types import SimpleNamespace

import pytest

from app.llm import (
    ClaudeProviderAdapter,
    ClaudeTransport,
    LLMConfigurationLoader,
    LLMConfigurationSettings,
    LLMGenerationBudget,
    LLMGenerationBudgetReasoningEffort,
    LLMGenerationRequest,
    LLMGenerationResponse,
    LLMGenerationProfileName,
    LLMMessage,
    LLMMessageRole,
    LLMProviderName,
    LLMRuntimeCompositionRoot,
    LLMToolChoice,
    LLMToolChoiceMode,
    LLMToolDefinition,
    ProductionLLMProviderTransportFactory,
)
from app.llm.transport import LLMTransportError
from app.llm.runtime_trace import AIRuntimeTraceRegistry, AIRuntimeTraceSession
from app.services.prompt_builder import PromptBuilderService


class FakeRawResponse:
    def __init__(self, message, *, request_id="req-1", status_code=200) -> None:
        self._message = message
        self.headers = {"request-id": request_id}
        self.status_code = status_code

    def parse(self):
        return self._message


class FakeMessagesAPI:
    def __init__(self, response) -> None:
        self.with_raw_response = self
        self._response = response
        self.calls: list[dict[str, object]] = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        if isinstance(self._response, Exception):
            raise self._response
        return self._response


class FakeAnthropicClient:
    def __init__(self, response) -> None:
        self.messages = FakeMessagesAPI(response)


class FakeAPIStatusError(Exception):
    def __init__(self, message: str, *, status_code: int, request_id: str | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.request_id = request_id


class AuthenticationError(FakeAPIStatusError):
    pass


class RateLimitError(FakeAPIStatusError):
    pass


class APITimeoutError(Exception):
    pass


def _claude_config():
    config = LLMConfigurationLoader().load(
        LLMConfigurationSettings(
            claude={
                "enabled": True,
                "default_model_name": "claude-sonnet-4-5",
                "api_key": "claude-key",
                "feature_flags": {
                    "tool_calls": True,
                    "reasoning": True,
                    "citations": True,
                },
            }
        )
    ).get_provider(LLMProviderName.CLAUDE)
    assert config is not None
    return config


def test_claude_transport_invokes_anthropic_client_and_normalizes_response():
    message = SimpleNamespace(
        id="msg-1",
        model="claude-sonnet-4-5",
        role="assistant",
        type="message",
        stop_reason="end_turn",
        usage=SimpleNamespace(input_tokens=120, output_tokens=40),
        content=[
            SimpleNamespace(
                type="text",
                text="Clinic policy summary.",
                citations=[
                    SimpleNamespace(
                        title="Clinic Policy",
                        url="https://example.com/policy",
                        cited_text="Bring your ID.",
                    )
                ],
            ),
            SimpleNamespace(
                type="thinking",
                thinking="Reviewed the policy knowledge first.",
            ),
            SimpleNamespace(
                type="tool_use",
                id="tool-1",
                name="lookup_policy",
                input={"policy_id": 7},
            ),
        ],
    )
    transport = ClaudeTransport(
        _claude_config(),
        client=FakeAnthropicClient(FakeRawResponse(message, request_id="anthropic-req-1")),
    )

    payload = transport.invoke(
        {
            "model": "claude-sonnet-4-5",
            "system": "Follow clinic policy.",
            "messages": [{"role": "user", "content": "Summarize the policy."}],
            "max_tokens": 256,
            "thinking": {"effort": "medium", "include_summary": True},
            "tools": [
                {
                    "name": "lookup_policy",
                    "description": "Look up a clinic policy.",
                    "input_schema": {"type": "object"},
                }
            ],
            "tool_choice": {"mode": "required"},
            "adapter_metadata": {
                "metadata": {"request_id": "control-1"},
            },
        }
    )

    assert payload["content"] == "Clinic policy summary."
    assert payload["stop_reason"] == "end_turn"
    assert payload["model"] == "claude-sonnet-4-5"
    assert payload["usage"]["input_tokens"] == 120
    assert payload["usage"]["output_tokens"] == 40
    assert payload["provider_metadata"]["request_id"] == "anthropic-req-1"
    assert payload["provider_metadata"]["response_id"] == "msg-1"
    assert payload["tool_calls"][0]["tool_name"] == "lookup_policy"
    assert payload["thinking_summary"] == "Reviewed the policy knowledge first."
    assert payload["metadata"]["citations"][0]["label"] == "Clinic Policy"


def test_claude_transport_uses_generation_budget_when_max_tokens_missing():
    client = FakeAnthropicClient(
        FakeRawResponse(
            SimpleNamespace(
                id="msg-2",
                model="claude-sonnet-4-5",
                role="assistant",
                type="message",
                stop_reason="end_turn",
                usage=SimpleNamespace(input_tokens=10, output_tokens=5),
                content=[SimpleNamespace(type="text", text="ok", citations=None)],
            )
        )
    )
    transport = ClaudeTransport(_claude_config(), client=client)

    transport.invoke(
        {
            "model": "claude-sonnet-4-5",
            "messages": [{"role": "user", "content": "Hello"}],
            "generation_budget": {
                "max_tokens": 333,
                "thinking": {"effort": "low"},
            },
        }
    )

    assert client.messages.calls[0]["max_tokens"] == 333
    assert client.messages.calls[0]["thinking"]["effort"] == "low"


def test_claude_transport_updates_runtime_trace(caplog):
    message = SimpleNamespace(
        id="msg-trace",
        model="claude-sonnet-4-5",
        role="assistant",
        type="message",
        stop_reason="end_turn",
        usage=SimpleNamespace(input_tokens=22, output_tokens=11),
        content=[SimpleNamespace(type="text", text="ok", citations=None)],
    )
    trace = AIRuntimeTraceSession(enabled=True, request_id="req-trace", conversation_id="conv-trace")
    AIRuntimeTraceRegistry.register(trace)
    transport = ClaudeTransport(
        _claude_config(),
        client=FakeAnthropicClient(FakeRawResponse(message, request_id="anthropic-trace")),
    )

    with caplog.at_level("INFO"):
        transport.invoke(
            {
                "model": "claude-sonnet-4-5",
                "messages": [{"role": "user", "content": "Hello"}],
                "adapter_metadata": {"ai_runtime_trace_id": trace.trace_id},
            }
        )
        trace.emit()
    AIRuntimeTraceRegistry.unregister(trace.trace_id)

    trace_record = next(
        record for record in caplog.records if record.message.startswith("ai_runtime_trace ")
    )
    payload = loads(trace_record.message.removeprefix("ai_runtime_trace "))
    assert payload["provider_transport"]["transport_selected"] == "ClaudeTransport"
    assert payload["provider_transport"]["http_response_received"] is True
    assert payload["provider_transport"]["token_usage"]["input_tokens"] == 22


def test_claude_transport_maps_sdk_status_errors():
    transport = ClaudeTransport(
        _claude_config(),
        client=FakeAnthropicClient(
            AuthenticationError(
                "bad key",
                status_code=401,
                request_id="anthropic-auth-1",
            )
        ),
    )

    with pytest.raises(LLMTransportError) as exc_info:
        transport.invoke(
            {
                "model": "claude-sonnet-4-5",
                "messages": [{"role": "user", "content": "Hello"}],
            }
        )

    assert exc_info.value.error_code == "authentication_error"
    assert exc_info.value.status_code == 401
    assert exc_info.value.request_id == "anthropic-auth-1"


def test_claude_transport_maps_timeout_errors():
    transport = ClaudeTransport(
        _claude_config(),
        client=FakeAnthropicClient(APITimeoutError("timed out")),
    )

    with pytest.raises(LLMTransportError) as exc_info:
        transport.invoke(
            {
                "model": "claude-sonnet-4-5",
                "messages": [{"role": "user", "content": "Hello"}],
            }
        )

    assert exc_info.value.error_code == "timeout"
    assert exc_info.value.retryable is True


def test_claude_transport_activation_snapshot_reports_missing_sdk():
    transport = ClaudeTransport(
        _claude_config(),
        sdk_loader=lambda: (_ for _ in ()).throw(RuntimeError("sdk missing")),
    )

    snapshot = transport.get_activation_snapshot()

    assert snapshot.available is False
    assert snapshot.transport_name == "ClaudeTransport"
    assert snapshot.diagnostics[0]["code"] == "transport_sdk_unavailable"


def test_production_transport_factory_creates_only_enabled_claude_provider():
    configuration = LLMConfigurationLoader().load(
        LLMConfigurationSettings(
            claude={
                "enabled": True,
                "default_model_name": "claude-sonnet-4-5",
                "api_key": "claude-key",
            },
            openai={
                "enabled": True,
                "default_model_name": "gpt-4.1-mini",
                "api_key": "openai-key",
            },
        )
    )

    transports = ProductionLLMProviderTransportFactory().create_transports(configuration)

    assert list(transports.keys()) == ["claude"]
    assert isinstance(transports["claude"], ClaudeTransport)


def test_claude_adapter_can_translate_transport_payload_into_canonical_response():
    adapter = ClaudeProviderAdapter(_claude_config())

    response: LLMGenerationResponse = adapter.translate_response(
        {
            "content": "Answer.",
            "stop_reason": "end_turn",
            "model": "claude-sonnet-4-5",
            "usage": {"input_tokens": 14, "output_tokens": 6},
            "thinking_summary": "Checked the clinic notes.",
            "tool_calls": [
                {
                    "tool_use_id": "tool-7",
                    "tool_name": "lookup_policy",
                    "arguments": {"policy_id": 7},
                }
            ],
            "provider_metadata": {"request_id": "anthropic-req-7", "response_id": "msg-7"},
            "metadata": {
                "citations": [
                    {
                        "label": "Clinic Policy",
                        "url": "https://example.com/policy",
                        "excerpt": "Bring your ID.",
                    }
                ]
            },
        },
        request=LLMGenerationRequest(
            messages=[LLMMessage(role=LLMMessageRole.USER, content="Need help")],
        ),
    )

    assert response.message.content == "Answer."
    assert response.usage is not None
    assert response.usage.total_tokens == 20
    assert response.citations[0].label == "Clinic Policy"
    assert response.provider_metadata["response_id"] == "msg-7"


def test_composition_root_uses_production_transport_factory_by_default_for_claude():
    root = LLMRuntimeCompositionRoot(
        prompt_builder=PromptBuilderService(),
        configuration_settings=LLMConfigurationSettings(
            provider=LLMProviderName.CLAUDE,
            enabled=True,
            allow_generation=True,
            claude={
                "enabled": True,
                "default_model_name": "claude-sonnet-4-5",
                "api_key": "claude-key",
            },
        ),
    )

    composition = root.compose()

    assert "claude" in composition.transports


@pytest.mark.integration
def test_claude_transport_optional_live_integration():
    if os.environ.get("CI"):
        pytest.skip("Live Claude integration test is skipped in CI.")

    api_key = os.environ.get("CLAUDE_API_KEY") or os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        pytest.skip("Set CLAUDE_API_KEY or ANTHROPIC_API_KEY to run the live Claude transport test.")

    config = LLMConfigurationLoader().load(
        LLMConfigurationSettings(
            claude={
                "enabled": True,
                "default_model_name": "claude-sonnet-4-5",
                "api_key": api_key,
            }
        )
    ).get_provider(LLMProviderName.CLAUDE)
    assert config is not None

    transport = ClaudeTransport(config)
    adapter = ClaudeProviderAdapter(config, transport=transport)
    response = adapter.generate(
        LLMGenerationRequest(
            messages=[LLMMessage(role=LLMMessageRole.USER, content="Reply with the word OK.")],
            tools=[
                LLMToolDefinition(
                    name="noop",
                    description="No-op tool",
                    input_schema={"type": "object"},
                )
            ],
            tool_choice=LLMToolChoice(mode=LLMToolChoiceMode.NONE),
            generation_budget=LLMGenerationBudget(
                profile=LLMGenerationProfileName.FAST,
                reasoning_effort=LLMGenerationBudgetReasoningEffort.LOW,
                max_output_tokens=32,
            ),
        )
    )

    assert response.message.content.strip()
