# Phase 06 LLM Integration Architecture

## Summary

Phase 6.1 introduces a provider-neutral backend LLM Integration boundary as an inactive architectural seam only.

## What Changed

- Added a new backend package at `backend/app/llm/`.
- Defined provider-neutral message, request, response, constraints, capabilities, and provider-descriptor models.
- Defined protocol boundaries for future provider adapters and provider registries.
- Added an inactive `LLMIntegrationService` facade that reports disconnected status by default and only delegates generation when a registry is explicitly supplied.
- Added focused backend tests confirming the seam remains inert unless explicitly invoked with a stub registry.

## What Did Not Change

- No LLM SDK integration
- No provider-specific code
- No runtime wiring
- No `ConversationManager` changes
- No `WorkflowEngine` changes
- No Vector-less RAG changes
- No `PromptBuilderService` changes
- No API changes
- No database changes
- No frontend changes

## Intended Next Step

Future phases can add provider adapters behind the `LLMProvider` and `LLMProviderRegistry` contracts without reworking the current deterministic assistant architecture.
