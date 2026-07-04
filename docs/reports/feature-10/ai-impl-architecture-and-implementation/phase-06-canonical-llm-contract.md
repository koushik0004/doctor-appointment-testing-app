# Phase 6.3 Canonical LLM Request/Response Contract

## Summary

Phase 6.3 refines the inactive `backend/app/llm/` canonical request/response contract so it can serve as the long-term provider-neutral interface for future LLM adapters.

This phase remains architectural only:

- no provider SDK
- no concrete OpenAI, Claude, Gemini, OpenRouter, Bedrock, Vertex, Ollama, or other provider adapter
- no runtime wiring into chat orchestration
- no API, frontend, database, workflow, retrieval, or Prompt Builder changes

## What Changed

### 1. Canonical request refinement

`backend/app/llm/models.py` now allows canonical requests to express future provider-neutral intent for:

- explicit `model_name` selection
- requested modalities
- structured-output requirements
- tool definitions and tool-choice policy
- reasoning preferences
- streaming preferences

All of these remain optional so existing callers that only send `messages` continue to work unchanged.

### 2. Canonical response refinement

Canonical responses can now carry future provider-neutral result metadata for:

- structured-output results
- tool-call metadata
- reasoning summaries
- streaming metadata
- citations
- separated provider metadata
- separated model metadata

These fields remain optional and do not require any provider integration in this phase.

### 3. Message and capability refinement

`LLMMessage` now supports canonical tool-call linkage through `tool_call_id` and optional canonical `tool_calls`.

`LLMProviderCapabilities` now advertises additional optional future capabilities for:

- reasoning
- citations
- audio input
- audio output

### 4. Focused validation

Added focused tests in `backend/tests/test_llm_models.py` covering:

- canonical model validation
- backward-compatible defaults
- deterministic serialization
- optional field handling
- provider-neutral future extensibility

Existing LLM seam tests remain unchanged in purpose and continue to validate the inactive registry and adapter boundaries.

## Boundary Confirmation

This phase does not modify:

- `backend/app/services/conversation_manager.py`
- `backend/app/services/workflow_engine.py`
- `backend/app/services/prompt_builder.py`
- `backend/app/knowledge/*`
- FastAPI routes or schemas
- frontend chat code
- database models or persistence

## Outcome

The codebase now has a stronger canonical internal LLM contract that is still simple, inactive, backward compatible, and provider-neutral while being ready for future structured output, tool calling, streaming, reasoning, citation, and multimodal metadata work.
