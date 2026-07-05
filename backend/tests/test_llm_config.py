from pydantic import ValidationError

from app.llm import (
    LLMConfigurationLoader,
    LLMConfigurationSettings,
    LLMProviderName,
)


def test_llm_configuration_loader_is_deterministic_for_equal_inputs():
    settings = LLMConfigurationSettings(
        provider=LLMProviderName.OPENAI,
        timeout_seconds=45,
        max_retries=4,
        retry_backoff_seconds=1.25,
        openai={
            "enabled": True,
            "default_model_name": "gpt-4.1-mini",
            "api_key": "openai-key",
            "feature_flags": {
                "streaming": True,
                "structured_output": True,
            },
        },
    )
    loader = LLMConfigurationLoader()

    config_a = loader.load(settings)
    config_b = loader.load(settings)

    assert config_a.model_dump(mode="json") == config_b.model_dump(mode="json")


def test_llm_configuration_loader_allows_missing_optional_keys_for_disabled_providers():
    config = LLMConfigurationLoader().load(LLMConfigurationSettings())

    assert config.selected_provider_name is None
    assert config.list_enabled_provider_names() == []
    assert config.get_provider(LLMProviderName.OPENAI) is not None
    assert config.get_provider(LLMProviderName.OPENAI).base_url is None


def test_llm_configuration_loader_rejects_missing_required_keys_for_enabled_provider():
    settings = LLMConfigurationSettings(
        openai={
            "enabled": True,
            "default_model_name": "gpt-4.1-mini",
        }
    )

    try:
        LLMConfigurationLoader().load(settings)
    except ValidationError as exc:
        assert "api_key" in str(exc)
    else:
        raise AssertionError("Expected enabled OpenAI configuration without api_key to fail.")


def test_llm_configuration_loader_rejects_missing_model_for_enabled_provider():
    settings = LLMConfigurationSettings(
        claude={
            "enabled": True,
            "api_key": "anthropic-key",
        }
    )

    try:
        LLMConfigurationLoader().load(settings)
    except ValidationError as exc:
        assert "default_model_name" in str(exc)
    else:
        raise AssertionError(
            "Expected enabled Claude configuration without default_model_name to fail."
        )


def test_llm_configuration_loader_rejects_selected_disabled_provider():
    settings = LLMConfigurationSettings(provider=LLMProviderName.GEMINI)

    try:
        LLMConfigurationLoader().load(settings)
    except ValidationError as exc:
        assert "disabled" in str(exc)
    else:
        raise AssertionError("Expected selected disabled provider to fail validation.")


def test_llm_configuration_loader_applies_global_defaults_and_provider_overrides():
    settings = LLMConfigurationSettings(
        timeout_seconds=60,
        max_retries=5,
        retry_backoff_seconds=2.0,
        openrouter={
            "enabled": True,
            "default_model_name": "openrouter/auto",
            "api_key": "openrouter-key",
            "timeout_seconds": 12,
            "feature_flags": {
                "tool_calls": True,
            },
        },
    )

    config = LLMConfigurationLoader().load(settings)
    openrouter = config.get_provider(LLMProviderName.OPENROUTER)
    openai = config.get_provider(LLMProviderName.OPENAI)

    assert openrouter is not None
    assert openrouter.timeout_seconds == 12
    assert openrouter.max_retries == 5
    assert openrouter.retry_backoff_seconds == 2.0
    assert openrouter.feature_flags.tool_calls is True
    assert openai is not None
    assert openai.timeout_seconds == 60
    assert openai.max_retries == 5
    assert openai.retry_backoff_seconds == 2.0


def test_llm_configuration_settings_maps_nested_environment_variables(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "ollama")
    monkeypatch.setenv("LLM_TIMEOUT_SECONDS", "75")
    monkeypatch.setenv("LLM_OLLAMA__ENABLED", "true")
    monkeypatch.setenv("LLM_OLLAMA__DEFAULT_MODEL_NAME", "llama3.1")
    monkeypatch.setenv("LLM_OLLAMA__BASE_URL", "http://localhost:11434")
    monkeypatch.setenv("LLM_OLLAMA__FEATURE_FLAGS__STREAMING", "true")

    settings = LLMConfigurationSettings()
    config = LLMConfigurationLoader().load(settings)
    ollama = config.get_provider(LLMProviderName.OLLAMA)

    assert config.selected_provider_name == LLMProviderName.OLLAMA
    assert ollama is not None
    assert ollama.enabled is True
    assert ollama.default_model_name == "llama3.1"
    assert ollama.base_url == "http://localhost:11434"
    assert ollama.timeout_seconds == 75
    assert ollama.feature_flags.streaming is True


def test_llm_configuration_loader_preserves_backward_compatible_inactive_defaults():
    config = LLMConfigurationLoader().load()

    assert config.selected_provider_name is None
    assert config.list_enabled_provider_names() == []
    assert [provider.provider_name.value for provider in config.providers] == [
        "openai",
        "claude",
        "gemini",
        "openrouter",
        "ollama",
    ]
