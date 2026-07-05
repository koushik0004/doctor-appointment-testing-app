from pydantic import ValidationError

from app.llm import (
    LLMGenerationBudget,
    LLMGenerationBudgetCostPreference,
    LLMGenerationBudgetLatencyPreference,
    LLMGenerationBudgetOverrides,
    LLMGenerationBudgetProfileCatalog,
    LLMGenerationBudgetQualityPreference,
    LLMGenerationBudgetReasoningEffort,
    LLMGenerationProfileName,
    build_default_generation_budget_profile_catalog,
)


def test_generation_budget_rejects_context_budget_smaller_than_output_budget():
    try:
        LLMGenerationBudget(max_output_tokens=1000, max_context_tokens=999)
    except ValidationError as exc:
        assert "max_context_tokens" in str(exc)
    else:
        raise AssertionError(
            "Expected generation budget validation to reject smaller context budgets."
        )


def test_default_generation_budget_catalog_uses_balanced_profile():
    catalog = build_default_generation_budget_profile_catalog()
    budget = catalog.resolve_budget()

    assert catalog.default_profile == LLMGenerationProfileName.BALANCED
    assert budget.profile == LLMGenerationProfileName.BALANCED
    assert budget.reasoning_effort == LLMGenerationBudgetReasoningEffort.MEDIUM


def test_generation_budget_catalog_applies_profile_overrides_without_mutating_base():
    catalog = build_default_generation_budget_profile_catalog()
    base_budget = catalog.resolve_budget(profile_name=LLMGenerationProfileName.FAST)
    resolved_budget = catalog.resolve_budget(
        profile_name=LLMGenerationProfileName.FAST,
        overrides=LLMGenerationBudgetOverrides(
            max_output_tokens=640,
            quality_preference=LLMGenerationBudgetQualityPreference.HIGH,
            metadata={"scenario": "workflow-escalation"},
        ),
    )

    assert base_budget.max_output_tokens == 512
    assert resolved_budget.profile == LLMGenerationProfileName.FAST
    assert resolved_budget.max_output_tokens == 640
    assert (
        resolved_budget.quality_preference
        == LLMGenerationBudgetQualityPreference.HIGH
    )
    assert resolved_budget.metadata["scenario"] == "workflow-escalation"


def test_generation_budget_catalog_serialization_is_deterministic():
    catalog_a = build_default_generation_budget_profile_catalog()
    catalog_b = build_default_generation_budget_profile_catalog()

    assert catalog_a.model_dump(mode="json") == catalog_b.model_dump(mode="json")


def test_generation_budget_catalog_remains_provider_neutral():
    catalog = build_default_generation_budget_profile_catalog()
    dumped = catalog.model_dump(mode="json")
    serialized = str(dumped).lower()

    assert "openai" not in serialized
    assert "claude" not in serialized
    assert "gemini" not in serialized
    assert "openrouter" not in serialized
    assert "ollama" not in serialized


def test_generation_budget_catalog_rejects_missing_default_profile():
    profile = build_default_generation_budget_profile_catalog().get_profile(
        LLMGenerationProfileName.FAST
    )
    assert profile is not None

    try:
        LLMGenerationBudgetProfileCatalog(
            default_profile=LLMGenerationProfileName.MAXIMUM,
            profiles=[profile],
        )
    except ValidationError as exc:
        assert "default" in str(exc).lower()
    else:
        raise AssertionError("Expected missing default profile validation to fail.")


def test_generation_budget_preferences_cover_latency_quality_and_cost_controls():
    budget = LLMGenerationBudget(
        profile=LLMGenerationProfileName.QUALITY,
        reasoning_effort=LLMGenerationBudgetReasoningEffort.HIGH,
        max_output_tokens=2048,
        max_context_tokens=32000,
        latency_preference=LLMGenerationBudgetLatencyPreference.RELAXED,
        quality_preference=LLMGenerationBudgetQualityPreference.MAXIMUM,
        cost_preference=LLMGenerationBudgetCostPreference.FLEXIBLE,
    )

    dumped = budget.model_dump(mode="json")

    assert dumped["latency_preference"] == "relaxed"
    assert dumped["quality_preference"] == "maximum"
    assert dumped["cost_preference"] == "flexible"
