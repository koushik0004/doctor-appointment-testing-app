from __future__ import annotations

from enum import Enum
from typing import Any, Protocol, TypeVar

from pydantic import BaseModel, ConfigDict, Field, model_validator


class LLMGenerationProfileName(str, Enum):
    FAST = "fast"
    BALANCED = "balanced"
    WORKFLOW = "workflow"
    QUALITY = "quality"
    MAXIMUM = "maximum"


class LLMGenerationBudgetReasoningEffort(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class LLMGenerationBudgetLatencyPreference(str, Enum):
    LOW = "low"
    BALANCED = "balanced"
    RELAXED = "relaxed"


class LLMGenerationBudgetQualityPreference(str, Enum):
    STANDARD = "standard"
    HIGH = "high"
    MAXIMUM = "maximum"


class LLMGenerationBudgetCostPreference(str, Enum):
    MINIMIZE = "minimize"
    BALANCED = "balanced"
    FLEXIBLE = "flexible"


class LLMGenerationBudget(BaseModel):
    profile: LLMGenerationProfileName | None = None
    reasoning_effort: LLMGenerationBudgetReasoningEffort | None = None
    max_output_tokens: int | None = Field(default=None, gt=0)
    max_context_tokens: int | None = Field(default=None, gt=0)
    latency_preference: LLMGenerationBudgetLatencyPreference | None = None
    quality_preference: LLMGenerationBudgetQualityPreference | None = None
    cost_preference: LLMGenerationBudgetCostPreference | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(str_strip_whitespace=True, frozen=True)

    @model_validator(mode="after")
    def validate_token_budget_relationship(self) -> LLMGenerationBudget:
        if (
            self.max_output_tokens is not None
            and self.max_context_tokens is not None
            and self.max_context_tokens < self.max_output_tokens
        ):
            raise ValueError(
                "max_context_tokens must be greater than or equal to max_output_tokens."
            )

        return self


class LLMGenerationBudgetOverrides(BaseModel):
    reasoning_effort: LLMGenerationBudgetReasoningEffort | None = None
    max_output_tokens: int | None = Field(default=None, gt=0)
    max_context_tokens: int | None = Field(default=None, gt=0)
    latency_preference: LLMGenerationBudgetLatencyPreference | None = None
    quality_preference: LLMGenerationBudgetQualityPreference | None = None
    cost_preference: LLMGenerationBudgetCostPreference | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(str_strip_whitespace=True, frozen=True)

    def apply_to(
        self,
        budget: LLMGenerationBudget,
        *,
        profile: LLMGenerationProfileName | None = None,
    ) -> LLMGenerationBudget:
        merged_metadata = budget.metadata | self.metadata
        return LLMGenerationBudget(
            profile=profile if profile is not None else budget.profile,
            reasoning_effort=(
                self.reasoning_effort
                if self.reasoning_effort is not None
                else budget.reasoning_effort
            ),
            max_output_tokens=(
                self.max_output_tokens
                if self.max_output_tokens is not None
                else budget.max_output_tokens
            ),
            max_context_tokens=(
                self.max_context_tokens
                if self.max_context_tokens is not None
                else budget.max_context_tokens
            ),
            latency_preference=(
                self.latency_preference
                if self.latency_preference is not None
                else budget.latency_preference
            ),
            quality_preference=(
                self.quality_preference
                if self.quality_preference is not None
                else budget.quality_preference
            ),
            cost_preference=(
                self.cost_preference
                if self.cost_preference is not None
                else budget.cost_preference
            ),
            metadata=merged_metadata,
        )


class LLMGenerationBudgetProfile(BaseModel):
    name: LLMGenerationProfileName
    budget: LLMGenerationBudget
    description: str | None = None

    model_config = ConfigDict(str_strip_whitespace=True, frozen=True)


class LLMGenerationBudgetProfileCatalog(BaseModel):
    default_profile: LLMGenerationProfileName = LLMGenerationProfileName.BALANCED
    profiles: list[LLMGenerationBudgetProfile] = Field(default_factory=list)

    model_config = ConfigDict(frozen=True)

    @model_validator(mode="after")
    def validate_profiles(self) -> LLMGenerationBudgetProfileCatalog:
        seen: set[LLMGenerationProfileName] = set()
        for profile in self.profiles:
            if profile.name in seen:
                raise ValueError(
                    f"Duplicate generation budget profile '{profile.name.value}'."
                )
            seen.add(profile.name)

        if self.get_profile(self.default_profile) is None:
            raise ValueError(
                f"Default generation budget profile '{self.default_profile.value}' is not configured."
            )

        return self

    def get_profile(
        self,
        profile_name: LLMGenerationProfileName | str,
    ) -> LLMGenerationBudgetProfile | None:
        profile_value = (
            profile_name.value
            if isinstance(profile_name, LLMGenerationProfileName)
            else profile_name
        )
        for profile in self.profiles:
            if profile.name.value == profile_value:
                return profile
        return None

    def resolve_budget(
        self,
        *,
        profile_name: LLMGenerationProfileName | None = None,
        overrides: LLMGenerationBudgetOverrides | None = None,
    ) -> LLMGenerationBudget:
        selected_name = profile_name or self.default_profile
        selected_profile = self.get_profile(selected_name)
        if selected_profile is None:
            raise ValueError(
                f"Generation budget profile '{selected_name.value}' is not configured."
            )

        base_budget = selected_profile.budget.model_copy(deep=True)
        if overrides is None:
            return base_budget

        return overrides.apply_to(base_budget, profile=selected_profile.name)


BudgetTranslationT = TypeVar("BudgetTranslationT")


class LLMGenerationBudgetTranslator(Protocol[BudgetTranslationT]):
    """Translates canonical generation budgets into provider-private payloads."""

    def translate_generation_budget(
        self,
        budget: LLMGenerationBudget,
    ) -> BudgetTranslationT:
        ...


def build_default_generation_budget_profile_catalog() -> (
    LLMGenerationBudgetProfileCatalog
):
    return LLMGenerationBudgetProfileCatalog(
        default_profile=LLMGenerationProfileName.BALANCED,
        profiles=[
            LLMGenerationBudgetProfile(
                name=LLMGenerationProfileName.FAST,
                description="Low-latency responses with constrained reasoning and output budgets.",
                budget=LLMGenerationBudget(
                    profile=LLMGenerationProfileName.FAST,
                    reasoning_effort=LLMGenerationBudgetReasoningEffort.LOW,
                    max_output_tokens=512,
                    max_context_tokens=16_000,
                    latency_preference=LLMGenerationBudgetLatencyPreference.LOW,
                    quality_preference=LLMGenerationBudgetQualityPreference.STANDARD,
                    cost_preference=LLMGenerationBudgetCostPreference.MINIMIZE,
                ),
            ),
            LLMGenerationBudgetProfile(
                name=LLMGenerationProfileName.BALANCED,
                description="General-purpose default balancing quality, latency, and cost.",
                budget=LLMGenerationBudget(
                    profile=LLMGenerationProfileName.BALANCED,
                    reasoning_effort=LLMGenerationBudgetReasoningEffort.MEDIUM,
                    max_output_tokens=1_024,
                    max_context_tokens=24_000,
                    latency_preference=LLMGenerationBudgetLatencyPreference.BALANCED,
                    quality_preference=LLMGenerationBudgetQualityPreference.HIGH,
                    cost_preference=LLMGenerationBudgetCostPreference.BALANCED,
                ),
            ),
            LLMGenerationBudgetProfile(
                name=LLMGenerationProfileName.WORKFLOW,
                description="Workflow-safe profile favoring consistency for structured task turns.",
                budget=LLMGenerationBudget(
                    profile=LLMGenerationProfileName.WORKFLOW,
                    reasoning_effort=LLMGenerationBudgetReasoningEffort.MEDIUM,
                    max_output_tokens=768,
                    max_context_tokens=20_000,
                    latency_preference=LLMGenerationBudgetLatencyPreference.BALANCED,
                    quality_preference=LLMGenerationBudgetQualityPreference.HIGH,
                    cost_preference=LLMGenerationBudgetCostPreference.BALANCED,
                ),
            ),
            LLMGenerationBudgetProfile(
                name=LLMGenerationProfileName.QUALITY,
                description="Higher-quality profile with larger token and reasoning budgets.",
                budget=LLMGenerationBudget(
                    profile=LLMGenerationProfileName.QUALITY,
                    reasoning_effort=LLMGenerationBudgetReasoningEffort.HIGH,
                    max_output_tokens=2_048,
                    max_context_tokens=32_000,
                    latency_preference=LLMGenerationBudgetLatencyPreference.RELAXED,
                    quality_preference=LLMGenerationBudgetQualityPreference.HIGH,
                    cost_preference=LLMGenerationBudgetCostPreference.FLEXIBLE,
                ),
            ),
            LLMGenerationBudgetProfile(
                name=LLMGenerationProfileName.MAXIMUM,
                description="Maximum canonical budget for future high-effort generation paths.",
                budget=LLMGenerationBudget(
                    profile=LLMGenerationProfileName.MAXIMUM,
                    reasoning_effort=LLMGenerationBudgetReasoningEffort.HIGH,
                    max_output_tokens=4_096,
                    max_context_tokens=64_000,
                    latency_preference=LLMGenerationBudgetLatencyPreference.RELAXED,
                    quality_preference=LLMGenerationBudgetQualityPreference.MAXIMUM,
                    cost_preference=LLMGenerationBudgetCostPreference.FLEXIBLE,
                ),
            ),
        ],
    )
