# Phase 6.9 Runtime Execution Policy And Routing

## Summary

Phase 6.9 adds an inactive provider-neutral execution-policy seam under `backend/app/llm/execution_policy.py`.

The implementation introduces canonical execution modes, ownership decisions, fallback strategies, activation snapshots, and deterministic diagnostics so future runtime callers can decide between workflow, knowledge, deterministic, hybrid, LLM-only, and shadow paths without changing the live chat runtime.

The composition root now assembles the execution-policy seam alongside the existing activation, registry, integration-service, and orchestrator seams, but nothing is wired into `ConversationManager`, `WorkflowEngine`, Vector-less RAG retrieval, FastAPI chat routes, or the frontend widget.

## Added

- `backend/app/llm/execution_policy.py`
  - Adds canonical execution-policy contracts and a deterministic evaluator/service.
- `backend/tests/test_llm_execution_policy.py`
  - Covers workflow ownership, knowledge ownership, deterministic default routing, activation-aware shadow routing, fallback routing, serialization, and decision determinism.
- `docs/analysis/hybrid-ai-assistant-architecture/llm-execution-policy-architecture.md`
  - Defines the Phase 6.9 routing architecture and boundaries.

## Updated

- `backend/app/llm/composition.py`
  - The inactive composition root now assembles `AIExecutionPolicyEvaluator` and `AIExecutionPolicyService`.
- `backend/app/llm/__init__.py`
  - Re-exports the execution-policy seam.
- `backend/tests/test_llm_composition.py`
  - Verifies composed execution-policy availability.
- `docs/analysis/hybrid-ai-assistant-architecture/llm-runtime-activation-architecture.md`
  - Clarifies that Phase 6.9 consumes activation state but does not move routing into the activation seam.
- `docs/analysis/hybrid-ai-assistant-architecture/llm-runtime-composition-architecture.md`
  - Documents execution-policy assembly in the composed graph.
- `docs/analysis/hybrid-ai-assistant-architecture/llm-integration-architecture.md`
  - Extends the Phase 6 package reference with the execution-policy layer.

## Preserved Boundaries

Phase 6.9 does not:

- call provider SDKs
- execute workflows
- retrieve knowledge
- build prompts
- change deterministic routing
- change chat API behavior
- change frontend or database behavior

The deterministic chatbot remains the default production path, and workflow-first ownership remains unchanged.

## Verification

- `backend/.venv/bin/python -m pytest backend/tests/test_llm_execution_policy.py backend/tests/test_llm_activation.py backend/tests/test_llm_composition.py backend/tests/test_llm_config.py backend/tests/test_llm_integration.py backend/tests/test_llm_orchestrator.py backend/tests/test_llm_provider_adapters.py backend/tests/test_llm_budget.py backend/tests/test_llm_models.py -q`
  - `58 passed`
- `python -m compileall backend/app/llm`
  - completed successfully
