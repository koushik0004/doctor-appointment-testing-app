from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Any, Mapping

from pydantic import BaseModel, ConfigDict, Field, SecretStr, ValidationError

from app.llm.config import (
    LLMConfiguration,
    LLMProviderConfiguration,
    LLMProviderName,
    LLMRuntimeFeatureFlags,
)
from app.llm.providers import ConfigurableLLMProviderAdapter, LLMProviderTransport

if TYPE_CHECKING:
    from app.llm.composition import LLMRuntimeComposition, LLMRuntimeCompositionRoot


class LLMActivationSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class LLMActivationDiagnostic(BaseModel):
    code: str = Field(min_length=1)
    message: str = Field(min_length=1)
    severity: LLMActivationSeverity = LLMActivationSeverity.ERROR
    provider_name: str | None = None
    blocking: bool = True
    metadata: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(str_strip_whitespace=True)


class LLMProviderActivationStatus(BaseModel):
    provider_name: str
    selected: bool = False
    provider_enabled: bool = False
    adapter_available: bool = False
    transport_available: bool = False
    authentication_configured: bool = False
    generation_budget_resolved: bool = False
    healthy: bool = False
    generation_allowed: bool = False
    generation_available: bool = False
    streaming_allowed: bool = False
    tool_calling_allowed: bool = False
    reasoning_allowed: bool = False
    diagnostics: list[LLMActivationDiagnostic] = Field(default_factory=list)

    model_config = ConfigDict(str_strip_whitespace=True)


class LLMRuntimeActivationStatus(BaseModel):
    llm_enabled: bool = False
    shadow_mode: bool = False
    configuration_loaded: bool = False
    configuration_valid: bool = False
    selected_provider_name: str | None = None
    selected_provider_enabled: bool = False
    selected_provider_healthy: bool = False
    provider_readiness: bool = False
    generation_allowed: bool = False
    generation_available: bool = False
    streaming_allowed: bool = False
    tool_calling_allowed: bool = False
    reasoning_allowed: bool = False
    failure_safe: bool = True
    status_reason: str = Field(
        default="LLM runtime activation is inactive and deterministic chat remains primary."
    )
    providers: list[LLMProviderActivationStatus] = Field(default_factory=list)
    diagnostics: list[LLMActivationDiagnostic] = Field(default_factory=list)

    model_config = ConfigDict(str_strip_whitespace=True)


@dataclass(frozen=True)
class LLMRuntimeActivationResult:
    status: LLMRuntimeActivationStatus
    composition: LLMRuntimeComposition | None = None


class LLMRuntimeActivationEvaluator:
    """Deterministic provider-neutral runtime activation policy."""

    def evaluate(
        self,
        *,
        configuration: LLMConfiguration,
        adapters: Mapping[str, ConfigurableLLMProviderAdapter],
        transports: Mapping[str, LLMProviderTransport],
    ) -> LLMRuntimeActivationStatus:
        runtime_flags = configuration.runtime_flags
        selected_provider_name = self._resolve_selected_provider_name(configuration)
        providers = [
            self._evaluate_provider(
                provider_configuration=provider_configuration,
                runtime_flags=runtime_flags,
                selected_provider_name=selected_provider_name,
                adapter=adapters.get(provider_configuration.provider_name.value),
                transport=transports.get(provider_configuration.provider_name.value),
            )
            for provider_configuration in configuration.providers
        ]

        diagnostics: list[LLMActivationDiagnostic] = []
        if not runtime_flags.enabled:
            diagnostics.append(
                LLMActivationDiagnostic(
                    code="llm_disabled",
                    message="LLM runtime activation is disabled by the LLM_ENABLED flag.",
                    severity=LLMActivationSeverity.INFO,
                    blocking=True,
                )
            )

        if not runtime_flags.allow_generation:
            diagnostics.append(
                LLMActivationDiagnostic(
                    code="generation_disallowed",
                    message="LLM generation is blocked by the LLM_ALLOW_GENERATION flag.",
                    severity=LLMActivationSeverity.INFO,
                    blocking=True,
                )
            )

        if selected_provider_name is None:
            diagnostics.append(
                LLMActivationDiagnostic(
                    code="selected_provider_missing",
                    message="No selected provider is configured for runtime activation.",
                    severity=LLMActivationSeverity.WARNING,
                    blocking=True,
                )
            )

        selected_provider_status = next(
            (provider for provider in providers if provider.selected),
            None,
        )
        if selected_provider_name is not None and selected_provider_status is None:
            diagnostics.append(
                LLMActivationDiagnostic(
                    code="selected_provider_unconfigured",
                    message=(
                        f"Selected provider '{selected_provider_name}' is not available in the "
                        "resolved configuration."
                    ),
                    severity=LLMActivationSeverity.ERROR,
                    blocking=True,
                    provider_name=selected_provider_name,
                )
            )

        diagnostics.extend(
            diagnostic
            for provider in providers
            for diagnostic in provider.diagnostics
            if provider.selected
        )

        selected_provider_enabled = (
            selected_provider_status.provider_enabled
            if selected_provider_status is not None
            else False
        )
        selected_provider_healthy = (
            selected_provider_status.healthy if selected_provider_status is not None else False
        )
        generation_allowed = (
            runtime_flags.enabled
            and runtime_flags.allow_generation
            and selected_provider_enabled
        )
        generation_available = (
            generation_allowed
            and selected_provider_status is not None
            and selected_provider_status.generation_available
        )

        return LLMRuntimeActivationStatus(
            llm_enabled=runtime_flags.enabled,
            shadow_mode=runtime_flags.shadow_mode,
            configuration_loaded=True,
            configuration_valid=True,
            selected_provider_name=selected_provider_name,
            selected_provider_enabled=selected_provider_enabled,
            selected_provider_healthy=selected_provider_healthy,
            provider_readiness=selected_provider_healthy,
            generation_allowed=generation_allowed,
            generation_available=generation_available,
            streaming_allowed=bool(
                selected_provider_status and selected_provider_status.streaming_allowed
            ),
            tool_calling_allowed=bool(
                selected_provider_status and selected_provider_status.tool_calling_allowed
            ),
            reasoning_allowed=bool(
                selected_provider_status and selected_provider_status.reasoning_allowed
            ),
            status_reason=self._build_status_reason(
                runtime_flags=runtime_flags,
                selected_provider_name=selected_provider_name,
                selected_provider_status=selected_provider_status,
                generation_available=generation_available,
            ),
            providers=providers,
            diagnostics=diagnostics,
        )

    def _evaluate_provider(
        self,
        *,
        provider_configuration: LLMProviderConfiguration,
        runtime_flags: LLMRuntimeFeatureFlags,
        selected_provider_name: str | None,
        adapter: ConfigurableLLMProviderAdapter | None,
        transport: LLMProviderTransport | None,
    ) -> LLMProviderActivationStatus:
        provider_name = provider_configuration.provider_name.value
        diagnostics: list[LLMActivationDiagnostic] = []
        provider_enabled = provider_configuration.enabled
        adapter_available = adapter is not None
        transport_available = transport is not None
        authentication_configured = self._is_authentication_configured(
            provider_configuration
        )
        generation_budget_resolved = self._can_resolve_generation_budget(
            provider_configuration,
            diagnostics=diagnostics,
        )

        if not provider_enabled:
            diagnostics.append(
                LLMActivationDiagnostic(
                    code="provider_disabled",
                    message=(
                        f"Provider '{provider_name}' is disabled by its "
                        "LLM_<PROVIDER>__ENABLED flag."
                    ),
                    severity=LLMActivationSeverity.INFO,
                    blocking=True,
                    provider_name=provider_name,
                )
            )

        if not adapter_available:
            diagnostics.append(
                LLMActivationDiagnostic(
                    code="adapter_unavailable",
                    message=f"Provider '{provider_name}' has no composed adapter.",
                    severity=LLMActivationSeverity.WARNING,
                    blocking=True,
                    provider_name=provider_name,
                )
            )

        if not transport_available:
            diagnostics.append(
                LLMActivationDiagnostic(
                    code="transport_unavailable",
                    message=f"Provider '{provider_name}' has no configured transport.",
                    severity=LLMActivationSeverity.WARNING,
                    blocking=True,
                    provider_name=provider_name,
                )
            )

        if not authentication_configured:
            diagnostics.append(
                LLMActivationDiagnostic(
                    code="authentication_missing",
                    message=(
                        f"Provider '{provider_name}' is missing required authentication "
                        "configuration."
                    ),
                    severity=LLMActivationSeverity.ERROR,
                    blocking=True,
                    provider_name=provider_name,
                )
            )

        healthy = all(
            [
                provider_enabled,
                adapter_available,
                transport_available,
                authentication_configured,
                generation_budget_resolved,
            ]
        )
        generation_allowed = runtime_flags.enabled and runtime_flags.allow_generation
        generation_available = generation_allowed and healthy

        feature_flags = provider_configuration.feature_flags
        return LLMProviderActivationStatus(
            provider_name=provider_name,
            selected=provider_name == selected_provider_name,
            provider_enabled=provider_enabled,
            adapter_available=adapter_available,
            transport_available=transport_available,
            authentication_configured=authentication_configured,
            generation_budget_resolved=generation_budget_resolved,
            healthy=healthy,
            generation_allowed=generation_allowed,
            generation_available=generation_available,
            streaming_allowed=(
                generation_available
                and runtime_flags.allow_streaming
                and feature_flags.streaming
            ),
            tool_calling_allowed=(
                generation_available
                and runtime_flags.allow_tool_calling
                and feature_flags.tool_calls
            ),
            reasoning_allowed=(
                generation_available
                and runtime_flags.allow_reasoning
                and feature_flags.reasoning
            ),
            diagnostics=diagnostics,
        )

    def _can_resolve_generation_budget(
        self,
        provider_configuration: LLMProviderConfiguration,
        *,
        diagnostics: list[LLMActivationDiagnostic],
    ) -> bool:
        try:
            provider_configuration.generation_budget_profiles.resolve_budget()
        except ValueError as exc:
            diagnostics.append(
                LLMActivationDiagnostic(
                    code="generation_budget_unresolved",
                    message=(
                        f"Provider '{provider_configuration.provider_name.value}' has an "
                        f"invalid generation budget configuration: {exc}"
                    ),
                    severity=LLMActivationSeverity.ERROR,
                    blocking=True,
                    provider_name=provider_configuration.provider_name.value,
                )
            )
            return False
        return True

    def _is_authentication_configured(
        self,
        provider_configuration: LLMProviderConfiguration,
    ) -> bool:
        if provider_configuration.provider_name is LLMProviderName.OLLAMA:
            return bool(provider_configuration.base_url)
        return self._has_secret(provider_configuration.api_key)

    def _has_secret(self, secret: SecretStr | None) -> bool:
        if secret is None:
            return False
        return bool(secret.get_secret_value().strip())

    def _resolve_selected_provider_name(
        self,
        configuration: LLMConfiguration,
    ) -> str | None:
        if configuration.selected_provider_name is None:
            return None
        return configuration.selected_provider_name.value

    def _build_status_reason(
        self,
        *,
        runtime_flags: LLMRuntimeFeatureFlags,
        selected_provider_name: str | None,
        selected_provider_status: LLMProviderActivationStatus | None,
        generation_available: bool,
    ) -> str:
        if not runtime_flags.enabled:
            return "LLM runtime activation is disabled by the LLM_ENABLED flag."
        if selected_provider_name is None:
            return "LLM runtime activation is inactive because no selected provider is configured."
        if selected_provider_status is None:
            return (
                f"LLM runtime activation is inactive because selected provider "
                f"'{selected_provider_name}' is not configured."
            )
        if not selected_provider_status.provider_enabled:
            return (
                f"LLM runtime activation is inactive because selected provider "
                f"'{selected_provider_name}' is disabled."
            )
        if not runtime_flags.allow_generation:
            return "LLM runtime activation is loaded, but generation is disabled by policy."
        if not selected_provider_status.healthy:
            return (
                f"LLM runtime activation is inactive because selected provider "
                f"'{selected_provider_name}' is not ready."
            )
        if generation_available:
            if runtime_flags.shadow_mode:
                return (
                    f"LLM runtime activation is ready for provider '{selected_provider_name}' "
                    "in shadow mode."
                )
            return (
                f"LLM runtime activation is ready for provider "
                f"'{selected_provider_name}'."
            )
        return "LLM runtime activation is inactive and deterministic chat remains primary."


class LLMRuntimeActivationService:
    """Safe wrapper that evaluates activation without allowing startup failures to escape."""

    def __init__(
        self,
        *,
        composition_root: LLMRuntimeCompositionRoot,
        evaluator: LLMRuntimeActivationEvaluator | None = None,
    ) -> None:
        self._composition_root = composition_root
        self._evaluator = (
            evaluator if evaluator is not None else LLMRuntimeActivationEvaluator()
        )
        self._result: LLMRuntimeActivationResult | None = None

    def evaluate(self) -> LLMRuntimeActivationResult:
        if self._result is not None:
            return self._result

        try:
            composition = self._composition_root.compose()
        except (ValidationError, ValueError) as exc:
            self._result = LLMRuntimeActivationResult(
                status=LLMRuntimeActivationStatus(
                    configuration_loaded=False,
                    configuration_valid=False,
                    status_reason=(
                        "LLM runtime activation is inactive because configuration is invalid."
                    ),
                    diagnostics=[
                        LLMActivationDiagnostic(
                            code="configuration_invalid",
                            message=str(exc),
                            severity=LLMActivationSeverity.ERROR,
                            blocking=True,
                        )
                    ],
                ),
            )
            return self._result
        except Exception as exc:  # pragma: no cover - defensive safe-startup guard
            self._result = LLMRuntimeActivationResult(
                status=LLMRuntimeActivationStatus(
                    configuration_loaded=False,
                    configuration_valid=False,
                    status_reason=(
                        "LLM runtime activation failed safely during dependency assembly."
                    ),
                    diagnostics=[
                        LLMActivationDiagnostic(
                            code="activation_assembly_failed",
                            message=str(exc),
                            severity=LLMActivationSeverity.ERROR,
                            blocking=True,
                        )
                    ],
                ),
            )
            return self._result

        self._result = LLMRuntimeActivationResult(
            status=composition.activation_status,
            composition=composition,
        )
        return self._result
