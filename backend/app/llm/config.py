from __future__ import annotations

from enum import Enum
from functools import lru_cache

from pydantic import BaseModel, ConfigDict, Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMProviderName(str, Enum):
    OPENAI = "openai"
    CLAUDE = "claude"
    GEMINI = "gemini"
    OPENROUTER = "openrouter"
    OLLAMA = "ollama"


class LLMProviderFeatureFlags(BaseModel):
    streaming: bool = False
    structured_output: bool = False
    tool_calls: bool = False
    reasoning: bool = False
    citations: bool = False


class LLMProviderEnvironmentSettings(BaseModel):
    enabled: bool = False
    default_model_name: str | None = None
    api_key: SecretStr | None = None
    base_url: str | None = None
    timeout_seconds: float | None = Field(default=None, gt=0)
    max_retries: int | None = Field(default=None, ge=0)
    retry_backoff_seconds: float | None = Field(default=None, ge=0)
    feature_flags: LLMProviderFeatureFlags = Field(
        default_factory=LLMProviderFeatureFlags
    )

    model_config = ConfigDict(str_strip_whitespace=True)


class LLMProviderConfiguration(BaseModel):
    provider_name: LLMProviderName
    enabled: bool = False
    default_model_name: str | None = None
    api_key: SecretStr | None = None
    base_url: str | None = None
    timeout_seconds: float = Field(default=30.0, gt=0)
    max_retries: int = Field(default=2, ge=0)
    retry_backoff_seconds: float = Field(default=0.5, ge=0)
    feature_flags: LLMProviderFeatureFlags = Field(
        default_factory=LLMProviderFeatureFlags
    )

    model_config = ConfigDict(str_strip_whitespace=True)

    @model_validator(mode="after")
    def validate_enabled_provider_requirements(self) -> LLMProviderConfiguration:
        if not self.enabled:
            return self

        if not self.default_model_name:
            raise ValueError(
                f"Provider '{self.provider_name.value}' requires a default_model_name when enabled."
            )

        if self.provider_name is not LLMProviderName.OLLAMA and self.api_key is None:
            raise ValueError(
                f"Provider '{self.provider_name.value}' requires an api_key when enabled."
            )

        return self


class LLMConfiguration(BaseModel):
    selected_provider_name: LLMProviderName | None = None
    providers: list[LLMProviderConfiguration] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_selected_provider(self) -> LLMConfiguration:
        if self.selected_provider_name is None:
            return self

        selected = self.get_provider(self.selected_provider_name)
        if selected is None:
            raise ValueError(
                f"Selected provider '{self.selected_provider_name.value}' is not configured."
            )

        if not selected.enabled:
            raise ValueError(
                f"Selected provider '{self.selected_provider_name.value}' is disabled."
            )

        return self

    def get_provider(
        self,
        provider_name: LLMProviderName | str,
    ) -> LLMProviderConfiguration | None:
        provider_value = (
            provider_name.value
            if isinstance(provider_name, LLMProviderName)
            else provider_name
        )
        for provider in self.providers:
            if provider.provider_name.value == provider_value:
                return provider
        return None

    def list_enabled_provider_names(self) -> list[str]:
        return [
            provider.provider_name.value
            for provider in self.providers
            if provider.enabled
        ]


class LLMConfigurationSettings(BaseSettings):
    provider: LLMProviderName | None = None
    timeout_seconds: float = Field(default=30.0, gt=0)
    max_retries: int = Field(default=2, ge=0)
    retry_backoff_seconds: float = Field(default=0.5, ge=0)
    openai: LLMProviderEnvironmentSettings = Field(
        default_factory=LLMProviderEnvironmentSettings
    )
    claude: LLMProviderEnvironmentSettings = Field(
        default_factory=LLMProviderEnvironmentSettings
    )
    gemini: LLMProviderEnvironmentSettings = Field(
        default_factory=LLMProviderEnvironmentSettings
    )
    openrouter: LLMProviderEnvironmentSettings = Field(
        default_factory=LLMProviderEnvironmentSettings
    )
    ollama: LLMProviderEnvironmentSettings = Field(
        default_factory=LLMProviderEnvironmentSettings
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        env_prefix="LLM_",
        env_nested_delimiter="__",
    )


class LLMConfigurationLoader:
    """Deterministic loader for the inactive provider-neutral LLM config seam."""

    def load(
        self,
        settings: LLMConfigurationSettings | None = None,
    ) -> LLMConfiguration:
        resolved_settings = (
            settings if settings is not None else LLMConfigurationSettings()
        )
        providers = [
            self._build_provider_config(
                provider_name=LLMProviderName.OPENAI,
                settings=resolved_settings.openai,
                global_timeout_seconds=resolved_settings.timeout_seconds,
                global_max_retries=resolved_settings.max_retries,
                global_retry_backoff_seconds=resolved_settings.retry_backoff_seconds,
            ),
            self._build_provider_config(
                provider_name=LLMProviderName.CLAUDE,
                settings=resolved_settings.claude,
                global_timeout_seconds=resolved_settings.timeout_seconds,
                global_max_retries=resolved_settings.max_retries,
                global_retry_backoff_seconds=resolved_settings.retry_backoff_seconds,
            ),
            self._build_provider_config(
                provider_name=LLMProviderName.GEMINI,
                settings=resolved_settings.gemini,
                global_timeout_seconds=resolved_settings.timeout_seconds,
                global_max_retries=resolved_settings.max_retries,
                global_retry_backoff_seconds=resolved_settings.retry_backoff_seconds,
            ),
            self._build_provider_config(
                provider_name=LLMProviderName.OPENROUTER,
                settings=resolved_settings.openrouter,
                global_timeout_seconds=resolved_settings.timeout_seconds,
                global_max_retries=resolved_settings.max_retries,
                global_retry_backoff_seconds=resolved_settings.retry_backoff_seconds,
            ),
            self._build_provider_config(
                provider_name=LLMProviderName.OLLAMA,
                settings=resolved_settings.ollama,
                global_timeout_seconds=resolved_settings.timeout_seconds,
                global_max_retries=resolved_settings.max_retries,
                global_retry_backoff_seconds=resolved_settings.retry_backoff_seconds,
            ),
        ]

        return LLMConfiguration(
            selected_provider_name=resolved_settings.provider,
            providers=providers,
        )

    def _build_provider_config(
        self,
        *,
        provider_name: LLMProviderName,
        settings: LLMProviderEnvironmentSettings,
        global_timeout_seconds: float,
        global_max_retries: int,
        global_retry_backoff_seconds: float,
    ) -> LLMProviderConfiguration:
        return LLMProviderConfiguration(
            provider_name=provider_name,
            enabled=settings.enabled,
            default_model_name=settings.default_model_name,
            api_key=settings.api_key,
            base_url=settings.base_url,
            timeout_seconds=(
                settings.timeout_seconds
                if settings.timeout_seconds is not None
                else global_timeout_seconds
            ),
            max_retries=(
                settings.max_retries
                if settings.max_retries is not None
                else global_max_retries
            ),
            retry_backoff_seconds=(
                settings.retry_backoff_seconds
                if settings.retry_backoff_seconds is not None
                else global_retry_backoff_seconds
            ),
            feature_flags=settings.feature_flags.model_copy(deep=True),
        )


@lru_cache(maxsize=1)
def get_llm_configuration() -> LLMConfiguration:
    return LLMConfigurationLoader().load()
