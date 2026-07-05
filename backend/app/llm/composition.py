from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping, Protocol

from app.llm.activation import (
    LLMRuntimeActivationEvaluator,
    LLMRuntimeActivationStatus,
)
from app.llm.config import (
    LLMConfiguration,
    LLMConfigurationLoader,
    LLMConfigurationSettings,
)
from app.llm.execution_policy import (
    AIExecutionPolicyEvaluator,
    AIExecutionPolicyService,
)
from app.llm.operations import (
    LLMOperationalReadinessEvaluator,
    LLMOperationalReadinessService,
)
from app.llm.orchestrator import LLMGenerationOrchestrator
from app.llm.providers import (
    ConfigurableLLMProviderAdapter,
    LLMProviderAdapterFactory,
    LLMProviderTransport,
)
from app.llm.registry import InMemoryLLMProviderRegistry
from app.llm.service import LLMIntegrationService
from app.services.prompt_builder import PromptBuilderService


class LLMProviderTransportFactory(Protocol):
    """Builds provider transports separately from provider adapters."""

    def create_transports(
        self,
        configuration: LLMConfiguration,
    ) -> Mapping[str, LLMProviderTransport]:
        ...


class InactiveLLMProviderTransportFactory:
    """Default inactive transport factory that keeps the LLM seam disconnected."""

    def create_transports(
        self,
        configuration: LLMConfiguration,
    ) -> Mapping[str, LLMProviderTransport]:
        del configuration
        return {}


@dataclass(frozen=True)
class LLMRuntimeComposition:
    configuration: LLMConfiguration
    transports: Mapping[str, LLMProviderTransport]
    adapters: Mapping[str, ConfigurableLLMProviderAdapter]
    activation_status: LLMRuntimeActivationStatus
    execution_policy: AIExecutionPolicyEvaluator
    execution_policy_service: AIExecutionPolicyService
    operational_readiness: LLMOperationalReadinessEvaluator
    operational_readiness_service: LLMOperationalReadinessService
    provider_registry: InMemoryLLMProviderRegistry
    default_provider_name: str | None
    llm_integration_service: LLMIntegrationService
    prompt_builder: PromptBuilderService
    orchestrator: LLMGenerationOrchestrator


class LLMRuntimeCompositionRoot:
    """Single composition root for the inactive LLM dependency graph."""

    def __init__(
        self,
        *,
        prompt_builder: PromptBuilderService,
        configuration_loader: LLMConfigurationLoader | None = None,
        configuration_settings: LLMConfigurationSettings | None = None,
        transport_factory: LLMProviderTransportFactory | None = None,
        adapter_factory: LLMProviderAdapterFactory | None = None,
        activation_evaluator: LLMRuntimeActivationEvaluator | None = None,
        execution_policy: AIExecutionPolicyEvaluator | None = None,
        operational_readiness: LLMOperationalReadinessEvaluator | None = None,
    ) -> None:
        self._prompt_builder = prompt_builder
        self._configuration_loader = (
            configuration_loader
            if configuration_loader is not None
            else LLMConfigurationLoader()
        )
        self._configuration_settings = configuration_settings
        self._transport_factory = (
            transport_factory
            if transport_factory is not None
            else InactiveLLMProviderTransportFactory()
        )
        self._adapter_factory = (
            adapter_factory if adapter_factory is not None else LLMProviderAdapterFactory()
        )
        self._activation_evaluator = (
            activation_evaluator
            if activation_evaluator is not None
            else LLMRuntimeActivationEvaluator()
        )
        self._execution_policy = (
            execution_policy if execution_policy is not None else AIExecutionPolicyEvaluator()
        )
        self._operational_readiness = (
            operational_readiness
            if operational_readiness is not None
            else LLMOperationalReadinessEvaluator()
        )
        self._composition: LLMRuntimeComposition | None = None

    def compose(self) -> LLMRuntimeComposition:
        if self._composition is not None:
            return self._composition

        configuration = self._configuration_loader.load(self._configuration_settings)
        transports = self._build_transports(configuration)
        adapters = self._build_adapters(
            configuration=configuration,
            transports=transports,
        )
        activation_status = self._activation_evaluator.evaluate(
            configuration=configuration,
            adapters=adapters,
            transports=transports,
        )
        default_provider_name = self._resolve_default_provider_name(configuration)
        provider_registry = InMemoryLLMProviderRegistry(
            adapters.values(),
            default_provider_name=default_provider_name,
        )
        llm_integration_service = LLMIntegrationService(
            provider_registry=provider_registry,
            default_provider_name=default_provider_name,
        )
        orchestrator = LLMGenerationOrchestrator(
            prompt_builder=self._prompt_builder,
            llm_integration_service=llm_integration_service,
        )
        execution_policy_service = AIExecutionPolicyService(
            composition_root=self,
            evaluator=self._execution_policy,
        )
        operational_readiness_service = LLMOperationalReadinessService(
            composition_root=self,
            evaluator=self._operational_readiness,
        )

        self._composition = LLMRuntimeComposition(
            configuration=configuration,
            transports=MappingProxyType(dict(transports)),
            adapters=MappingProxyType(dict(adapters)),
            activation_status=activation_status,
            execution_policy=self._execution_policy,
            execution_policy_service=execution_policy_service,
            operational_readiness=self._operational_readiness,
            operational_readiness_service=operational_readiness_service,
            provider_registry=provider_registry,
            default_provider_name=default_provider_name,
            llm_integration_service=llm_integration_service,
            prompt_builder=self._prompt_builder,
            orchestrator=orchestrator,
        )
        return self._composition

    def _build_transports(
        self,
        configuration: LLMConfiguration,
    ) -> Mapping[str, LLMProviderTransport]:
        enabled_provider_names = set(configuration.list_enabled_provider_names())
        transports = dict(self._transport_factory.create_transports(configuration))
        return {
            provider_name: transport
            for provider_name, transport in transports.items()
            if provider_name in enabled_provider_names
        }

    def _build_adapters(
        self,
        *,
        configuration: LLMConfiguration,
        transports: Mapping[str, LLMProviderTransport],
    ) -> dict[str, ConfigurableLLMProviderAdapter]:
        adapters: dict[str, ConfigurableLLMProviderAdapter] = {}
        for provider_configuration in configuration.providers:
            if not provider_configuration.enabled:
                continue

            provider_name = provider_configuration.provider_name.value
            adapters[provider_name] = self._adapter_factory.create_adapter(
                provider_configuration,
                transport=transports.get(provider_name),
            )
        return adapters

    def _resolve_default_provider_name(
        self,
        configuration: LLMConfiguration,
    ) -> str | None:
        if configuration.selected_provider_name is None:
            return None
        return configuration.selected_provider_name.value
