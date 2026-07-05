# LLM Runtime Activation Architecture

## Purpose

This document defines the Phase 6.8 runtime activation layer for the inactive LLM subsystem, extended in Phase 6.9 as the readiness source for execution-policy decisions.

The goal remains architectural only:

- decide whether the LLM subsystem is ready without changing chat routing
- keep deterministic chat as the default production path
- expose provider-neutral activation status and diagnostics
- fail safely when configuration or provider readiness is incomplete

## Activation Scope

`backend/app/llm/activation.py` introduces a standalone activation policy and safe evaluation wrapper.

It is responsible for:

- evaluating top-level runtime flags such as `LLM_ENABLED`, `LLM_SHADOW_MODE`, and `LLM_ALLOW_GENERATION`
- evaluating provider-scoped enablement through existing `LLM_<PROVIDER>__ENABLED` flags
- checking selected-provider readiness
- checking adapter availability
- checking transport availability
- checking authentication presence
- checking default generation-budget resolution
- reporting structured diagnostics instead of raising startup failures

It is not responsible for:

- prompt construction
- routing
- retrieval
- workflow execution
- provider invocation
- conversation-state mutation

Phase 6.9 keeps that boundary intact. The new execution-policy seam consumes activation status, but activation itself still does not make routing decisions.

## Canonical Models

The activation layer exposes:

- `LLMActivationDiagnostic`
- `LLMProviderActivationStatus`
- `LLMRuntimeActivationStatus`
- `LLMRuntimeActivationResult`

These models answer the Phase 6.8 readiness questions directly:

- whether the subsystem is enabled
- whether the selected provider is enabled
- whether the selected provider is healthy
- whether generation is allowed
- whether generation is actually available
- whether streaming, tool calling, and reasoning are permitted
- why activation is inactive when readiness is incomplete

## Evaluation Rules

Provider readiness is evaluated deterministically from composed dependencies and resolved configuration:

1. configuration loaded successfully
2. provider is enabled
3. adapter exists
4. transport exists
5. authentication is configured when required
6. default generation budget resolves successfully

The provider is considered healthy only when all provider-local checks pass.

Generation becomes available only when:

- `LLM_ENABLED=true`
- `LLM_ALLOW_GENERATION=true`
- the selected provider is enabled
- the selected provider is healthy

Streaming, tool calling, and reasoning require both:

- global allow flags
- provider capability flags from configuration

## Safe Failure Strategy

`LLMRuntimeActivationService` wraps the composition root and converts configuration or assembly failures into inactive status objects.

This preserves safe startup because failures:

- do not crash FastAPI startup
- do not affect deterministic chat
- do not affect booking workflows
- do not affect Vector-less RAG

The result is a structured inactive status plus diagnostics, not a live runtime change.
