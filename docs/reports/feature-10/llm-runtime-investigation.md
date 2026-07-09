# LLM Runtime Investigation

Date: 2026-07-07

Update: Later on 2026-07-07, the Claude production transport gap identified by this investigation was implemented in `backend/app/llm/transport.py` and wired into the default composition path through `ProductionLLMProviderTransportFactory`. This report remains the pre-implementation baseline.

## Executive Summary

At the time of this investigation, the application was **not capable of making a real LLM API call in production as checked in**.

That conclusion is backed by implementation, not assumption:

- The only production `LLMRuntimeCompositionRoot` is created in `backend/app/services/chat_service.py` without a transport factory override, so it uses `InactiveLLMProviderTransportFactory` by default.
- `InactiveLLMProviderTransportFactory.create_transports()` returns `{}`, so no real provider transport is composed.
- Every concrete provider adapter requires an explicit injected transport and raises an inactive-runtime error when no transport exists.
- No real HTTP transport implementation exists anywhere in `backend/` or `frontend/`.
- No OpenAI SDK, Anthropic SDK, Gemini SDK, OpenRouter SDK, Ollama client, `requests`, `aiohttp`, or backend `httpx` runtime client is wired to provider execution.
- Backend startup initializes only the database and API router. It does not initialize provider clients, transports, or the LLM runtime.
- The production chat path calls `ConversationManager.handle()`, which may trigger shadow mode through `LLMRuntimeFacade.run_shadow_mode()`, but that still bottoms out at the transport boundary and cannot reach an external provider with the checked-in composition.

The repository contains a substantial provider-neutral architecture seam:

- configuration
- activation
- execution policy
- prompt building
- orchestration
- validation
- eligibility
- composition
- composition/post-processing

But the seam is still incomplete at the network boundary. The exact execution stop point is:

`ConversationManager` -> `LLMRuntimeFacade` -> `LLMGenerationOrchestrator` -> `LLMIntegrationService` -> `Provider Adapter` -> `invoke_provider()` -> **fails because `_transport is None`**

## Current Runtime Status

Status: **architecturally advanced but operationally inactive**

What is implemented:

- provider-neutral configuration loading
- provider-neutral adapter classes
- provider-neutral activation evaluation
- runtime execution policy
- prompt builder and prompt renderer
- generation orchestrator
- runtime response validation
- runtime response eligibility
- response composition and post-processing
- shadow-mode and controlled-generation facade entry points

What is missing for real execution:

- real transport classes
- real transport factory
- real HTTP request wiring
- startup/runtime composition that injects real transports in production
- production entry point that invokes controlled generation for visible chat

## Architecture Diagram

```text
Browser
  |
  v
Next.js frontend proxy
  |
  v
FastAPI /api/chat
  |
  v
create_chat_response()
  |
  v
ConversationManager.handle()
  |
  +--> WorkflowEngine.handle() ------------------------------+
  |                                                         |
  +--> Knowledge retrieval / deterministic fallback         |
  |                                                         |
  +--> _run_shadow_mode()                                   |
        |
        v
      LLMRuntimeFacade.run_shadow_mode()
        |
        v
      AIExecutionPolicyService.evaluate()
        |
        v
      LLMGenerationOrchestrator.generate()
        |
        +--> PromptBuilderService.build()
        |
        +--> LLMIntegrationService.generate()
               |
               v
             Provider adapter generate()
               |
               v
             invoke_provider()
               |
               v
             transport.invoke(...)
               |
               X
             No production transport exists
```

## Execution Flow

### 1. Browser to backend

Frontend requests do not call Claude or any other provider directly.

- `frontend/app/api/[...path]/route.ts` proxies browser requests to `BACKEND_API_BASE_URL` by building `/api/...` backend URLs and calling `fetch(backendUrl, init)`.
- `backend/app/api/router.py` exposes `/api/chat` and `/api/v1/chat`.
- `backend/app/api/chat.py` calls `create_chat_response(session, request)`.

Conclusion:

- Browser -> Frontend proxy -> Backend is the implemented path.
- Browser -> Claude direct is **not** implemented anywhere in the checked-in app.

### 2. Backend chat runtime

`create_chat_response()` constructs the runtime objects:

- deterministic responder
- knowledge retrieval service
- `LLMRuntimeFacade(composition_root=LLMRuntimeCompositionRoot(prompt_builder=PromptBuilderService()))`

That is the critical production composition point. No transport factory is passed there.

`ConversationManager.handle()`:

- runs workflow first
- falls back to knowledge or deterministic response
- always returns the official app response from those existing paths
- then calls `_run_shadow_mode(...)`

`_run_shadow_mode(...)` invokes:

- `self._llm_runtime_facade.run_shadow_mode(...)`

So production currently uses LLM runtime only as:

- best-effort hidden shadow execution
- never as the primary visible response path

### 3. Shadow execution path

`LLMRuntimeFacade.run_shadow_mode()`:

- evaluates shadow policy
- if allowed, schedules `_execute_shadow_mode()`

`_execute_shadow_mode()`:

- builds an `LLMGenerationOrchestrationRequest`
- calls `composition.orchestrator.generate(orchestration_request)`

`LLMGenerationOrchestrator.generate()`:

- builds prompt via `PromptBuilderService`
- builds canonical `LLMGenerationRequest`
- calls `LLMIntegrationService.generate()`

`LLMIntegrationService.generate()`:

- resolves provider
- loads provider from registry
- calls `provider.generate(request)`

`BaseLLMProviderAdapter.generate()`:

- translates canonical request
- calls `invoke_provider(provider_request)`
- translates provider response back

`ConfigurableLLMProviderAdapter.invoke_provider()`:

- raises runtime error if `self._transport is None`

That is the current hard stop in production.

## Dependency Graph

### Production dependency graph

```text
frontend/app/api/[...path]/route.ts
  -> backend/app/api/chat.py
  -> backend/app/services/chat_service.py:create_chat_response
  -> backend/app/services/conversation_manager.py:ConversationManager
  -> backend/app/services/workflow_engine.py:WorkflowEngine
  -> backend/app/llm/facade.py:LLMRuntimeFacade
  -> backend/app/llm/composition.py:LLMRuntimeCompositionRoot
  -> backend/app/services/prompt_builder.py:PromptBuilderService
  -> backend/app/llm/orchestrator.py:LLMGenerationOrchestrator
  -> backend/app/llm/service.py:LLMIntegrationService
  -> backend/app/llm/registry.py:InMemoryLLMProviderRegistry
  -> backend/app/llm/providers.py:*ProviderAdapter
  -> backend/app/llm/providers.py:LLMProviderTransport
  -> external provider
```

### Exact current stop point

Execution currently stops at:

- `backend/app/llm/providers.py`
- `ConfigurableLLMProviderAdapter.invoke_provider()`
- because `_transport` is `None`

Reason:

- the production composition root defaults to `InactiveLLMProviderTransportFactory`
- that factory returns no transports
- adapters are composed without a transport

## Activation Flow

`LLM_ENABLED`, `LLM_PROVIDER`, and `LLM_ALLOW_GENERATION` are real configuration inputs, but in the checked-in application they are **activation metadata**, not a complete real-runtime activation path.

What they do:

- `backend/app/llm/config.py` loads env into `LLMConfigurationSettings`
- `LLMConfigurationLoader.load()` maps settings into `LLMConfiguration`
- `LLMRuntimeCompositionRoot.compose()` passes configuration, adapters, and transports into `LLMRuntimeActivationEvaluator.evaluate()`
- `LLMRuntimeActivationEvaluator` computes `generation_allowed` and `generation_available`

What they do not do by themselves:

- create real transports
- instantiate provider SDK clients
- create HTTP sessions
- override the inactive production transport factory

Therefore:

- `LLM_ENABLED=true` alone does not make real execution possible
- `LLM_PROVIDER=claude` alone does not make real execution possible
- `LLM_ALLOW_GENERATION=true` alone does not make real execution possible

They only become execution-enabling if a real transport factory is also composed.

## Transport Analysis

### Implementations found

Found transport seam:

- `backend/app/llm/providers.py`
  - `class LLMProviderTransport(Protocol)`
  - method: `invoke(self, request) -> ProviderPayload`

Found transport factory seam:

- `backend/app/llm/composition.py`
  - `class LLMProviderTransportFactory(Protocol)`
  - method: `create_transports(configuration) -> Mapping[str, LLMProviderTransport]`

Found default factory:

- `backend/app/llm/composition.py`
  - `class InactiveLLMProviderTransportFactory`
  - `create_transports(...)` returns `{}`

### Real transport implementations

Real checked-in transport implementations in application code:

- none

There are only test doubles such as:

- `RecordingTransport`
- `StaticTransport`
- `FailingTransport`

These exist only under `backend/tests/` and are not production runtime code.

### Is `InactiveLLMProviderTransportFactory` still being used?

Yes.

In production, it is the default.

Evidence:

- `LLMRuntimeCompositionRoot.__init__()` assigns `InactiveLLMProviderTransportFactory()` when `transport_factory` is not provided.
- `backend/app/services/chat_service.py` creates `LLMRuntimeCompositionRoot(prompt_builder=PromptBuilderService())` with no transport factory override.

Conditions under which it is used:

- every checked-in production chat request path
- every normal backend startup
- every production shadow-mode execution

Conditions under which it is not used:

- selected tests that explicitly inject a custom `StaticTransportFactory`

### Can a real HTTP request ever be made?

In checked-in production code: **no evidence of any real provider HTTP request path exists**.

Search findings:

- no `requests.post(...)`
- no backend `httpx.Client` / `httpx.AsyncClient` usage for providers
- no `aiohttp` provider client
- no Anthropic/OpenAI/Google/Ollama/OpenRouter SDK imports in application runtime code
- no provider endpoint strings such as `https://api.anthropic.com/v1/messages`

Important nuance:

- `httpx` exists only as a dev dependency in `backend/pyproject.toml`.
- That does not create a provider runtime by itself.
- The app uses browser/server `fetch` for frontend-to-backend proxying, not backend-to-provider execution.

## Provider Analysis

### Summary table

| Provider | Adapter exists | Transport seam exists | Real transport impl exists | Request mapping | Response mapping | Production ready |
|---|---|---:|---:|---:|---:|---:|
| OpenAI | Yes | Yes | No | Yes | Yes | No |
| Claude | Yes | Yes | No | Yes | Yes | No |
| Gemini | Yes | Yes | No | Yes | Yes | No |
| OpenRouter | Yes | Yes | No | Yes | Yes | No |
| Ollama | Yes | Yes | No | Yes | Yes | No |

### OpenAI

Adapter:

- `OpenAIProviderAdapter`
- inherits `OpenAICompatibleProviderAdapter`

Request translation:

- maps model, messages, system prompt, max tokens, temperature, top_p, stop, structured output, tools, tool choice, reasoning, generation budget

Response translation:

- maps content, finish reason, model, usage, structured output, tool calls, reasoning summary, metadata

Transport status:

- no real OpenAI transport class exists
- no OpenAI SDK import exists

Production readiness:

- not production ready
- missing network transport and runtime wiring

### Claude

Adapter:

- `ClaudeProviderAdapter`

Request translation:

- maps model, messages, system, `max_tokens`, temperature, top_p, `stop_sequences`, output schema, tools, tool choice, thinking, generation budget

Response translation:

- maps content, `stop_reason`, usage, tool calls, thinking summary, metadata

Transport status:

- no Anthropic transport class exists
- no Anthropic SDK import exists
- no `https://api.anthropic.com/v1/messages` call site exists

Production readiness:

- not production ready
- missing real Claude transport and startup/runtime wiring

### Gemini

Adapter:

- `GeminiProviderAdapter`

Request translation:

- maps `contents`, `system_instruction`, `generation_config`, response schema, tools, tool config, thinking config, generation budget

Response translation:

- maps usage metadata, text/content, finish reason, tool calls, thinking summary, metadata

Transport status:

- no real Gemini transport exists
- no Google AI SDK import exists

Production readiness:

- not production ready

### OpenRouter

Adapter:

- `OpenRouterProviderAdapter`
- inherits `OpenAICompatibleProviderAdapter`

Request translation:

- same base mapping as OpenAI-compatible adapter
- OpenRouter-specific generation-budget translation

Transport status:

- no OpenRouter transport exists
- no OpenRouter SDK/client exists

Production readiness:

- not production ready

### Ollama

Adapter:

- `OllamaProviderAdapter`

Request translation:

- maps model, messages, system, stop, `options`, tools, structured output format, generation-budget overrides into options

Response translation:

- maps message content, `done_reason`, usage counters, metadata

Transport status:

- no real Ollama transport exists
- no HTTP client or Ollama runtime client exists

Production readiness:

- not production ready

## Startup Analysis

Backend startup is minimal.

`backend/app/main.py`:

- creates FastAPI app
- sets CORS
- includes API router
- in lifespan only calls `init_db()`

What startup does **not** do:

- compose `LLMRuntimeCompositionRoot`
- preload `LLMRuntimeFacade`
- initialize provider registry globally
- initialize transports
- initialize provider SDK clients
- create an activation snapshot at startup time

The first likely runtime composition happens lazily when chat code reaches the cached `_llm_runtime_facade()` function in `backend/app/services/chat_service.py`.

That composition still uses the inactive default transport factory.

## Generation Budget Analysis

### Do `.env` values reach provider configuration?

Yes.

Evidence:

- `LLMConfigurationSettings` includes global and provider-specific generation budget settings.
- `LLMConfigurationLoader._build_provider_config()` builds each provider configuration with `generation_budget_profiles=...`.
- `_build_generation_budget_profile_catalog()` merges global and provider overrides into the provider configuration.

### Do budget values reach adapters?

Yes, but only if a request carries `generation_budget`.

Evidence:

- `LLMGenerationOrchestrator.build_llm_request()` copies request fields into `LLMGenerationRequest`.
- Each adapter reads `request.generation_budget` through `_translate_budget()` and maps it into provider-specific payload fields.

Examples:

- OpenAI -> `max_completion_tokens`, `context_window_tokens`, `reasoning_effort`
- Claude -> `max_tokens`, `context_management.max_input_tokens`, `thinking.effort`
- Gemini -> `generation_config.max_output_tokens`, `thinking_config.effort`
- OpenRouter -> `max_tokens`, routing/quality/cost hints
- Ollama -> `options.num_predict`, `options.num_ctx`

### Do configured default budget profiles automatically become outbound provider request fields in production?

Not by current checked-in production flow.

Reason:

- configuration stores the budget profile catalog
- activation checks that a budget can be resolved
- but `LLMGenerationOrchestrator.build_llm_request()` does not automatically resolve a default provider profile into `request.generation_budget`
- provider adapters only translate a budget if `request.generation_budget` is already present

So the current state is:

- `.env` budget values do reach provider configuration objects
- those values can be used by callers/tests that explicitly supply `generation_budget`
- they do **not** automatically flow from env -> provider config -> live provider request in the current production chat path

## Runtime Activation Analysis

Activation is real as a status computation, not as a complete transport/runtime bootstrap.

### What activation currently proves

If all of these are true:

- `LLM_ENABLED=true`
- `LLM_ALLOW_GENERATION=true`
- provider selected and enabled
- authentication configured
- adapter composed
- transport available
- budget resolved

then activation can compute:

- `selected_provider_healthy=True`
- `generation_available=True`

### What activation currently does not prove

It does not prove that production code is wired to:

- create real transports
- call a real provider
- return a visible provider-generated chat response

Why:

- activation consumes already-composed `adapters` and `transports`
- production composition currently builds zero transports

## Prompt Builder to Orchestrator Analysis

Does Prompt Builder currently reach the LLM orchestrator?

Yes, in the runtime seam.

Evidence:

- `LLMGenerationOrchestrator.generate()` calls `self._prompt_builder.build(...)`
- then calls `self._llm_integration_service.generate(...)`

Does workflow state reach the prompt?

Yes.

Evidence:

- `PromptContextWorkflowCollector` extracts workflow state from conversation state
- `PromptContextAssemblyPipeline` emits a `"Workflow State"` section when workflow data exists
- `PromptRenderer` renders labeled sections into final prompt text
- tests assert that generated prompt content contains `[Workflow State]`

Important scope note:

- this path is active only inside the LLM seam
- it is not the primary visible chat path in production

## Conversation Manager to LLM Runtime Analysis

Does `ConversationManager` currently invoke the LLM runtime?

Yes, but only for shadow mode.

Evidence:

- `ConversationManager.handle()` ends by calling `_run_shadow_mode(...)`
- `_run_shadow_mode(...)` calls `self._llm_runtime_facade.run_shadow_mode(...)`

Does `ConversationManager` currently invoke controlled generation for visible chat responses?

No.

There is no production call site for:

- `LLMRuntimeFacade.run_controlled_generation(...)`

Only tests call it.

Therefore current production behavior is:

- visible response = workflow / knowledge / deterministic
- LLM runtime = hidden, best-effort shadow branch only

## Browser Routing Analysis

Should browser requests ever reach Claude directly?

No, not in this application.

Implemented routing is:

`Browser -> Next.js proxy -> FastAPI backend`

There is no frontend provider SDK dependency and no frontend provider call site.

Evidence:

- frontend `package.json` contains no OpenAI, Anthropic, Google, OpenRouter, or Ollama SDKs
- `frontend/app/api/[...path]/route.ts` forwards requests only to backend `/api/...`

Correct current mental model:

- Browser -> Backend only
- Any future Claude/OpenAI/Gemini/OpenRouter/Ollama call would have to originate from the backend after real transport implementation is added

## Test Coverage Analysis

Current tests verify **mocked or synthetic execution**, not real provider execution.

Patterns used in tests:

- `StaticTransport`
- `RecordingTransport`
- `FailingTransport`
- `StaticTransportFactory`

What tests prove:

- composition can accept injected transports
- adapters can translate requests/responses
- facade behavior around shadow mode / controlled generation / fallback works
- activation status flips when a synthetic transport is present

What tests do not prove:

- real HTTP request dispatch
- real authentication headers
- real API endpoint compatibility
- real provider error handling
- streaming behavior with a live provider
- live SDK integration

Conclusion:

- current LLM tests are architecture tests and mocked execution tests
- they are not end-to-end provider execution tests

## How To Prove a Real Claude API Call

A developer cannot prove a real Claude API call with the current checked-in code, because there is no real Claude transport implementation to observe.

After adding a real Claude transport, proof should require multiple layers:

### 1. Backend logs

Add transport-level structured logs around:

- provider name
- model
- request id / correlation id
- endpoint URL
- HTTP status
- timing
- Anthropic request id response header if available

### 2. Breakpoints

Set breakpoints at:

- `ClaudeProviderAdapter.translate_request()`
- future `ClaudeTransport.invoke()`
- any HTTP client `post(...)` call

### 3. HTTP tracing

Use one of:

- `httpx` event hooks
- custom transport wrapper
- `mitmproxy`
- Charles Proxy
- Proxyman
- tcpdump/Wireshark if needed

### 4. Runtime diagnostics

Persist diagnostic fields such as:

- provider = `claude`
- endpoint = `https://api.anthropic.com/v1/messages`
- request id
- response id
- token usage
- model
- status code

### 5. Test strategy

Create an opt-in integration test that:

- requires real env credentials
- is skipped by default in CI
- exercises the actual Claude transport end to end
- asserts a non-mocked Anthropic response and request id

## Evidence

### Real transport creation

Evidence that no real production transport is created:

- `backend/app/llm/composition.py`
  - `InactiveLLMProviderTransportFactory.create_transports()` returns `{}`
  - `LLMRuntimeCompositionRoot.__init__()` uses that factory by default
- `backend/app/services/chat_service.py`
  - production `_llm_runtime_facade()` constructs `LLMRuntimeCompositionRoot` without passing `transport_factory`

### Adapter hard stop

Evidence that execution stops without a transport:

- `backend/app/llm/providers.py`
  - `ConfigurableLLMProviderAdapter.invoke_provider()` raises if `_transport is None`

### No startup initialization

Evidence that backend startup does not initialize LLM runtime:

- `backend/app/main.py`
  - lifespan only calls `init_db()`

### No visible controlled generation path

Evidence that visible production chat does not use `run_controlled_generation()`:

- search shows production call sites only for `run_shadow_mode()`
- `run_controlled_generation()` appears only in `backend/app/llm/facade.py` and tests

### Frontend does not call Claude directly

Evidence:

- `frontend/package.json` has no provider SDK dependency
- `frontend/app/api/[...path]/route.ts` proxies only to backend URLs

## Missing Components

### Critical

1. Real provider transport implementation(s)
   - Example: `ClaudeTransport`, `OpenAITransport`, `GeminiTransport`, `OpenRouterTransport`, `OllamaTransport`

2. Real production `LLMProviderTransportFactory`
   - Must create live transport instances from `LLMConfiguration`

3. Backend HTTP or SDK integration
   - `httpx` / provider SDK / equivalent
   - request auth, retries, timeout, base URL, headers

4. Production composition wiring
   - `backend/app/services/chat_service.py` or a startup/provider composition module must inject the real transport factory

5. End-to-end provider execution observability
   - logs, tracing, response ids, failure diagnostics

6. Real integration tests
   - opt-in, credential-based, non-mocked

### Important

1. Explicit transport classes per provider instead of only generic test doubles
2. Provider-specific error normalization
3. Retry/backoff implementation at transport layer
4. Structured timeout handling
5. Real streaming support path
6. Secret-safe logging and redaction
7. Live budget-resolution path from config defaults into actual request generation

### Optional

1. Startup-time warm validation of selected provider configuration
2. Health endpoint for provider readiness snapshot
3. Connection pooling/session reuse
4. Circuit breaker / outage shielding
5. Provider capability handshake / model catalog sync

## Production Readiness

Current production readiness for real LLM execution: **Not ready**

Readiness by layer:

- Prompt Builder: largely ready as deterministic infrastructure
- Orchestrator: structurally ready
- Configuration: structurally ready
- Activation: structurally ready
- Provider adapters: structurally ready
- Validation/eligibility/composer/post-processor: structurally ready
- Real network transport: not implemented
- Startup/runtime wiring: not implemented
- End-to-end provider observability: not implemented
- Visible controlled-generation production integration: not implemented

## Recommended Next Implementation Order

1. Implement one real provider transport end to end, preferably Claude if that is the target runtime.
2. Add a real `LLMProviderTransportFactory` that builds that provider transport from `LLMConfiguration`.
3. Wire the real transport factory into the production `LLMRuntimeCompositionRoot` creation path.
4. Add transport-level logging, tracing, and request-id capture.
5. Add one opt-in real integration test against the chosen provider.
6. Decide whether visible chat should remain shadow-only or begin using `run_controlled_generation()`.
7. If visible generation is enabled, add production call sites from `ConversationManager` or the appropriate orchestration boundary.
8. Resolve env budget profiles into default runtime request budgets if that behavior is desired.
9. Repeat provider transport implementation for the remaining providers only after one provider is proven end to end.

## Final Conclusion

The repository contains a serious provider-neutral LLM runtime architecture, but it is still missing the only component that can actually cross the network boundary: a real provider transport and its production wiring.

As of 2026-07-07, the checked-in application can:

- build prompts
- compose provider adapters
- evaluate activation
- simulate provider execution in tests
- run hidden shadow-mode orchestration until the transport boundary

It cannot:

- create a real Claude/OpenAI/Gemini/OpenRouter/Ollama production transport
- send a real provider HTTP request
- prove that a live provider call occurred

So the correct answer to the central question is:

**No, the current application is not capable of making real LLM API calls in its checked-in production implementation.**
