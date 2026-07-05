from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from app.llm.activation import LLMRuntimeActivationStatus
from app.llm.composition import LLMRuntimeComposition, LLMRuntimeCompositionRoot
from app.llm.service import LLMIntegrationStatus


class LLMRuntimeFacadeSnapshot(BaseModel):
    """Deterministic save-ready view of the inactive LLM runtime boundary."""

    configuration_loaded: bool = True
    composition_cached: bool = True
    connected_provider_names: list[str] = Field(default_factory=list)
    default_provider_name: str | None = None
    selected_provider_name: str | None = None
    activation_status: LLMRuntimeActivationStatus
    integration_status: LLMIntegrationStatus
    prompt_builder_attached: bool = True
    orchestrator_attached: bool = True

    model_config = ConfigDict(str_strip_whitespace=True)


class LLMRuntimeFacade:
    """Inactive public runtime facade for the composed LLM subsystem."""

    def __init__(self, *, composition_root: LLMRuntimeCompositionRoot) -> None:
        self._composition_root = composition_root

    def compose(self) -> LLMRuntimeComposition:
        return self._composition_root.compose()

    def get_composition(self) -> LLMRuntimeComposition:
        return self.compose()

    def snapshot(self) -> LLMRuntimeFacadeSnapshot:
        composition = self.compose()
        integration_status = composition.llm_integration_service.get_status()
        return LLMRuntimeFacadeSnapshot(
            connected_provider_names=list(integration_status.connected_provider_names),
            default_provider_name=integration_status.default_provider_name,
            selected_provider_name=composition.activation_status.selected_provider_name,
            activation_status=composition.activation_status,
            integration_status=integration_status,
        )

    def save_integration_boundary(self) -> LLMRuntimeFacadeSnapshot:
        """Alias for callers that want an explicit boundary-capture verb."""

        return self.snapshot()
